# Data dictionary

All files are in `extracted/gialai/`. Document codes (`source`) are listed in the main README.

## checklist_records.csv — one row per checklist row (581 rows)

| Column | Meaning |
|---|---|
| `source`, `waterbody`, `group` | Document code, waterbody (Vietnamese name), taxonomic group |
| `idx` | Row number printed in the source table |
| `raw_name` | Name string as extracted, including authorship and symbols |
| `vn_name` | Vietnamese vernacular name, where printed |
| `canonical`, `genus` | Parsed canonical name and genus; morphospecies are written `Genus sp.` or `Genus sp.N` |
| `authorship`, `year` | Parsed authorship and year |
| `is_morphospecies`, `is_higher_taxon` | Unidentified morphospecies; row naming a taxon above species rank (e.g. larvae) |
| `symbols` | Footnote symbols printed next to the name (●, ♠, ♦, ♣, \*) |
| `name_notes` | Parser notes (e.g. `diacritic_in_latin`, `authorship_without_year`) |
| `src_phylum` … `src_family` | Higher taxa as printed in the hierarchy rows of the table (after repair of damaged names) |
| `status` | JSON object of conservation columns, e.g. `{"IUCN_2026": "VU", "DLDVN_2024": "VU"}`; keys follow each document's legend |
| `extra` | Additional printed columns (e.g. native range of alien species) |
| `campaigns` | Survey campaigns in which the taxon was recorded, where printed |
| `n_sites_marked`, `n_sites_present` | Number of site cells with a mark / with presence |
| `gbif_key`, `gbif_name`, `gbif_rank`, `gbif_status`, `gbif_accepted` | GBIF Backbone match; `gbif_accepted` is filled for synonyms |
| `gbif_match` | `exact`, `synonym`, `fuzzy`, `fuzzy_rejected`, `higherrank`, `none` |
| `gbif_confidence`, `gbif_pass` | GBIF confidence; 1 = first pass, 2 = resolved by the context-aware second pass |
| `gbif_kingdom` … `gbif_genus` | Classification returned by GBIF |
| `family_agrees`, `family_similarity` | Whether the printed family equals the GBIF family; string similarity of the two |

## site_presence.csv — presence/absence by site (2,871 rows)

| Column | Meaning |
|---|---|
| `source`, `idx` | Document code and row number (joins to `checklist_records.csv`) |
| `site` | Site code as used in the document (M1, M2, …) |
| `present` | `True` for presence, `False` for absence. Blank cells are recorded as absence only in AH_DVN, where the legend defines blank as absent |

## sites.csv — sampling sites with coordinates

| Column | Meaning |
|---|---|
| `source`, `waterbody`, `site` | Document, waterbody and site code in that document |
| `lat`, `lon` | Decimal degrees (WGS84), converted from the printed degrees/minutes/seconds |
| `site_uid` | Identifier after merging sites of the same waterbody that are less than 150 m apart |

## ayunha_abundance.csv — plankton abundance, Ayun Ha Reservoir (4,919 rows)

| Column | Meaning |
|---|---|
| `group` | `phytoplankton` (cells/L) or `zooplankton` (individuals/m³) |
| `campaign` | Survey month (YYYY-MM), March 2021 – November 2022 |
| `site` | Site code in the project appendix (M1–M11) |
| `raw_name`, `canonical`, `gbif_key`, `gbif_match` | Printed name, parsed name and GBIF resolution |
| `value` | Density; `-1` means the taxon was marked present without a count |
| `trait` | Trait printed in the appendix (`Tảo độc` = toxic, `Tảo gây hại` = harmful) |

## ayunha_water_quality.csv — water quality, Ayun Ha Reservoir (1,496 rows)

| Column | Meaning |
|---|---|
| `campaign`, `site` | Survey month and site code (M1–M11) |
| `parameter` | Parameter name and unit as printed (17 parameters, e.g. `Chl-a (ug/L)`, `DO (mg/L)`, `Photphat (mgP-PO4/L)`) |
| `value` | Measured value |

## Evaluation and query outputs

| File | Content |
|---|---|
| `eval_E1_E3_counts.csv` | Reported vs extracted numbers of species, genera, families and orders per document |
| `eval_E2_cells.csv` | Per-site species totals printed by the authors vs recomputed from extracted cells |
| `eval_E2b_status_columns.csv` | Species per conservation column or symbol: reported vs extracted |
| `eval_E4_resolution.csv`, `eval_E4_name_issues.csv` | GBIF resolution outcome per document; list of names with issues |
| `eval_E6_family_conflicts.csv`, `eval_E6_cross_source.csv` | Printed family vs GBIF family; taxa recorded in several documents with their assessments |
| `eval_E7_reconciliation_overlap.csv` | Sørensen similarity between waterbodies with verbatim vs reconciled names |
| `hierarchy_repairs.csv` | Damaged higher-taxon names and their restored form |
| `ablation_names.csv`, `ablation_cells.csv`, `ablation_merge_verbatim.csv` | Baselines and ablations |
| `extraction_meta.csv` | Number of glyph repairs and printed total rows per document |
| `cq_results/*.csv` | Results of the SPARQL queries in `biokg/queries/` |
| `gbif_cache.json` | Cached GBIF API responses used for name resolution |
