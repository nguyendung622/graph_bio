"""Baselines and ablations reported in the paper.

  B1  pdftotext (reading order) + binomial regex over the checklist region
  B2  pdftotext -layout       + binomial regex over the checklist region
  Ours full pipeline; name-level scores against the reference checklist (records validated
      against the authors' reported counts, see evaluate.py)
  A1  cell accuracy without bbox re-rendering (layout text only)
  A2  record completeness without wrapped-row merging
  A3  name resolution without the context-hinted second pass
  A4  hierarchy repair without the context lexicon (raw damaged names)
"""
import re
import subprocess
from pathlib import Path

import pandas as pd

from . import extract as X
from .names import parse
from .sources import DATA, SOURCES

OUT = Path(__file__).resolve().parent.parent / "extracted" / "gialai"
BINOMIAL = re.compile(r"\b([A-Z][a-z]{2,})\s+(sp\.?\s?\d*|[a-z][a-z\-]{2,})\b")
STOP = {"Tên", "Bảng", "Ngành", "Lớp", "Họ", "Bộ"}


def region(text, src):
    lines = text.splitlines()
    st = next(i for i, l in enumerate(lines) if re.search(src["table"], l))
    en = next((i for i in range(st + 1, len(lines)) if re.match(r"^\s*(Bảng \d+\.|Ghi chú)", lines[i])), len(lines))
    return "\n".join(lines[st + 1:en])


def regex_names(text):
    out = set()
    for g, e in BINOMIAL.findall(text):
        if g in STOP:
            continue
        out.add(f"{g} sp." if e.startswith("sp") else f"{g} {e}")
    return out


def prf(pred, gold):
    tp = len(pred & gold)
    p = tp / len(pred) if pred else 0
    r = tp / len(gold) if gold else 0
    return round(p, 3), round(r, 3), round(2 * p * r / (p + r), 3) if p + r else 0


def run():
    rec = pd.read_csv(OUT / "checklist_records.csv")
    rows = []
    for src in SOURCES:
        if src["kind"] != "pdf":
            continue
        gold = {re.sub(r"sp\.\d+$", "sp.", c) for c in rec[rec.source == src["id"]].canonical}
        raw = subprocess.run(["pdftotext", str(DATA / src["file"]), "-"], capture_output=True).stdout.decode()
        lay = X.pdf_text(DATA / src["file"])
        for name, txt in (("B1 pdftotext+regex", raw), ("B2 layout+regex", lay)):
            try:
                pred = regex_names(region(txt, src))
            except StopIteration:      # caption itself is split in reading-order text
                pred = regex_names(txt)
            rows.append(dict(source=src["id"], method=name, n_pred=len(pred), n_gold=len(gold),
                             **dict(zip(("P", "R", "F1"), prf(pred, gold)))))
        recs, _ = X.extract_source(src)
        pred = {re.sub(r"sp\.\d+$", "sp.", parse(r.raw_name).canonical) for r in recs}
        rows.append(dict(source=src["id"], method="Ours", n_pred=len(pred), n_gold=len(gold),
                         **dict(zip(("P", "R", "F1"), prf(pred, gold)))))
    names = pd.DataFrame(rows)
    names.to_csv(OUT / "ablation_names.csv", index=False)

    # A1: cell accuracy with / without bbox rendering
    rows = []
    for src in SOURCES:
        n = src["reported"].get("sites")
        if src["kind"] != "pdf" or not n:
            continue
        for render in ("layout", "bbox"):
            s2 = dict(src, render=render)
            recs, meta = X.extract_source(s2)
            t = (meta.get("totals_row") or [])[:n]
            got = [sum(1 for r in recs if r.sites.get(f"M{i}") == "+") for i in range(1, n + 1)]
            rows.append(dict(source=src["id"], render=render, records=len(recs),
                             site_totals_matched=sum(a == b for a, b in zip(t, got)) if t else None, sites=n))
    cells = pd.DataFrame(rows)
    cells.to_csv(OUT / "ablation_cells.csv", index=False)

    # A2: without wrapped-row merging; independent precision check: canonical name printed verbatim in the PDF
    rows = []
    for src in SOURCES:
        if src["kind"] != "pdf":
            continue
        flat = re.sub(r"\s+", " ", X.pdf_text(DATA / src["file"]))
        flat_folded = "".join(c for c in __import__("unicodedata").normalize("NFD", flat)
                              if __import__("unicodedata").category(c) != "Mn")
        gold = list(rec[rec.source == src["id"]].canonical)
        for variant in ("full", "no_merge"):
            recs, _ = X.extract_source(dict(src, no_merge=variant == "no_merge"))
            pred = [parse(r.raw_name).canonical for r in recs]
            ok = sum(a == b for a, b in zip(pred, gold)) if len(pred) == len(gold) else None
            empty = sum(1 for r in recs if not re.match(r"[A-Z][a-z]+ ", r.raw_name))
            verbatim = sum(1 for c in pred if re.sub(r"sp\.\d+$", "sp", c).split(" sp")[0] in flat_folded)
            rows.append(dict(source=src["id"], variant=variant, records=len(recs), names_equal_reference=ok,
                             records_without_binomial=empty, canonical_found_verbatim=verbatim))
    merge = pd.DataFrame(rows)
    merge.to_csv(OUT / "ablation_merge_verbatim.csv", index=False)
    return names, cells, merge


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    a, b, c = run()
    print(a.groupby("method")[["P", "R", "F1"]].mean().round(3))
    print(b.to_string())
    print(c.to_string())
