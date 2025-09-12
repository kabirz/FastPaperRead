import pdfplumber

with pdfplumber.open("1706.03762v7.pdf") as pdf:
    first_page = pdf.pages[0]
    print(first_page.chars[0])
    

#提取全部文字
def extract_text_allpage (filepath):
 
    pdf = pdfplumber.open(filepath)
 
    for page in pdf.pages:
        print(page.extract_text())
        
extract_text_allpage("1706.03762v7.pdf")