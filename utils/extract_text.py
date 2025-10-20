import fitz  # PyMuPDF
import docx

def extract_text_from_resume(filepath):
    # Check file type and extract text accordingly
    if filepath.endswith(".pdf"):
        doc = fitz.open(filepath)
        return "\n".join([page.get_text() for page in doc])
    elif filepath.endswith(".docx"):
        doc = docx.Document(filepath)
        return "\n".join([para.text for para in doc.paragraphs])
    else:
        return "Unsupported file format."
