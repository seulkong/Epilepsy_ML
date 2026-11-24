import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml

doc = docx.Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = Inches(0.984)
section.bottom_margin = Inches(0.984)
section.left_margin = Inches(0.984)
section.right_margin = Inches(0.984)

EQ_HEIGHTS = {
    1: 0.40,
    2: 0.40,
    3: 0.24,
    4: 0.25,
    5: 0.42,
    6: 0.32,
    7: 0.40,
    8: 0.38,
    9: 0.24,
    10: 0.38,
    11: 0.24,
    12: 0.24,
    13: 0.38,
    14: 0.48
}

def add_universal_equation(eq_num):
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    tblBorders = parse_xml(
        '<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>'
        '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(tblBorders)
    
    row = tbl.rows[0]
    
    # 좌측 셀: 수식 이미지 (가운데 정렬)
    cell_math = row.cells[0]
    cell_math.width = Inches(5.5)
    p_math = cell_math.paragraphs[0]
    p_math.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_math.paragraph_format.space_before = Pt(4)
    p_math.paragraph_format.space_after = Pt(4)
    p_math.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    
    img_path = f'equations_img/eq_{eq_num}.png'
    h = EQ_HEIGHTS.get(eq_num, 0.35)
    run_img = p_math.add_run()
    run_img.add_picture(img_path, height=Inches(h))
    
    # 우측 셀: 수식 번호 (우측 정렬)
    cell_num = row.cells[1]
    cell_num.width = Inches(0.8)
    p_num = cell_num.paragraphs[0]
    p_num.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(4)
    p_num.paragraph_format.space_after = Pt(4)
    p_num.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run_num = p_num.add_run(f"({eq_num})")
    run_num.bold = True
    run_num.font.size = Pt(11)

p_intro = doc.add_paragraph("유니버설 호환 수식 14개 테스트:")
for i in range(1, 15):
    p_t = doc.add_paragraph(f"수식 ({i}) 설명 텍스트...")
    add_universal_equation(i)

doc.save("test_universal_equations.docx")
print("Saved test_universal_equations.docx")
