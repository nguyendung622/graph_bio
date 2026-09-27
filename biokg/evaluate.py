"""Stage 7: evaluation and consistency reports used in the paper.

  E1  record-level completeness vs. species counts reported by the authors
  E2  cell-level accuracy: per-site richness recomputed from extracted cells vs. printed totals rows
  E3  hierarchy reconciliation: genus/family/order counts vs. counts reported in the abstract
  E4  name resolution outcome distribution and source-name issues (misspelling, synonym, homonym)
  E5  glyph-loss repair of higher-taxon names
  E6  cross-source consistency (same taxon, different family / status / site coordinates)
"""
import json
from pathlib import Path

import pandas as pd

from .sources import SOURCES

OUT = Path(__file__).resolve().parent.parent / "extracted" / "gialai"


def run():
    rec = pd.read_csv(OUT / "checklist_records.csv")
    pres = pd.read_csv(OUT / "site_presence.csv")
    meta = pd.read_csv(OUT / "extraction_meta.csv").set_index("source")
    rep = {s["id"]: s for s in SOURCES}
    report = {}

    # E1 + E3
    rows = []
    for sid, g in rec.groupby("source", sort=False):
        r = rep[sid]["reported"]
        fam = g.src_family.dropna().str.lower().nunique()
        ordr = g.src_order.dropna().str.lower().nunique()
        rows.append(dict(source=sid, waterbody=rep[sid]["waterbody"], group=rep[sid]["group"],
                         species_reported=r["species"], records_extracted=len(g),
                         genus_reported=r.get("genus"), genus_extracted=g[~g.is_higher_taxon].genus.nunique(),
                         family_reported=r.get("family"), family_extracted=fam,
                         order_reported=r.get("order"), order_extracted=ordr,
                         glyph_fixes=int(meta.loc[sid, "glyph_fixes"])))
    e13 = pd.DataFrame(rows)
    e13.to_csv(OUT / "eval_E1_E3_counts.csv", index=False)
    report["E1_E3"] = e13

    # E2
    rows = []
    for sid, g in pres.groupby("source"):
        t = meta.loc[sid, "totals_row"]
        n = rep[sid]["reported"].get("sites")
        if not isinstance(t, str) or t == "null" or not n:
            continue
        t = json.loads(t)[:n]
        got = [int(g[(g.site == f"M{i}") & g.present].shape[0]) for i in range(1, n + 1)]
        rows.append(dict(source=sid, sites=n, cells=int(len(rec[rec.source == sid]) * n),
                         site_totals_matched=sum(a == b for a, b in zip(t, got)),
                         reported=t, recomputed=got))
    e2 = pd.DataFrame(rows)
    e2.to_csv(OUT / "eval_E2_cells.csv", index=False)
    report["E2"] = e2

    # E2b: conservation-status columns vs. per-column totals printed by the authors
    rows = []
    for sid, g in rec.groupby("source"):
        for key in ("status_footer", "status_abstract"):
            exp = rep[sid].get(key)
            if not exp:
                continue
            cnt = {}
            for st in g.status:
                for k, v in json.loads(st).items():
                    cnt[k] = cnt.get(k, 0) + 1
                    if k.startswith("IUCN") and v not in ("LC", "NE", "DD"):
                        cnt[k + "_nonLC"] = cnt.get(k + "_nonLC", 0) + 1
            for col, n in exp.items():
                rows.append(dict(source=sid, reference=key, column=col, reported=n, extracted=cnt.get(col, 0),
                                 match=n == cnt.get(col, 0)))
    for sid, g in rec.groupby("source"):
        legend, exp = rep[sid].get("symbol_legend"), rep[sid].get("symbol_abstract")
        if not (legend and exp):
            continue
        for sym, trait in legend.items():
            if trait in exp:
                n = int(g.symbols.fillna("").str.contains(sym, regex=False).sum())
                rows.append(dict(source=sid, reference="symbol_abstract", column=trait, reported=exp[trait],
                                 extracted=n, match=n == exp[trait]))
    e2b = pd.DataFrame(rows)
    e2b.to_csv(OUT / "eval_E2b_status_columns.csv", index=False)
    report["E2b"] = e2b

    # E4
    e4 = rec.groupby(["source", "gbif_match"]).size().unstack(fill_value=0)
    e4["resolved_2nd_pass"] = rec[rec.gbif_pass == 2].groupby("source").size()
    e4 = e4.fillna(0).astype(int)
    e4.to_csv(OUT / "eval_E4_resolution.csv")
    report["E4"] = e4
    issues = rec[rec.gbif_match.isin(["fuzzy", "synonym", "none", "higherrank"]) | (rec.gbif_pass == 2)][
        ["source", "raw_name", "canonical", "gbif_match", "gbif_pass", "gbif_name", "gbif_accepted", "gbif_family"]]
    issues.to_csv(OUT / "eval_E4_name_issues.csv", index=False)

    # E5
    e5 = pd.read_csv(OUT / "hierarchy_repairs.csv")
    report["E5"] = e5

    # E6: family disagreements source vs GBIF, and cross-source status disagreements
    fam = rec[rec.family_agrees == False][["source", "canonical", "src_family", "gbif_family", "family_similarity",  # noqa: E712
                                            "gbif_match"]].copy()
    fam["kind"] = ["glyph_unrepaired" if " " in a else "rejected_fuzzy" if m == "fuzzy_rejected"
                   else "spelling_variant" if sim >= 0.8 and a[:5].lower() == b[:5].lower() else "classification"
                   for a, b, sim, m in zip(fam.src_family, fam.gbif_family, fam.family_similarity, fam.gbif_match)]
    fam.to_csv(OUT / "eval_E6_family_conflicts.csv", index=False)
    report["E6_family"] = fam
    multi = rec[rec.gbif_key.notna() & ~rec.is_morphospecies].groupby("gbif_key").filter(
        lambda g: g.source.nunique() > 1)
    st = []
    for key, g in multi.groupby("gbif_key"):
        vals = {row.source: json.loads(row.status) for row in g.itertuples()}
        iucn = {s: next((v for k, v in d.items() if k.startswith("IUCN")), None) for s, d in vals.items()}
        vnrl = {s: next((v for k, v in d.items() if k.startswith(("DLDVN", "SDVN"))), None) for s, d in vals.items()}
        st.append(dict(gbif_key=key, name=g.gbif_name.iloc[0], sources=",".join(sorted(g.source)),
                       src_names="; ".join(sorted(set(g.canonical))), vn_names="; ".join(sorted(set(g.vn_name.dropna()))),
                       iucn=json.dumps(iucn, ensure_ascii=False), vn_redlist=json.dumps(vnrl, ensure_ascii=False),
                       iucn_conflict=len({v for v in iucn.values() if v}) > 1,
                       src_family_conflict=g.src_family.dropna().str.lower().nunique() > 1))
    e6 = pd.DataFrame(st)
    e6.to_csv(OUT / "eval_E6_cross_source.csv", index=False)
    report["E6_cross"] = e6
    # E7: effect of name reconciliation on cross-waterbody overlap (verbatim vs GBIF-accepted names)
    sp = rec[~rec.is_morphospecies & ~rec.is_higher_taxon].copy()
    sp["accepted"] = sp.gbif_accepted.fillna(sp.gbif_name).where(~sp.gbif_match.isin(["none", "higherrank", "fuzzy_rejected"]),
                                                                  sp.canonical)
    rows = []
    for grp, pairs in {"fish": [("Hồ Ayun Hạ", "Hồ TĐ Ialy"), ("Hồ Ayun Hạ", "Sông Sê San"),
                                ("Hồ TĐ Ialy", "Sông Sê San")],
                       "zoobenthos": [("Hồ Ayun Hạ", "Biển Hồ")]}.items():
        for a, b in pairs:
            for col in ("canonical", "accepted"):
                A = set(sp[(sp.group == grp) & (sp.waterbody == a)][col])
                B = set(sp[(sp.group == grp) & (sp.waterbody == b)][col])
                rows.append(dict(group=grp, pair=f"{a} – {b}", names=col, n_a=len(A), n_b=len(B),
                                 shared=len(A & B), sorensen=round(2 * len(A & B) / (len(A) + len(B)), 3),
                                 gained=sorted(A & B) if col == "accepted" else None))
    e7 = pd.DataFrame(rows)
    base = e7[e7.names == "canonical"].set_index("pair").shared
    e7["gained_by_reconciliation"] = [
        sorted(set(r.gained) - set(sp[(sp.group == r.group)].pipe(lambda d: set(
            d[d.waterbody == r.pair.split(" – ")[0]].canonical) & set(d[d.waterbody == r.pair.split(" – ")[1]].canonical))))
        if r.names == "accepted" else "" for r in e7.itertuples()]
    e7 = e7.drop(columns="gained")
    e7.to_csv(OUT / "eval_E7_reconciliation_overlap.csv", index=False)
    report["E7"] = e7
    return report


if __name__ == "__main__":
    pd.set_option("display.width", 250)
    pd.set_option("display.max_columns", 30)
    pd.set_option("display.max_colwidth", 60)
    r = run()
    for k, v in r.items():
        print(f"===== {k}")
        print(v.to_string() if len(v) < 60 else v.head(60).to_string())
