import zipfile
import xml.etree.ElementTree as ET
import os

def read_docx_text(path):
    if not os.path.exists(path):
        return "File not found."
    
    try:
        with zipfile.ZipFile(path) as z:
            xml_content = z.read('word/document.xml')
        
        root = ET.fromstring(xml_content)
        namespace = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        
        text = []
        for para in root.findall('.//w:p', namespace):
            t_elements = para.findall('.//w:t', namespace)
            if t_elements:
                para_text = "".join([t.text for t in t_elements if t.text])
                text.append(para_text)
        
        return "\n".join(text)
    except Exception as e:
        return f"Error reading docx: {str(e)}"

if __name__ == "__main__":
    docx_path = r"c:\Nam 3 ki 2\Thực tập cơ sở\Dataset\ĐàmChiếnThắng_Đỗ Quốc Tấn_Xây dựng hệ thống phân tầng mức độ rủi ro học tập của sinh viên.docx"
    content = read_docx_text(docx_path)
    # Print first 5000 characters to get the main parts
    print(content[:5000])
