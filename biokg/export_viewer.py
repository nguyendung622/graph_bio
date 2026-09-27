"""Export the knowledge graph (gialai_biokg.ttl) to a compact JSON for the browser viewer.

Nodes: Taxon, NameUsage, SourceDocument, Waterbody, SamplingSite, ConservationAssessment.
SiteOccurrence and observation nodes are too many to draw; they are summarised per usage / taxon / site,
and each node keeps its real RDF triples (subject position) as Turtle text.
Usage:  python -m biokg.export_viewer
"""
import csv
import json
from collections import defaultdict
from pathlib import Path

from rdflib import RDF, Graph, URIRef

from .kg import BKG, DWC, GEO, OUT, SOSA
from rdflib.namespace import DCTERMS, PROV, RDFS, SKOS

ROOT = Path(__file__).resolve().parent.parent
# standalone repository layout uses ./viewer; the working project keeps paper/kg_viewer
VIEW = ROOT / "viewer" if (ROOT / "viewer").is_dir() else ROOT / "paper" / "kg_viewer"
TYPES = {BKG.NameUsage: "NameUsage", DWC.Taxon: "Taxon", BKG.SourceDocument: "SourceDocument",
         BKG.Waterbody: "Waterbody", BKG.SamplingSite: "SamplingSite",
         BKG.ConservationAssessment: "ConservationAssessment"}


def main():
    g = Graph()
    g.parse(OUT / "gialai_biokg.ttl", format="turtle")
    nm = g.namespace_manager
    short = lambda t: t.n3(nm)  # noqa: E731

    def ttl(s):
        lines = [f"{short(s)}"]
        preds = sorted(g.predicate_objects(s), key=lambda po: (po[0] != RDF.type, short(po[0])))
        for i, (p, o) in enumerate(preds):
            end = " ." if i == len(preds) - 1 else " ;"
            lines.append(f"    {short(p)} {short(o)}{end}")
        return "\n".join(lines)

    first = lambda s, p: next(g.objects(s, p), None)  # noqa: E731
    nodes, edges = {}, []
    for cls, typ in TYPES.items():
        for s in set(g.subjects(RDF.type, cls)):
            nodes[str(s)] = dict(id=str(s), type=typ, ttl=ttl(s))

    for sid, n in nodes.items():
        s = URIRef(sid)
        t = n["type"]
        if t == "Taxon":
            n["label"] = str(first(s, DWC.scientificName) or sid.rsplit("/", 1)[-1])
            n["rank"] = str(first(s, DWC.taxonRank) or "")
            n["family"] = str(first(s, DWC.family) or "")
            n["traits"] = sorted(str(x).split("#")[1] for x in g.objects(s, BKG.hasTrait))
        elif t == "NameUsage":
            src = str(first(s, PROV.wasDerivedFrom)).rsplit("/", 1)[-1]
            n["label"] = str(first(s, DWC.scientificName))
            n["verbatim"] = str(first(s, BKG.verbatimName))
            n["vn"] = str(first(s, DWC.vernacularName) or "")
            n["source"] = src
            n["match"] = str(first(s, BKG.matchType))
            n["issues"] = sorted(str(x).split("#")[1] for x in g.objects(s, BKG.hasIssue))
            n["traits"] = sorted(str(x).split("#")[1] for x in g.objects(s, BKG.hasTrait))
            for p, rel in ((BKG.resolvesTo, "resolvesTo"), (PROV.wasDerivedFrom, "wasDerivedFrom"),
                           (BKG.recordedIn, "recordedIn"), (BKG.hasAssessment, "hasAssessment")):
                for o in g.objects(s, p):
                    edges.append([sid, str(o), rel])
        elif t == "SourceDocument":
            n["label"] = sid.rsplit("/", 1)[-1]
            n["cite"] = str(first(s, DCTERMS.bibliographicCitation))
            n["group"] = str(first(s, BKG.taxonGroup))
        elif t == "Waterbody":
            n["label"] = str(first(s, RDFS.label))
            n["kind"] = str(first(s, BKG.waterbodyType))
        elif t == "SamplingSite":
            codes = sorted(str(x) for x in g.objects(s, BKG.localCode))
            n["label"] = sid.rsplit("/", 1)[-1] + " (" + ", ".join(c.split(":")[1] for c in codes[:1]) + ")"
            n["codes"] = codes
            n["lat"], n["lon"] = float(first(s, GEO.lat)), float(first(s, GEO.long))
            edges.append([sid, str(first(s, BKG.inWaterbody)), "inWaterbody"])
        elif t == "ConservationAssessment":
            n["label"] = f"{first(s, BKG.scheme)} {first(s, BKG.schemeVersion)}: {first(s, BKG.category)}"
            edges.append([sid, str(first(s, BKG.assessedTaxon)), "assessedTaxon"])

    # site occurrences -> presence table per usage, and usage -> site edges for "present"
    occ_example = None
    for o in g.subjects(RDF.type, BKG.SiteOccurrence):
        u, site = str(first(o, BKG.ofUsage)), str(first(o, BKG.atSite))
        status = str(first(o, DWC.occurrenceStatus))
        if u in nodes:
            nodes[u].setdefault("sites", []).append([site.rsplit("/", 1)[-1], status])
            if status == "present":
                edges.append([u, site, "presentAt"])
        occ_example = occ_example or ttl(o)

    # observations -> per taxon and per site summaries
    ab_tax, ab_site, wq_site = defaultdict(list), defaultdict(int), defaultdict(int)
    obs_example = wq_example = None
    for o in g.subjects(RDF.type, BKG.AbundanceObservation):
        t, site = str(first(o, BKG.observedTaxon)), first(o, SOSA.hasFeatureOfInterest)
        v, time = first(o, SOSA.hasSimpleResult), str(first(o, SOSA.resultTime))
        code = str(first(o, BKG.localSiteCode))
        if v is not None:
            ab_tax[t].append([time, code, float(v), str(first(o, BKG.unit))])
        if site is not None:
            ab_site[str(site)] += 1
        obs_example = obs_example or ttl(o)
    for o in g.subjects(RDF.type, BKG.WaterQualityObservation):
        site = first(o, SOSA.hasFeatureOfInterest)
        if site is not None:
            wq_site[str(site)] += 1
        wq_example = wq_example or ttl(o)
    for t, rows in ab_tax.items():
        if t in nodes:
            rows.sort(key=lambda r: -r[2])
            nodes[t]["abundance"] = dict(n=len(rows), top=rows[:8])
    for s, n in ab_site.items():
        if s in nodes:
            nodes[s]["n_abundance"] = n
    for s, n in wq_site.items():
        if s in nodes:
            nodes[s]["n_wq"] = n

    stats = dict(triples=len(g))
    for cls in ["SourceDocument", "Waterbody", "SamplingSite", "NameUsage", "ConservationAssessment",
                "SiteOccurrence", "AbundanceObservation", "WaterQualityObservation"]:
        stats[cls] = len(set(g.subjects(RDF.type, BKG[cls])))
    stats["Taxon"] = len(set(g.subjects(RDF.type, DWC.Taxon)))

    queries = []
    for q in sorted((Path(__file__).parent / "queries").glob("*.rq")):
        with open(OUT / "cq_results" / (q.stem + ".csv"), encoding="utf-8") as f:
            rows = list(csv.reader(f))
        queries.append(dict(name=q.stem, sparql=q.read_text(encoding="utf-8"), header=rows[0] if rows else [],
                            rows=rows[1:]))

    data = dict(stats=stats, nodes=list(nodes.values()), edges=edges, queries=queries,
                examples=dict(SiteOccurrence=occ_example, AbundanceObservation=obs_example,
                              WaterQualityObservation=wq_example))
    VIEW.mkdir(parents=True, exist_ok=True)
    (VIEW / "kg_data.json").write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")),
                                        encoding="utf-8")
    # single-file page: the JSON is embedded, so the HTML also opens directly from disk
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    for tpl_name, out_name in (("template.html", "kg_explorer.html"), ("template_en.html", "kg_explorer_en.html")):
        if (VIEW / tpl_name).exists():
            tpl = (VIEW / tpl_name).read_text(encoding="utf-8")
            (VIEW / out_name).write_text(tpl.replace("__KG_DATA__", blob), encoding="utf-8")
    print(stats, len(nodes), "nodes", len(edges), "edges",
          round((VIEW / "kg_data.json").stat().st_size / 1e6, 2), "MB")


if __name__ == "__main__":
    main()
