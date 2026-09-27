"""Stage 4: parse raw scientific-name strings into canonical name, authorship and flags."""
import re
import unicodedata
from dataclasses import dataclass

SYMBOLS = "●♠♦♣*†§¤"
INFRA = r"(?:var\.|subsp\.|ssp\.|f\.|forma)"
EPITHET = r"[a-z][a-z\-]+"
MORPHO = r"(?:sp|spp)\.?\s?\d*\.?|sp\d+\.?"


@dataclass
class ParsedName:
    canonical: str          # e.g. "Microcystis aeruginosa", "Acentrella sp."
    genus: str
    epithet: str | None
    infra: str | None
    authorship: str
    year: int | None
    qualifier: str | None   # cf. / aff.
    is_morphospecies: bool
    is_higher_taxon: bool   # e.g. "Bivalvia" larvae, "Copepoda nauplius"
    symbols: str            # footnote symbols printed next to the name
    notes: list


def _fold(s: str) -> str:
    """Strip diacritics that sometimes appear in Latin names (Tetraëdron -> Tetraedron)."""
    return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")


def parse(raw: str) -> ParsedName:
    notes = []
    symbols = "".join(c for c in raw if c in SYMBOLS)
    s = "".join(c for c in raw if c not in SYMBOLS)
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip(" ,;")
    s = re.sub(r"\s(\d(?:,\d)+|[123])$", "", s)          # trailing campaign list, e.g. "... 1,2,3"
    folded = _fold(s)
    if folded != s:
        notes.append("diacritic_in_latin")
    qual = None
    m = re.match(rf"^([A-Z][a-z]+)\s+(cf\.|aff\.)?\s*({MORPHO}|{EPITHET})(?:\s+({EPITHET}))?"
                 rf"(?:\s+{INFRA}\s+({EPITHET}))?\b(.*)$", folded)
    if not m:
        g = re.match(r"^([A-Z][a-z]+)\b(.*)$", folded)
        genus = g.group(1) if g else folded
        return ParsedName(genus, genus, None, None, (g.group(2) if g else "").strip(), None, None,
                          False, True, symbols, notes + ["higher_or_unparsed"])
    genus, qual, ep, ep2, infra, rest = m.groups()
    rest = s[m.start(6):]                      # keep diacritics in authorship (NFC->folded keeps length)
    if ep in ("nauplius", "larva", "larvae", "juvenile"):
        return ParsedName(genus, genus, None, None, "", None, None, False, True, symbols,
                          notes + ["life_stage:" + ep])
    morpho = bool(re.fullmatch(MORPHO, ep))
    if ep2 and ep2 == ep:                       # "Brachionus calyciflorus calyciflorus" (nominotypical)
        infra, notes = ep2, notes + ["nominotypical_subspecies"]
    elif ep2 and not morpho and rest.strip()[:1] not in ("(", "") and not re.match(r"[A-Z]", ep2):
        rest = f" {ep2}{rest}"                  # was actually part of authorship (lower-case particle)
    elif ep2 and not morpho:
        infra = ep2
    if morpho:
        num = re.search(r"\d+", ep)
        canonical = f"{genus} sp." + (num.group(0) if num else "")   # sp1 and sp2 are different taxa
        ep = None
    else:
        canonical = f"{genus} {ep}" + (f" {infra}" if infra and infra != ep else "")
    auth = rest.strip(" ,.")
    auth = re.sub(r"^(nauplius|larva[e]?|juvenile)\b", lambda x: notes.append("life_stage") or "", auth).strip()
    year = re.search(r"\b(1[7-9]\d\d|20[0-2]\d)\b", auth)
    if auth and not year:
        notes.append("authorship_without_year")
    if re.search(r"\(\s*[^()]*$", auth):
        notes.append("unbalanced_parenthesis")
    return ParsedName(canonical, genus, ep, infra, auth, int(year.group(1)) if year else None, qual,
                      morpho, False, symbols, notes)
