"""Stage 5: resolve names against the GBIF Backbone Taxonomy, and repair glyph-damaged
higher-taxon names using a context lexicon built from the resolved species.
"""
import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

GBIF = "https://api.gbif.org/v1/species/match"
RANKS = ["kingdom", "phylum", "class", "order", "family", "genus"]


class GbifResolver:
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self.cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}

    def _fetch(self, key):
        name, rank, *hints = key.split("|")
        q = {"name": name, "verbose": "false"}
        if rank:
            q["rank"] = rank
        for h in hints:                    # context hints, e.g. "family=Ephemeridae"
            k, v = h.split("=", 1)
            q[k] = v
        url = GBIF + "?" + urllib.parse.urlencode(q)
        for attempt in range(4):
            try:
                with urllib.request.urlopen(url, timeout=30) as r:
                    return key, json.loads(r.read())
            except Exception:  # transient network errors: back off and retry
                time.sleep(1.5 * (attempt + 1))
        return key, {"matchType": "ERROR"}

    def match_many(self, queries: list[tuple]) -> dict:
        """queries: [(name, rank or '', *hints)]. Returns {'name|rank|hints': gbif_json}."""
        wanted = {"|".join(q) for q in queries}
        with ThreadPoolExecutor(8) as ex:
            for k, v in ex.map(self._fetch, sorted(wanted - set(self.cache))):
                self.cache[k] = v
        self.cache_path.write_text(json.dumps(self.cache, ensure_ascii=False, indent=0))
        return {k: self.cache[k] for k in wanted}


KINGDOM_OF_GROUP = {"fish": "Animalia", "zoobenthos": "Animalia", "zooplankton": "Animalia",
                    "aquatic_insects": "Animalia"}


def hint_query(parsed, family, order, group) -> tuple:
    """Second-pass query with higher-taxon context from the source table (homonym disambiguation)."""
    name, rank = query_for(parsed)
    hints = []
    if isinstance(family, str) and " " not in family:
        hints.append(f"family={family.capitalize()}")
    if isinstance(order, str) and " " not in order:
        hints.append(f"order={order.capitalize()}")
    if group in KINGDOM_OF_GROUP:
        hints.append(f"kingdom={KINGDOM_OF_GROUP[group]}")
    return (name, rank, *hints)


def query_for(parsed) -> tuple[str, str]:
    """What to send to GBIF for a parsed name."""
    if parsed.is_morphospecies:
        return parsed.genus, "GENUS"
    if parsed.is_higher_taxon:
        return parsed.canonical, ""
    return parsed.canonical, "SPECIES"


def classify_match(res: dict, parsed) -> str:
    """Collapse GBIF output into: exact / fuzzy / synonym / higherrank / none."""
    mt = res.get("matchType", "NONE")
    if mt in ("NONE", "ERROR"):
        return "none"
    if mt == "HIGHERRANK" and not parsed.is_morphospecies:
        return "higherrank"
    if parsed.is_morphospecies and res.get("rank") not in ("GENUS", None):
        return "higherrank"           # genus query answered only at family level or above
    if res.get("status") in ("SYNONYM", "HETEROTYPIC_SYNONYM", "HOMOTYPIC_SYNONYM", "PROPARTE_SYNONYM"):
        return "synonym"
    return "fuzzy" if mt == "FUZZY" else "exact"


# ------------------------------------------------------------ glyph-loss repair
def gap_pattern(damaged: str) -> re.Pattern | None:
    """'Arce inida' -> ^arce[a-z]{1,4}inida$ ; returns None for names without internal gaps."""
    parts = damaged.split()
    if len(parts) < 2 or not all(re.fullmatch(r"[A-Za-z]+", p) for p in parts):
        return None
    return re.compile("^" + "[a-z]{1,4}".join(p.lower() for p in parts) + "$")


def repair_with_lexicon(damaged: str, lexicon: set[str]) -> str | None:
    pat = gap_pattern(damaged)
    if not pat:
        return None
    hits = sorted({w for w in lexicon if pat.match(w.lower())})
    return hits[0] if len(hits) == 1 else None
