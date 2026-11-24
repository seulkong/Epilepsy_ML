import docx
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

doc = docx.Document()
p = doc.add_paragraph("수식 테스트입니다:")

# OMML XML 생성
math_xml = (
    '<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">'
    '<m:oMath>'
    '<m:sSub><m:e><m:r><m:t>R</m:t></m:r></m:e><m:sub><m:r><m:t>res</m:t></m:r></m:sub></m:sSub>'
    '<m:r><m:t> = </m:t></m:r>'
    '<m:sSub><m:e><m:r><m:rPr><m:nor/></m:rPr><m:t>max</m:t></m:r></m:e>'
    '<m:sub><m:r><m:t>j ∈ K</m:t></m:r><m:sSub><m:e><m:r></m:r></m:e><m:sub><m:r><m:t>res</m:t></m:r></m:sub></m:sSub></m:sub></m:sSub>'
    '<m:r><m:t> </m:t></m:r>'
    '<m:sSub><m:e>'
    '<m:d><m:dPr><m:begChr m:val="‖"/><m:endChr m:val="‖"/><m:grow/></m:dPr>'
    '<m:e>'
    '<m:r><m:rPr><m:b/></m:rPr><m:t>p</m:t></m:r>'
    '<m:sSub><m:e><m:r></m:r></m:e><m:sub><m:r><m:t>j</m:t></m:r></m:sub></m:sSub>'
    '<m:r><m:t> - </m:t></m:r>'
    '<m:sSub><m:e><m:r><m:t>C</m:t></m:r></m:e><m:sub><m:r><m:t>res</m:t></m:r></m:sub></m:sSub>'
    '</m:e></m:d>'
    '</m:e>'
    '<m:sub><m:r><m:t>2</m:t></m:r></m:sub>'
    '</m:sSub>'
    '</m:oMath>'
    '</m:oMathPara>'
)

p_math = doc.add_paragraph()
p_math._p.append(parse_xml(math_xml))

doc.save("test_equation.docx")
print("Saved test_equation.docx")
