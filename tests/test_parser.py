"""
Tests for Document Parser and Text Normalizer.
"""

import os
import pytest
from src.parser import clean_text, extract_text, extract_text_from_pdf, extract_text_from_docx


def test_clean_text_normalizes_whitespace():
    raw = "Senior   Data  Scientist\n\n\n\nExperienced   with   NLP."
    cleaned = clean_text(raw)
    assert "Senior Data Scientist" in cleaned
    assert "Experienced with NLP." in cleaned
    assert "\n\n\n" not in cleaned


def test_clean_text_fixes_hyphenated_breaks():
    raw = "Built a micro- \n service with con- \n tainers."
    cleaned = clean_text(raw)
    assert "microservice" in cleaned
    assert "containers" in cleaned


def test_clean_text_standardizes_bullets():
    raw = "• Python\n* PyTorch\n- Scikit-Learn\n► Docker"
    cleaned = clean_text(raw)
    assert "• Python" in cleaned
    assert "• PyTorch" in cleaned
    assert "• Scikit-Learn" in cleaned


def test_clean_text_preserves_acronyms():
    raw = "Deployed NLP models on AWS EC2 using Docker and CI/CD pipelines with SQL databases."
    cleaned = clean_text(raw)
    assert "AWS" in cleaned
    assert "EC2" in cleaned
    assert "NLP" in cleaned
    assert "CI/CD" in cleaned
    assert "SQL" in cleaned


def test_pdf_extraction_sample():
    sample_pdf = os.path.join("data", "samples", "resumes", "data_scientist_resume.pdf")
    if os.path.exists(sample_pdf):
        text = extract_text(sample_pdf)
        assert len(text) > 200
        assert "PyTorch" in text or "Python" in text


def test_docx_extraction_sample():
    sample_docx = os.path.join("data", "samples", "resumes", "backend_engineer_resume.docx")
    if os.path.exists(sample_docx):
        text = extract_text(sample_docx)
        assert len(text) > 200
        assert "FastAPI" in text or "Python" in text
