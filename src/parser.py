"""
Resume and Document Parser Module.

Extracts text from PDF, DOCX, and TXT files, and performs robust
NLP-oriented text cleaning and normalization to resolve multi-column
layout noise, broken line wraps, bullet merging, and preserve critical acronyms.
"""

import io
import re
import os
from typing import Union, BinaryIO, Optional


# Known acronyms to preserve exact casing during normalization
PROTECTED_ACRONYMS = {
    "AWS", "GCP", "API", "APIS", "REST", "SQL", "NOSQL", "NLP", "LLM", "LLMS", 
    "RAG", "BERT", "GPT", "CNN", "RNN", "LSTM", "ML", "DL", "AI", "CI/CD", 
    "CICD", "K8S", "ETL", "ELT", "TF-IDF", "TFIDF", "NER", "S3", "EC2", 
    "EKS", "ECS", "IAM", "GKE", "TDD", "OOP", "ORM", "CLI", "GPU", "CPU",
    "JSON", "XML", "HTML", "CSS", "CUDA", "WANDB", "MLOPS", "ONNX"
}


def extract_text_from_pdf(file_input: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a PDF file using PyMuPDF (fitz) with fallback to pypdf.
    Handles multi-column layout and text blocks.
    """
    text_content = []

    # 1. Try PyMuPDF
    try:
        import pymupdf  # PyMuPDF
        if isinstance(file_input, str):
            doc = pymupdf.open(file_input)
        elif isinstance(file_input, bytes):
            doc = pymupdf.open(stream=file_input, filetype="pdf")
        else:
            doc = pymupdf.open(stream=file_input.read(), filetype="pdf")
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            # Use 'blocks' sort to maintain natural reading order in multi-column layouts
            blocks = page.get_text("blocks", sort=True)
            for b in blocks:
                block_text = b[4].strip()
                if block_text:
                    text_content.append(block_text)
        doc.close()
        return "\n\n".join(text_content)
    except Exception as e:
        # 2. Fallback to pypdf
        try:
            from pypdf import PdfReader
            if isinstance(file_input, (str, bytes)):
                stream = io.BytesIO(file_input) if isinstance(file_input, bytes) else file_input
            else:
                stream = file_input
            reader = PdfReader(stream)
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text_content.append(extracted)
            return "\n\n".join(text_content)
        except Exception as fallback_e:
            raise RuntimeError(f"Failed to parse PDF using both PyMuPDF and pypdf: {e}; fallback error: {fallback_e}")


def extract_text_from_docx(file_input: Union[str, bytes, BinaryIO]) -> str:
    """
    Extracts text from a DOCX document using python-docx, including paragraphs and tables.
    """
    try:
        import docx
        if isinstance(file_input, (bytes, bytearray)):
            file_stream = io.BytesIO(file_input)
        elif hasattr(file_input, "read"):
            file_stream = file_input
        else:
            file_stream = file_input

        doc = docx.Document(file_stream)
        text_parts = []

        # Extract paragraphs
        for para in doc.paragraphs:
            clean_para = para.text.strip()
            if clean_para:
                text_parts.append(clean_para)

        # Extract tables (often used for skill matrices / experience columns)
        for table in doc.tables:
            for row in table.rows:
                row_cells = [cell.text.strip() for cell in row.cells if cell.text.strip()]
                if row_cells:
                    text_parts.append(" | ".join(row_cells))

        return "\n".join(text_parts)
    except Exception as e:
        raise RuntimeError(f"Failed to parse DOCX file: {e}")


def extract_text(file_input: Union[str, bytes, BinaryIO], filename: Optional[str] = None) -> str:
    """
    Auto-detects file format by extension or path and extracts plain text.
    """
    target_name = filename or (file_input if isinstance(file_input, str) else "")
    ext = os.path.splitext(target_name)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_input)
    elif ext in [".docx", ".doc"]:
        return extract_text_from_docx(file_input)
    else:
        # Plain text / fallback
        if isinstance(file_input, str):
            if os.path.exists(file_input):
                with open(file_input, "r", encoding="utf-8", errors="ignore") as f:
                    return f.read()
            return file_input
        elif isinstance(file_input, bytes):
            return file_input.decode("utf-8", errors="ignore")
        elif hasattr(file_input, "read"):
            data = file_input.read()
            if isinstance(data, bytes):
                return data.decode("utf-8", errors="ignore")
            return data
        return str(file_input)


def clean_text(raw_text: str) -> str:
    """
    Normalizes and cleans resume or job description text:
    - Resolves hyphenated words broken across line wraps (e.g., 'trans- \n former' -> 'transformer')
    - Standardizes bullet points and punctuation
    - Strips unwanted page numbers and footer clutter
    - Cleans redundant whitespace while preserving paragraph breaks
    - Preserves critical technical acronyms (AWS, GCP, CI/CD, SQL, etc.)
    """
    if not raw_text:
        return ""

    text = raw_text

    # 1. Normalize line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # 2. Fix broken hyphenated words at line wraps (e.g. "con- \n tainer" -> "container")
    text = re.sub(r'(\b[A-Za-z]+)-\s*\n\s*([A-Za-z]+\b)', r'\1\2', text)

    # 3. Standardize bullet characters to standard bullet marker with spacing
    bullet_patterns = r'[\u2022\u2023\u25E6\u2043\u2219\u25AA\u25AB\u25BA\u27A2\u2713\u2714\u25CF\u25CB\u25CD\u25CE\u25CF\*\-\–\—]\s+'
    text = re.sub(bullet_patterns, '\n• ', text)

    # 4. Remove common PDF header/footer artifacts like "Page 1 of 4", "Page 2"
    text = re.sub(r'(?i)\bpage\s+\d+(\s+of\s+\d+)?\b', '', text)

    # 5. Remove isolated standalone digit lines (page numbers)
    text = re.sub(r'(?m)^\s*\d+\s*$', '', text)

    # 6. Replace excessive whitespace and tabs within lines
    text = re.sub(r'[ \t]+', ' ', text)

    # 7. Collapse more than two consecutive newlines into double newlines
    text = re.sub(r'\n{3,}', '\n\n', text)

    # 8. Clean trailing/leading spaces on lines
    cleaned_lines = [line.strip() for line in text.split('\n')]
    cleaned_text = "\n".join(cleaned_lines).strip()

    return cleaned_text
