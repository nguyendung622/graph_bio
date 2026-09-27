"""Create template_en.html from template.html by fixed string replacements (the Vietnamese file is not modified)."""
from pathlib import Path

HERE = Path(__file__).resolve().parent
R = [
    ("<title>BioKG Gia Lai</title>", "<title>BioKG Gia Lai (EN)</title>"),
    ("<h1>Đồ thị tri thức đa dạng sinh học thủy sinh Gia Lai</h1>", "<h1>Gia Lai Aquatic Biodiversity Knowledge Graph</h1>"),
    ('<p class="sub">Hồ Ayun Hạ, hồ thủy điện Ialy, sông Sê San và Biển Hồ. Dữ liệu lấy từ tệp <code>gialai_biokg.ttl</code> do quy trình BioKG tạo ra từ 10 tài liệu gốc.</p>',
     '<p class="sub">Ayun Ha Reservoir, Ialy Reservoir, Se San River and Bien Ho Lake. Data are read from <code>gialai_biokg.ttl</code>, produced by the BioKG pipeline from 10 source documents.</p>'),
    (">Khám phá đồ thị</button>", ">Explore</button>"),
    (">Truy vấn SPARQL</button>", ">SPARQL queries</button>"),
    (">Mô hình dữ liệu</button>", ">Data model</button>"),
    ('<label for="q">Tìm theo tên khoa học, tên Việt, mã tài liệu', '<label for="q">Search by scientific name, Vietnamese name or document code'),
    ('placeholder="ví dụ: Microcystis, cá chép, IALY_CA"', 'placeholder="e.g. Microcystis, cá chép, IALY_CA"'),
    ('<label for="ftype">Loại nút', '<label for="ftype">Node type'),
    ('<option value="">Tất cả</option>', '<option value="">All</option>'),
    ('<option value="NameUsage">Lượt dùng tên</option>', '<option value="NameUsage">Name usage</option>'),
    ('<option value="SourceDocument">Tài liệu</option>', '<option value="SourceDocument">Source document</option>'),
    ('<option value="Waterbody">Thủy vực</option>', '<option value="Waterbody">Waterbody</option>'),
    ('<option value="SamplingSite">Điểm thu mẫu</option>', '<option value="SamplingSite">Sampling site</option>'),
    ('<option value="ConservationAssessment">Đánh giá bảo tồn</option>', '<option value="ConservationAssessment">Conservation assessment</option>'),
    ('<label for="fwater">Thủy vực (áp dụng cho lượt dùng tên)', '<label for="fwater">Waterbody (applies to name usages)'),
    ('> Chỉ tên cần chuyên gia thẩm định</label>', '> Only names flagged for expert review</label>'),
    ('> Mở rộng 2 bước</label>', '> Expand to 2 hops</label>'),
    ('aria-label="Các nút liên kết với nút đang chọn"', 'aria-label="Nodes linked to the selected node"'),
    ('Bấm vào một nút để chọn. Kéo để di chuyển. Cạnh <code>presentAt</code> gộp từ các nút SiteOccurrence có trạng thái "present".',
     'Click a node to select it; drag to move. <code>presentAt</code> edges are derived from SiteOccurrence nodes with status "present".'),
    ("<h2>Lược đồ</h2>", "<h2>Schema</h2>"),
    ('<p>Mỗi hàng trong bảng danh lục trở thành một nút <code>NameUsage</code> (lượt dùng tên). Nút này nối tới tài liệu gốc, tới thủy vực, và tới một <code>dwc:Taxon</code> mang IRI của GBIF. Đánh giá bảo tồn là nút riêng, ghi hệ thống đánh giá, phiên bản và tài liệu nêu đánh giá. Số liệu mật độ và chất lượng nước là các <code>sosa:Observation</code> gắn với điểm thu mẫu và đợt khảo sát.</p>',
     '<p>Each checklist row becomes a <code>NameUsage</code> node (the name as printed). It links to its source document, its waterbody and a <code>dwc:Taxon</code> identified by a GBIF IRI. Each conservation assessment is a separate node recording the scheme, its version and the asserting document. Abundance and water-quality values are <code>sosa:Observation</code> nodes attached to a sampling site and a survey campaign.</p>'),
    ("<h2>Các nút không vẽ trong tab Khám phá</h2>", "<h2>Nodes not drawn in the Explore tab</h2>"),
    ("<p>Ba loại nút dưới đây có số lượng lớn nên chỉ được tóm tắt trong phần chi tiết của nút liên quan. Đây là một bản ghi thật của mỗi loại.</p>",
     "<p>These three node types are too numerous to draw and are summarised in the detail panel of related nodes. One real record of each type is shown.</p>"),
    ("NameUsage:{vi:'Lượt dùng tên'", "NameUsage:{vi:'Name usage'"),
    ("SourceDocument:{vi:'Tài liệu'", "SourceDocument:{vi:'Source document'"),
    ("Waterbody:{vi:'Thủy vực'", "Waterbody:{vi:'Waterbody'"),
    ("SamplingSite:{vi:'Điểm thu mẫu'", "SamplingSite:{vi:'Sampling site'"),
    ("ConservationAssessment:{vi:'Đánh giá bảo tồn'", "ConservationAssessment:{vi:'Conservation assessment'"),
    ("const ISSUE = {misspelling:'Sai chính tả', outdated_name:'Tên đồng nghĩa', family_conflict:'Họ khác GBIF',\n  unresolved:'Chưa phân giải', homonym_resolved:'Trùng tên, phân giải nhờ ngữ cảnh', no_site_data:'Thiếu dữ liệu điểm'};",
     "const ISSUE = {misspelling:'Misspelling', outdated_name:'Synonym', family_conflict:'Family differs from GBIF',\n  unresolved:'Unresolved', homonym_resolved:'Homonym resolved by context', no_site_data:'No site data'};"),
    ("const TRAIT = {EconomicValue:'Giá trị kinh tế', AquacultureValue:'Nuôi thương phẩm', OrnamentalValue:'Nuôi cảnh',\n  AlienSpecies:'Loài ngoại lai', InvasiveAlienSpecies:'Ngoại lai xâm hại', PotentialInvasiveSpecies:'Có nguy cơ xâm hại',\n  WidespreadInvasiveSpecies:'Xâm hại diện rộng', ToxicCyanobacterium:'Tảo độc', HarmfulAlga:'Tảo gây hại'};",
     "const TRAIT = {EconomicValue:'Economic value', AquacultureValue:'Aquaculture', OrnamentalValue:'Ornamental',\n  AlienSpecies:'Alien species', InvasiveAlienSpecies:'Invasive alien', PotentialInvasiveSpecies:'Potentially invasive',\n  WidespreadInvasiveSpecies:'Widespread invasive', ToxicCyanobacterium:'Toxic cyanobacterium', HarmfulAlga:'Harmful alga'};"),
    ("const MATCH = {exact:'Khớp chính xác', synonym:'Tên đồng nghĩa', fuzzy:'Khớp gần đúng', fuzzy_rejected:'Khớp gần đúng, bị loại',\n  higherrank:'Chỉ khớp bậc cao', none:'Không khớp'};",
     "const MATCH = {exact:'Exact match', synonym:'Synonym', fuzzy:'Fuzzy match', fuzzy_rejected:'Fuzzy match, rejected',\n  higherrank:'Higher rank only', none:'No match'};"),
    ("const SRC = {AH_TVN:'Ayun Hạ – thực vật nổi', AH_DVN:'Ayun Hạ – động vật nổi', AH_DVD:'Ayun Hạ – động vật đáy',\n  AH_CA:'Ayun Hạ – cá', AH_CTN:'Ayun Hạ – côn trùng nước', AH_NL:'Ayun Hạ – sinh vật ngoại lai',\n  SESAN_CA:'Sê San – cá', IALY_CA:'Ialy – cá', BH_DVD:'Biển Hồ – động vật đáy', AH_PL:'Ayun Hạ – phụ lục đề tài'};",
     "const SRC = {AH_TVN:'Ayun Ha – phytoplankton', AH_DVN:'Ayun Ha – zooplankton', AH_DVD:'Ayun Ha – zoobenthos',\n  AH_CA:'Ayun Ha – fish', AH_CTN:'Ayun Ha – aquatic insects', AH_NL:'Ayun Ha – alien species',\n  SESAN_CA:'Se San – fish', IALY_CA:'Ialy – fish', BH_DVD:'Bien Ho – zoobenthos', AH_PL:'Ayun Ha – project appendix'};\n"
     "const WB = {'Hồ Ayun Hạ':'Ayun Ha Reservoir', 'Hồ TĐ Ialy':'Ialy Reservoir', 'Sông Sê San':'Se San River', 'Biển Hồ':'Bien Ho Lake'};\n"
     "const WBK = {'Hồ chứa thủy lợi':'Irrigation reservoir', 'Hồ chứa thủy điện':'Hydropower reservoir', 'Sông':'River', 'Hồ tự nhiên (miệng núi lửa)':'Natural crater lake'};\n"
     "for (const n of D.nodes) if (n.type==='Waterbody'){ n.label = WB[n.label] || n.label; n.kind = WBK[n.kind] || n.kind; }"),
    ("const nf = new Intl.NumberFormat('vi-VN');", "const nf = new Intl.NumberFormat('en-US');"),
    ("['bộ ba', S.triples], ['lượt dùng tên', S.NameUsage], ['taxon', S.Taxon], ['điểm thu mẫu', S.SamplingSite],\n  ['đánh giá bảo tồn', S.ConservationAssessment], ['có/không theo điểm', S.SiteOccurrence],\n  ['quan trắc mật độ', S.AbundanceObservation], ['quan trắc chất lượng nước', S.WaterQualityObservation]",
     "['triples', S.triples], ['name usages', S.NameUsage], ['taxa', S.Taxon], ['sampling sites', S.SamplingSite],\n  ['conservation assessments', S.ConservationAssessment], ['site presence/absence', S.SiteOccurrence],\n  ['abundance observations', S.AbundanceObservation], ['water-quality observations', S.WaterQualityObservation]"),
    ("`${nf.format(rows.length)} nút${rows.length>300?' (hiện 300 đầu)':''}`", "`${nf.format(rows.length)} nodes${rows.length>300?' (first 300 shown)':''}`"),
    ("`<span class=\"count\">và ${ids.length-40} nút khác</span>`", "`<span class=\"count\">and ${ids.length-40} more</span>`"),
    ("kv = [['Tên in trong bảng', n.verbatim], ['Tên Việt', n.vn||'—'], ['Tài liệu', `${n.source} (${SRC[n.source]||''})`],\n          ['Thủy vực', waterOf(n)], ['Kết quả đối sánh GBIF', MATCH[n.match]||n.match]];",
     "kv = [['Name as printed', n.verbatim], ['Vietnamese name', n.vn||'—'], ['Source', `${n.source} (${SRC[n.source]||''})`],\n          ['Waterbody', waterOf(n)], ['GBIF match', MATCH[n.match]||n.match]];"),
    ("<h3>Có/không theo điểm (${s.length} nút SiteOccurrence)</h3>", "<h3>Presence/absence by site (${s.length} SiteOccurrence nodes)</h3>"),
    ("<th>Điểm</th><th>Mã trong tài liệu</th><th>Trạng thái</th>", "<th>Site</th><th>Code in source</th><th>Status</th>"),
    ("${st==='present'?'có':'không'}", "${st==='present'?'present':'absent'}"),
    ("kv = [['Bậc', n.rank||'—'], ['Họ (GBIF)', n.family||'—'], ['IRI', shortId(n.id)]];", "kv = [['Rank', n.rank||'—'], ['Family (GBIF)', n.family||'—'], ['IRI', shortId(n.id)]];"),
    ("<h3>Mật độ cao nhất ở hồ Ayun Hạ (${nf.format(n.abundance.n)} quan trắc)</h3>", "<h3>Highest abundance in Ayun Ha Reservoir (${nf.format(n.abundance.n)} observations)</h3>"),
    ("<th>Đợt</th><th>Điểm</th><th class=\"num\">Giá trị</th><th>Đơn vị</th>", "<th>Campaign</th><th>Site</th><th class=\"num\">Value</th><th>Unit</th>"),
    ("kv = [['Nội dung', SRC[n.label]||''], ['Nhóm sinh vật', n.group], ['Trích dẫn', n.cite]];", "kv = [['Content', SRC[n.label]||''], ['Taxonomic group', n.group], ['Citation', n.cite]];"),
    ("kv = [['Loại', n.kind]];", "kv = [['Type', n.kind]];"),
    ("kv = [['Vĩ độ, kinh độ', `${n.lat.toFixed(5)}, ${n.lon.toFixed(5)}`], ['Mã trong các tài liệu', n.codes.join(', ')],\n          ['Quan trắc mật độ', nf.format(n.n_abundance||0)], ['Quan trắc chất lượng nước', nf.format(n.n_wq||0)]];",
     "kv = [['Latitude, longitude', `${n.lat.toFixed(5)}, ${n.lon.toFixed(5)}`], ['Codes in sources', n.codes.join(', ')],\n          ['Abundance observations', nf.format(n.n_abundance||0)], ['Water-quality observations', nf.format(n.n_wq||0)]];"),
    ("<h3>Liên kết</h3>", "<h3>Links</h3>"),
    ("'<span class=\"count\">Không có</span>'", "'<span class=\"count\">None</span>'"),
    ("Bộ ba RDF của nút (Turtle)", "RDF triples of this node (Turtle)"),
    ("id=\"copy\">Sao chép</button>", "id=\"copy\">Copy</button>"),
    ("b.textContent = 'Đã sao chép'; setTimeout(()=>b.textContent='Sao chép',1500);", "b.textContent = 'Copied'; setTimeout(()=>b.textContent='Copy',1500);"),
    ("b.textContent = 'Đã chọn văn bản, nhấn Ctrl/Cmd+C';", "b.textContent = 'Text selected, press Ctrl/Cmd+C';"),
    ("cq1_richness:['Số taxon theo thủy vực và nhóm sinh vật','Đếm lượt dùng tên (không tính loài chưa định danh) và số tên đã chuẩn hóa khác nhau ở mỗi thủy vực.']",
     "cq1_richness:['Taxa per waterbody and group','Counts name usages (excluding unidentified morphospecies) and distinct reconciled names in each waterbody.']"),
    ("cq2_shared:['Loài chung giữa các thủy vực','Các loài cùng nhóm sinh vật có mặt ở hai thủy vực, so sánh bằng tên đã chuẩn hóa theo GBIF.']",
     "cq2_shared:['Species shared between waterbodies','Species of the same taxonomic group recorded in two waterbodies, compared by GBIF-reconciled names.']"),
    ("cq3_threatened:['Loài bị đe dọa','Loài được xếp CR, EN hoặc VU theo bất kỳ hệ thống đánh giá nào, kèm tài liệu nêu đánh giá.']",
     "cq3_threatened:['Threatened species','Species listed as CR, EN or VU under any assessment scheme, with the asserting document.']"),
    ("cq4_invasive_spread:['Loài ngoại lai có mặt ở đâu','Loài được một tài liệu đánh dấu là ngoại lai hoặc xâm hại, và các thủy vực khác có ghi nhận loài đó.']",
     "cq4_invasive_spread:['Where alien species occur','Species flagged as alien or invasive in one document, and the other waterbodies where they are recorded.']"),
    ("cq5_toxic_algae_env:['Tảo độc và chất lượng nước','Mật độ tảo độc cao nhất theo điểm và đợt ở hồ Ayun Hạ, kèm Chl-a, PO₄, NH₄ và độ trong đo cùng điểm, cùng đợt.']",
     "cq5_toxic_algae_env:['Toxic cyanobacteria and water quality','Highest toxic cyanobacteria densities by site and campaign in Ayun Ha Reservoir, with Chl-a, PO₄, NH₄ and transparency measured at the same site and campaign.']"),
    ("cq6_curation_queue:['Tên cần chuyên gia thẩm định','Số tên có vấn đề theo từng tài liệu và loại vấn đề.']",
     "cq6_curation_queue:['Names flagged for expert review','Number of flagged names per document and issue type.']"),
    ("cq7_assessment_conflicts:['Đánh giá bảo tồn khác nhau','Loài được các tài liệu xếp hạng khác nhau trong cùng một hệ thống đánh giá.']",
     "cq7_assessment_conflicts:['Conflicting conservation assessments','Species given different categories under the same scheme in different documents.']"),
    ("cq8_checklist_vs_matrix:['Danh lục và ma trận phụ lục','Loài có trong bài thực vật nổi nhưng không xuất hiện trong ma trận mật độ 8 đợt của phụ lục. Kết quả rỗng nghĩa là hai nguồn nhất quán.']",
     "cq8_checklist_vs_matrix:['Checklist versus appendix matrix','Species in the phytoplankton paper that never occur in the 8-campaign abundance matrix of the appendix. An empty result means the two sources agree.']"),
    ("<small>${esc(x.name)}.rq · ${x.rows.length} dòng</small>", "<small>${esc(x.name)}.rq · ${x.rows.length} rows</small>"),
    ("<summary>Xem câu truy vấn SPARQL</summary>", "<summary>Show SPARQL query</summary>"),
    ("'<p style=\"padding:12px\">Không có dòng nào.</p>'", "'<p style=\"padding:12px\">No rows.</p>'"),
    ("(${nf.format(D.stats[k])} nút)</h3>", "(${nf.format(D.stats[k])} nodes)</h3>"),
    ("const cell = c => esc(String(c).replace('https://biokg.example.org/gialai/resource/source/','').replace('source/',''));",
     "const cell = c => { let t = String(c).replace('https://biokg.example.org/gialai/resource/source/','').replace('source/','');\n    for (const [vi,en] of Object.entries(WB)) t = t.split(vi).join(en); return esc(t); };"),
]


def main():
    s = (HERE / "template.html").read_text(encoding="utf-8")
    missing = [a[:60] for a, _ in R if a not in s]
    if missing:
        raise SystemExit("not found: " + " | ".join(missing))
    for a, b in R:
        s = s.replace(a, b)
    (HERE / "template_en.html").write_text(s, encoding="utf-8")
    import re
    left = [l.strip()[:90] for l in s.splitlines() if re.search(r"[ạảấầẩẫậắằẳẵặẹẻẽếềểễệỉịọỏốồổỗộớờởỡợụủứừửữựỳỵỷỹđ]", l)]
    print("lines still containing Vietnamese:", len(left))
    for l in left:
        print("  ", l)


if __name__ == "__main__":
    main()
