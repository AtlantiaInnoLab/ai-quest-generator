import docx
import PyPDF2
from io import BytesIO

class DocumentProcessor:
    """Maneja la extracción de texto de diferentes tipos de documentos"""
    
    def extract_text(self, file):
        """Extrae texto según el tipo de archivo"""
        if file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            return self._extract_from_docx(file)
        elif file.type == "application/pdf":
            return self._extract_from_pdf(file)
        elif file.type == "text/plain":
            return self._extract_from_txt(file)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {file.type}")
    
    def _extract_from_docx(self, file):
        """Extrae texto de archivo DOCX"""
        doc = docx.Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_from_pdf(self, file):
        """Extrae texto de archivo PDF"""
        reader = PyPDF2.PdfReader(file)
        return "".join([page.extract_text() or "" for page in reader.pages])
    
    def _extract_from_txt(self, file):
        """Extrae texto de archivo TXT"""
        return file.getvalue().decode('utf-8')