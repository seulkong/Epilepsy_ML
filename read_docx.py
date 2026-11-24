import sys
try:
    import docx2txt
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "docx2txt"])
    import docx2txt

text = docx2txt.process("이슬빈 논문 초안 - 복사.docx")
print(text)
