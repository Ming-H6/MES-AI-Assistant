import re
from docx import Document


#Read documents
def read_docx(file_path):
    doc = Document(file_path)

    text= []

    for para in doc.paragraphs:
        if para.text.strip():
            text.append(para.text)
    return text


def parse_docx(file_path):
    content = read_docx(file_path)


    current_customer = None
    current_section = None
    current_subject = None
    current_content = []
    chunks = []
    
    def save_current_chunk():
          chunk ={
          "Customer":current_customer,
          "Section":current_section,
          "Subject":current_subject,
          "Content":current_content.copy()
          }
          chunks.append(chunk)

    for para in content:
        para = para.strip()

        matchObj = re.match(r'(\d+(?:\.\d+)*)\s+(.*)',para,re.M|re.I)

        if matchObj:
            number = matchObj.group(1)
            title = matchObj.group(2)
            levels = len(number.split('.'))
            if levels == 2:    
                    if current_subject is not None:
                        save_current_chunk()
                    current_customer = title
                    current_section = None
                    current_subject = None
                    current_content = []

            elif levels == 3:   
                    if current_subject is not None:
                        save_current_chunk()  
                    current_section = number
                    current_subject = title 
                    current_content = []
        else:
            if para:
                current_content.append(para)
    if current_subject is not None:
        save_current_chunk()     

    return chunks
