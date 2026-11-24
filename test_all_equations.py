import docx
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
import omml_equations as OEQ

doc = docx.Document()
section = doc.sections[0]
section.page_width = Inches(8.27)
section.page_height = Inches(11.69)
section.top_margin = Inches(0.984)
section.bottom_margin = Inches(0.984)
section.left_margin = Inches(0.984)
section.right_margin = Inches(0.984)

def add_native_equation(eq_number):
    omml_body = OEQ.get_equation_omml(eq_number)
    
    # 1행 2열 무테두리 테이블 생성 (수식 가운데 정렬, 번호 우측 정렬)
    tbl = doc.add_table(rows=1, cols=2)
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl.autofit = False
    
    # 테이블 테두리 제거 (투명 테이블)
    tblBorders = parse_xml(
        '<w:tblBorders xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        '<w:top w:val="none"/><w:left w:val="none"/><w:bottom w:val="none"/><w:right w:val="none"/>'
        '<w:insideH w:val="none"/><w:insideV w:val="none"/>'
        '</w:tblBorders>'
    )
    tbl._tbl.tblPr.append(tblBorders)
    
    row = tbl.rows[0]
    
    # 좌측 셀: 수식 (너비 약 5.5인치, 가운데 정렬)
    cell_math = row.cells[0]
    cell_math.width = Inches(5.5)
    p_math = cell_math.paragraphs[0]
    p_math.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_math.paragraph_format.space_before = Pt(3)
    p_math.paragraph_format.space_after = Pt(3)
    p_math.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    
    # Word 네이티브 수식 XML 삽입
    math_xml = (
        f'<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
        f'<m:oMath>{omml_body}</m:oMath>'
        f'</m:oMathPara>'
    )
    p_math._p.append(parse_xml(math_xml))
    
    # 우측 셀: 수식 번호 (너비 약 0.8인치, 우측 정렬)
    cell_num = row.cells[1]
    cell_num.width = Inches(0.8)
    p_num = cell_num.paragraphs[0]
    p_num.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_num.paragraph_format.space_before = Pt(3)
    p_num.paragraph_format.space_after = Pt(3)
    p_num.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    run_num = p_num.add_run(f"({eq_number})")
    run_num.bold = True
    run_num.font.size = Pt(11)

p_intro = doc.add_paragraph("MS Word 네이티브 수식 14개 테스트:")

for i in range(1, 15):
    doc.add_paragraph(f"수식 ({i}):")
    add_native_equation(i)

doc.save("test_all_14_equations.docx")
print("Saved test_all_14_equations.docx successfully!")
