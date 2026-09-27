"""Stage 6: build the Gia Lai aquatic-biodiversity knowledge graph (RDF, Turtle).

Vocabularies reused: Darwin Core (dwc), SOSA/SSN, PROV-O, W3C WGS84 geo, Dublin Core, SKOS.
Local terms live in the bkg: namespace (placeholder IRI; change BASE before publishing).

Usage:  python -m biokg.kg
"""
import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from rdflib import RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, PROV, SKOS

from .sources import APPENDIX, SOURCES

OUT = Path(__file__).resolve().parent.parent / "extracted" / "gialai"
BASE = "https://biokg.example.org/gialai/"
BKG = Namespace(BASE + "ontology#")
RES = Namespace(BASE + "resource/")
DWC = Namespace("http://rs.tdwg.org/dwc/terms/")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
GEO = Namespace("http://www.w3.org/2003/01/geo/wgs84_pos#")
GBIF = Namespace("https://www.gbif.org/species/")

WATERBODY_TYPE = {"Hồ Ayun Hạ": "Hồ chứa thủy lợi", "Hồ TĐ Ialy": "Hồ chứa thủy điện",
                  "Sông Sê San": "Sông", "Biển Hồ": "Hồ tự nhiên (miệng núi lửa)"}
TRAIT = {"economic": BKG.EconomicValue, "aquaculture": BKG.AquacultureValue, "ornamental": BKG.OrnamentalValue,
         "alien": BKG.AlienSpecies, "invasive": BKG.InvasiveAlienSpecies,
         "potential_invasive": BKG.PotentialInvasiveSpecies, "widespread_invasive": BKG.WidespreadInvasiveSpecies,
         "Tảo độc": BKG.ToxicCyanobacterium, "Tảo gây hại": BKG.HarmfulAlga}
THREAT = {"CR", "EN", "VU", "NT", "EW", "EX"}


def slug(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^A-Za-z0-9]+", "_", s.replace("đ", "d").replace("Đ", "D")).strip("_")


def taxon_iri(row) -> URIRef:
    if pd.notna(row.get("gbif_key")) and row.get("gbif_match") not in ("none", "fuzzy_rejected"):
        return GBIF[str(int(row["gbif_key"]))]
    return RES["taxon/" + slug(row["canonical"])]


def build() -> Graph:
    g = Graph()
    for p, ns in dict(bkg=BKG, res=RES, dwc=DWC, sosa=SOSA, geo=GEO, gbif=GBIF, prov=PROV, dct=DCTERMS,
                      skos=SKOS).items():
        g.bind(p, ns)
    rec = pd.read_csv(OUT / "checklist_records.csv")
    pres = pd.read_csv(OUT / "site_presence.csv")
    sites = pd.read_csv(OUT / "sites.csv")
    ab = pd.read_csv(OUT / "ayunha_abundance.csv")
    wq = pd.read_csv(OUT / "ayunha_water_quality.csv")
    srcmap = {s["id"]: s for s in SOURCES}

    # ---- ontology skeleton (classes and issue concepts)
    for c in ["SourceDocument", "Waterbody", "SamplingSite", "NameUsage", "ConservationAssessment",
              "SiteOccurrence", "AbundanceObservation", "WaterQualityObservation", "Trait", "CurationIssue"]:
        g.add((BKG[c], RDF.type, RDFS.Class))
    issues = {"misspelling": "Tên viết sai chính tả (khớp mờ GBIF)",
              "outdated_name": "Tên đồng nghĩa / đã lỗi thời",
              "family_conflict": "Họ trong tài liệu khác họ trong GBIF",
              "unresolved": "Không đối sánh được / chỉ khớp bậc cao",
              "homonym_resolved": "Tên trùng giữa các giới, phân giải nhờ ngữ cảnh",
              "no_site_data": "Không có dữ liệu có/không tại điểm nào"}
    for k, v in issues.items():
        g.add((BKG[k], RDF.type, BKG.CurationIssue))
        g.add((BKG[k], SKOS.prefLabel, Literal(v, lang="vi")))
    for t in set(TRAIT.values()):
        g.add((t, RDF.type, BKG.Trait))

    # ---- sources, waterbodies
    all_src = SOURCES + [dict(APPENDIX, group="plankton+water_quality", year=2022, reported={})]
    for s in all_src:
        u = RES["source/" + s["id"]]
        g.add((u, RDF.type, BKG.SourceDocument))
        g.add((u, DCTERMS.bibliographicCitation, Literal(s["cite"], lang="vi")))
        g.add((u, DCTERMS.date, Literal(str(s["year"]), datatype=XSD.gYear)))
        g.add((u, BKG.taxonGroup, Literal(s["group"])))
        for k, v in s.get("reported", {}).items():
            g.add((u, BKG["reported_" + k], Literal(v, datatype=XSD.integer)))
    for wb, typ in WATERBODY_TYPE.items():
        u = RES["waterbody/" + slug(wb)]
        g.add((u, RDF.type, BKG.Waterbody))
        g.add((u, RDFS.label, Literal(wb, lang="vi")))
        g.add((u, BKG.waterbodyType, Literal(typ, lang="vi")))
        g.add((u, BKG.province, Literal("Gia Lai", lang="vi")))

    # ---- sites (one node per coordinate cluster; local codes kept per source)
    local = {}
    for r in sites.itertuples():
        u = RES["site/" + r.site_uid]
        g.add((u, RDF.type, BKG.SamplingSite))
        g.add((u, GEO.lat, Literal(r.lat, datatype=XSD.decimal)))
        g.add((u, GEO.long, Literal(r.lon, datatype=XSD.decimal)))
        g.add((u, BKG.inWaterbody, RES["waterbody/" + slug(r.waterbody)]))
        g.add((u, BKG.localCode, Literal(f"{r.source}:{r.site}")))
        local[(r.source, r.site)] = u
    # appendix (2021-22 project) uses the same M1-M11 scheme as the zooplankton paper of that project
    for code in {c for (s_, c) in local if s_ == "AH_DVN"}:
        local[("AH_PL", code)] = local[("AH_DVN", code)]

    # ---- taxa and name usages
    for r in rec.to_dict("records"):
        t = taxon_iri(r)
        g.add((t, RDF.type, DWC.Taxon))
        if isinstance(r["gbif_name"], str):
            g.add((t, DWC.scientificName, Literal(r["gbif_name"])))
            g.add((t, DWC.taxonRank, Literal(str(r["gbif_rank"]).lower())))
            g.add((t, BKG.gbifTaxonomicStatus, Literal(r["gbif_status"])))
            for k in ("kingdom", "phylum", "class", "order", "family", "genus"):
                if isinstance(r[f"gbif_{k}"], str):
                    g.add((t, DWC[k], Literal(r[f"gbif_{k}"])))
            if isinstance(r["gbif_accepted"], str):
                g.add((t, BKG.acceptedNameGBIF, Literal(r["gbif_accepted"])))
        else:
            g.add((t, DWC.scientificName, Literal(r["canonical"])))

        u = RES[f"usage/{r['source']}/{r['idx']}"]
        g.add((u, RDF.type, BKG.NameUsage))
        g.add((u, BKG.verbatimName, Literal(r["raw_name"])))
        g.add((u, DWC.scientificName, Literal(r["canonical"])))
        if isinstance(r["authorship"], str):
            g.add((u, DWC.scientificNameAuthorship, Literal(r["authorship"])))
        if isinstance(r["vn_name"], str) and r["vn_name"]:
            g.add((u, DWC.vernacularName, Literal(r["vn_name"], lang="vi")))
        if isinstance(r["src_family"], str):
            g.add((u, BKG.verbatimFamily, Literal(r["src_family"])))
        g.add((u, BKG.resolvesTo, t))
        g.add((u, BKG.matchType, Literal(r["gbif_match"])))
        g.add((u, BKG.isMorphospecies, Literal(bool(r["is_morphospecies"]))))
        g.add((u, BKG.recordedIn, RES["waterbody/" + slug(r["waterbody"])]))
        g.add((u, PROV.wasDerivedFrom, RES["source/" + r["source"]]))
        g.add((u, BKG.rowIndex, Literal(int(r["idx"]))))
        # curation issues
        if r["gbif_match"] == "fuzzy":
            g.add((u, BKG.hasIssue, BKG.misspelling))
        if r["gbif_match"] == "synonym":
            g.add((u, BKG.hasIssue, BKG.outdated_name))
        if r["gbif_match"] in ("none", "higherrank", "fuzzy_rejected"):
            g.add((u, BKG.hasIssue, BKG.unresolved))
        if r["gbif_pass"] == 2:
            g.add((u, BKG.hasIssue, BKG.homonym_resolved))
        if r["family_agrees"] is False or str(r["family_agrees"]) == "False":
            g.add((u, BKG.hasIssue, BKG.family_conflict))
        if srcmap[r["source"]]["reported"].get("sites") and r["n_sites_marked"] == 0:
            g.add((u, BKG.hasIssue, BKG.no_site_data))
        # conservation status and traits
        for scheme, cat in json.loads(r["status"]).items():
            if scheme in ("codes", "specimen", "interview"):
                if scheme == "specimen":
                    g.add((u, BKG.evidence, Literal("specimen")))
                if scheme == "interview":
                    g.add((u, BKG.evidence, Literal("interview")))
                continue
            if scheme in TRAIT:
                g.add((u, BKG.hasTrait, TRAIT[scheme]))
                continue
            a = RES[f"assessment/{r['source']}/{r['idx']}/{scheme}"]
            name, _, ver = scheme.partition("_")
            g.add((a, RDF.type, BKG.ConservationAssessment))
            g.add((a, BKG.scheme, Literal(name)))
            g.add((a, BKG.schemeVersion, Literal(ver)))
            g.add((a, BKG.category, Literal(cat.replace(" ", ""))))
            g.add((a, BKG.assessedTaxon, t))
            g.add((a, PROV.wasDerivedFrom, RES["source/" + r["source"]]))
            g.add((u, BKG.hasAssessment, a))
        legend = srcmap[r["source"]].get("symbol_legend", {})
        for sym, trait in legend.items():
            if isinstance(r["symbols"], str) and sym in r["symbols"]:
                g.add((u, BKG.hasTrait, TRAIT[trait]))
        if r["source"] == "AH_NL" and isinstance(r["extra"], str):
            g.add((u, BKG.nativeRange, Literal(r["extra"], lang="vi")))

    # ---- site-level presence/absence
    for r in pres.itertuples():
        site = local.get((r.source, r.site))
        if site is None:
            continue
        o = RES[f"siteocc/{r.source}/{r.idx}/{r.site}"]
        g.add((o, RDF.type, BKG.SiteOccurrence))
        g.add((o, BKG.ofUsage, RES[f"usage/{r.source}/{r.idx}"]))
        g.add((o, BKG.atSite, site))
        g.add((o, DWC.occurrenceStatus, Literal("present" if r.present else "absent")))

    # ---- quantitative observations from the project appendix
    for i, r in enumerate(ab.itertuples()):
        o = RES[f"obs/abundance/{i}"]
        g.add((o, RDF.type, BKG.AbundanceObservation))
        g.add((o, RDF.type, SOSA.Observation))
        tax = GBIF[str(int(r.gbif_key))] if pd.notna(r.gbif_key) else RES["taxon/" + slug(r.canonical)]
        g.add((tax, RDF.type, DWC.Taxon))
        g.add((o, BKG.observedTaxon, tax))
        if (r.source, r.site) in local:
            g.add((o, SOSA.hasFeatureOfInterest, local[(r.source, r.site)]))
        g.add((o, BKG.localSiteCode, Literal(r.site)))
        g.add((o, SOSA.resultTime, Literal(r.campaign, datatype=XSD.gYearMonth)))
        g.add((o, BKG.taxonGroup, Literal(r.group)))
        if r.value >= 0:
            g.add((o, SOSA.hasSimpleResult, Literal(r.value, datatype=XSD.decimal)))
            g.add((o, BKG.unit, Literal("cells/L" if r.group == "phytoplankton" else "individuals/m3")))
        else:
            g.add((o, DWC.occurrenceStatus, Literal("present")))
        if isinstance(r.trait, str) and r.trait in TRAIT:
            g.add((tax, BKG.hasTrait, TRAIT[r.trait]))
        g.add((o, PROV.wasDerivedFrom, RES["source/AH_PL"]))
    for i, r in enumerate(wq.itertuples()):
        o = RES[f"obs/wq/{i}"]
        prop = RES["property/" + slug(r.parameter)]
        g.add((prop, RDFS.label, Literal(r.parameter, lang="vi")))
        g.add((o, RDF.type, BKG.WaterQualityObservation))
        g.add((o, RDF.type, SOSA.Observation))
        g.add((o, SOSA.observedProperty, prop))
        if (r.source, r.site) in local:
            g.add((o, SOSA.hasFeatureOfInterest, local[(r.source, r.site)]))
        g.add((o, BKG.localSiteCode, Literal(r.site)))
        g.add((o, SOSA.resultTime, Literal(r.campaign, datatype=XSD.gYearMonth)))
        g.add((o, SOSA.hasSimpleResult, Literal(r.value, datatype=XSD.decimal)))
        g.add((o, PROV.wasDerivedFrom, RES["source/AH_PL"]))
    return g


def run_queries(g: Graph):
    qdir = Path(__file__).resolve().parent / "queries"
    rdir = OUT / "cq_results"
    rdir.mkdir(exist_ok=True)
    summary = {}
    for q in sorted(qdir.glob("*.rq")):
        res = g.query(q.read_text())
        rows = [[str(x) if x is not None else "" for x in row] for row in res]
        df = pd.DataFrame(rows, columns=[str(v) for v in res.vars])
        df.to_csv(rdir / (q.stem + ".csv"), index=False)
        summary[q.stem] = df
    return summary


if __name__ == "__main__":
    g = build()
    g.serialize(OUT / "gialai_biokg.ttl", format="turtle")
    print("triples:", len(g))
    for cls in ["SourceDocument", "Waterbody", "SamplingSite", "NameUsage", "ConservationAssessment",
                "SiteOccurrence", "AbundanceObservation", "WaterQualityObservation"]:
        print(f"  {cls}: {len(set(g.subjects(RDF.type, BKG[cls])))}")
    print(f"  dwc:Taxon: {len(set(g.subjects(RDF.type, DWC.Taxon)))}")
    pd.set_option("display.width", 250)
    pd.set_option("display.max_colwidth", 70)
    for name, df in run_queries(g).items():
        print(f"===== {name} ({len(df)} rows)")
        print(df.head(25).to_string())
