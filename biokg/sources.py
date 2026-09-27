"""Registry of Gia Lai source documents.

Each entry describes where the species checklist lives inside the document and
the summary counts the authors report (used for automatic reconciliation).
"""
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "DataSource"

# Conservation-status columns, keyed by the column marker used in the source table.
SESAN_STATUS = {"(1)": "IUCN_2026", "(2)": "CITES_2026", "(3)": "DLDVN_2024", "(4)": "ND37_2024"}
AYUNHA_FISH_STATUS = {"5": "specimen", "6": "interview", "7": "SDVN_2007", "8": "IUCN_2022", "9": "CITES_2021",
                      "10*": "QD82_2008"}
IALY_STATUS = {"(1)": "ND26_2019", "(2)": "CITES_2026", "(3)": "DLDVN_2024", "(4)": "IUCN_2025"}

SOURCES = [
    dict(id="AH_TVN", file="Thực vật nổi hồ Ayun Hạ.pdf.pdf", kind="pdf",
         waterbody="Hồ Ayun Hạ", group="phytoplankton", year=2022,
         cite="Huỳnh Vũ Ngọc Quý, Hoàng Đình Trung và cs. (2022), VAP 5, doi:10.15625/vap.2022.0042",
         table=r"Bảng 2\. Danh sách thành phần loài thực vật nổi", site_prefix="M",
         reported=dict(species=79, genus=38, family=26, order=19, klass=10, phylum=7, sites=10)),
    dict(id="AH_DVN", file="Động vật nổi hồ Ayun Hạ.pdf.pdf", kind="pdf",
         waterbody="Hồ Ayun Hạ", group="zooplankton", year=2022,
         cite="Hoàng Đình Trung, Trần Vĩnh Hoàng (2022), VAP 5, doi:10.15625/vap.2022.0027",
         table=r"Bảng 2\. Thành phần loài động vật nổi", site_prefix="M", render="bbox",
         blank_means_absent=True,  # this table marks presence with "x" and leaves absence blank
         reported=dict(species=55, genus=27, family=21, sites=11)),
    dict(id="AH_DVD", file="6. Sinh - Hoang Dinh Trung (tập 23, số 02).pdf", kind="pdf",
         waterbody="Hồ Ayun Hạ", group="zoobenthos", year=2023,
         cite="Hoàng Đình Trung (2023), TC KH&CN ĐHKH Huế 23(2)",
         table=r"Bảng 2\. Danh lục thành phần loài động vật đáy", site_prefix="M",
         reported=dict(species=37, genus=24, family=13, order=6, klass=6, phylum=3, sites=9)),
    dict(id="AH_CA", file="2-Trung-6930-Edited-Final-Tr17-28 (cá hồ Ayun Hạ).pdf", kind="pdf",
         waterbody="Hồ Ayun Hạ", group="fish", year=2023,
         cite="Hoàng Đình Trung, Nguyễn Duy Thuận (2023), TC KH ĐH Huế: KHTN 132(1A):17-28",
         table=r"Bảng 2\. Danh lục thành phần loài cá", status_cols=AYUNHA_FISH_STATUS,
         symbol_legend={"●": "economic", "♠": "aquaculture", "♦": "ornamental", "♣": "alien"},
         symbol_abstract={"economic": 21, "aquaculture": 15, "ornamental": 14},
         status_footer={"specimen": 27, "interview": 7, "SDVN_2007": 1, "IUCN_2022": 14, "CITES_2021": 1,
                        "QD82_2008": 1},
         reported=dict(species=33, genus=31, family=20, order=9)),
    dict(id="AH_CTN", file="DẪN LIỆU BƯỚC ĐẦU VỀ THÀNH PHẦN LOÀI CÔN TRÙNG NƯỚC Ở HỒ AYUN HẠ (30.1.2023).docx",
         kind="docx", waterbody="Hồ Ayun Hạ", group="aquatic_insects", year=2023,
         cite="Hoàng Đình Trung (2023), bản thảo côn trùng nước hồ Ayun Hạ",
         table_index=1, reported=dict(species=73, genus=65, family=33, order=7, sites=9)),
    dict(id="AH_NL", file="Sinh vật ngoại lai xâm hại hồ Ayun Hạ.pdf.pdf", kind="pdf",
         waterbody="Hồ Ayun Hạ", group="invasive_alien", year=2022,
         cite="Hoàng Đình Trung (2022), VAP 5, doi:10.15625/vap.2022.0005",
         table=r"Bảng 2\. Danh sách loài SVNLXH",
         status_cols={"A": "invasive", "B": "potential_invasive", "C": "widespread_invasive"},
         status_abstract={"invasive": 10, "potential_invasive": 4},
         reported=dict(species=14, genus=13, family=11, order=10, phylum=4)),
    dict(id="SESAN_CA", file="Đa dạng thành phần loài cá ở sông Sê San (bản cuối chấp nhận đăng).docx",
         kind="docx", waterbody="Sông Sê San", group="fish", year=2026,
         cite="Hoàng Đình Trung và cs. (2026), bài chấp nhận đăng: Đa dạng thành phần loài cá ở sông Sê San",
         table_index=1, status_cols=SESAN_STATUS, reported=dict(species=110, genus=66, family=24, order=8),
         status_abstract={"DLDVN_2024": 13, "ND37_2024": 14, "IUCN_2026_nonLC": 17}),
    dict(id="IALY_CA", file="CB24.Hoang Dinh Trung.17.7.pdf", kind="pdf",
         waterbody="Hồ TĐ Ialy", group="fish", year=2026,
         cite="Hoàng Đình Trung, Ngô Thị Bảo Châu (2026), VAP 7, doi:10.15625/vap.2026.0083",
         table=r"Bảng 1\. Danh sách thành phần loài cá", status_cols=IALY_STATUS,
         reported=dict(species=109, genus=67, family=22, order=9),
         reported_table_footer=dict(species=109, genus=69, family=22, order=9),
         status_footer={"ND26_2019": 15, "CITES_2026": 0, "DLDVN_2024": 2, "IUCN_2025": 5}),
    dict(id="BH_DVD", file="CB23.Hoang Dinh Trung.25.6.pdf", kind="pdf",
         waterbody="Biển Hồ", group="zoobenthos", year=2026,
         cite="Hoàng Đình Trung, Ngô Thị Bảo Châu, Biện Văn Quyền (2026), VAP 7, doi:10.15625/vap.2026.0082",
         table=r"Bảng 2\. Danh sách thành phần loài động vật đáy", site_prefix="M",
         reported=dict(species=71, genus=63, family=38, order=13, klass=6, phylum=3, sites=7)),
]

# Quantitative plankton matrices (species x site x campaign) from the Gia Lai project appendix.
APPENDIX = dict(id="AH_PL", file="PHỤ LỤC Đề tài Gia Lai.docx", kind="docx", waterbody="Hồ Ayun Hạ",
                cite="Phụ lục đề tài KH&CN tỉnh Gia Lai: ĐDSH hồ Ayun Hạ (2021-2022)")
