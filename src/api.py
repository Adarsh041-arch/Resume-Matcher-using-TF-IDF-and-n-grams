"""
FastAPI Backend API for Resume & Job Description Matcher.

Provides endpoints for:
- Parsing resumes (PDF, DOCX, TXT)
- Computing TF-IDF cosine similarity, skill overlap, and ranked missing keywords
- Categorized skill breakdown and interactive benchmarks
- Serving the frontend web interface
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from src.parser import extract_text, clean_text
from src.skill_extractor import SkillExtractor
from src.scorer import ResumeScorer

# Initialize FastAPI app
app = FastAPI(
    title="Resume & Job Description NLP Matcher API",
    description="Production-ready NLP API for parsing resumes, calculating semantic/skill similarity, and ranking missing keywords.",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize NLP Engines
extractor = SkillExtractor()
scorer = ResumeScorer(extractor)

# Directory paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
SAMPLES_DIR = os.path.join(BASE_DIR, "data", "samples")


class MatchTextRequest(BaseModel):
    resume_text: str
    jd_text: str
    tfidf_weight: Optional[float] = 0.45
    skill_weight: Optional[float] = 0.55


class BenchmarkRequest(BaseModel):
    text: str


@app.get("/api/health")
def health_check():
    """Returns API health, loaded categories, and total skills indexed."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "skills_indexed": len(extractor.canonical_skills),
        "categories_count": len(extractor.categories),
        "categories": list(extractor.categories.keys())
    }


@app.get("/api/taxonomy")
def get_taxonomy():
    """Returns all available skill categories and canonical skills."""
    return {
        "categories": extractor.categories,
        "aliases_count": len(extractor.aliases),
        "total_skills": len(extractor.canonical_skills)
    }


@app.get("/api/samples")
def get_sample_presets():
    """Returns pre-loaded sample resumes and job descriptions for rapid testing."""
    samples = {
        "resumes": {},
        "job_descriptions": {}
    }
    
    resumes_path = os.path.join(SAMPLES_DIR, "resumes")
    jds_path = os.path.join(SAMPLES_DIR, "job_descriptions")
    
    if os.path.exists(resumes_path):
        for f in os.listdir(resumes_path):
            if f.endswith(".txt"):
                key = f.replace(".txt", "")
                with open(os.path.join(resumes_path, f), "r", encoding="utf-8") as fp:
                    samples["resumes"][key] = fp.read()

    if os.path.exists(jds_path):
        for f in os.listdir(jds_path):
            if f.endswith(".txt"):
                key = f.replace(".txt", "")
                with open(os.path.join(jds_path, f), "r", encoding="utf-8") as fp:
                    samples["job_descriptions"][key] = fp.read()

    return samples


@app.post("/api/match-text")
def match_text(payload: MatchTextRequest):
    """Computes similarity and missing skills between raw text resume and JD."""
    if not payload.resume_text.strip() or not payload.jd_text.strip():
        raise HTTPException(status_code=400, detail="Both resume_text and jd_text must be non-empty.")
    
    results = scorer.score(
        payload.resume_text,
        payload.jd_text,
        tfidf_weight=payload.tfidf_weight or 0.45,
        skill_weight=payload.skill_weight or 0.55
    )
    return results


@app.post("/api/match")
async def match_file_and_jd(
    resume_file: UploadFile = File(...),
    jd_text: str = Form(...),
    tfidf_weight: float = Form(0.45),
    skill_weight: float = Form(0.55)
):
    """
    Accepts uploaded resume file (PDF, DOCX, or TXT) along with Job Description text.
    Returns complete matching analytics.
    """
    if not jd_text.strip():
        raise HTTPException(status_code=400, detail="Job description text cannot be empty.")

    contents = await resume_file.read()
    filename = resume_file.filename or "uploaded_resume.txt"

    try:
        raw_resume_text = extract_text(contents, filename=filename)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Failed to parse resume file: {str(e)}")

    if not raw_resume_text.strip():
        raise HTTPException(status_code=422, detail="No readable text could be extracted from the uploaded document.")

    results = scorer.score(
        raw_resume_text,
        jd_text,
        tfidf_weight=tfidf_weight,
        skill_weight=skill_weight
    )
    results["filename"] = filename
    return results


@app.post("/api/benchmark-ner")
def benchmark_ner(payload: BenchmarkRequest):
    """Compares rule-based taxonomy extractor with statistical NER."""
    return extractor.benchmark_against_statistical_ner(payload.text)


# Serve frontend static assets
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_ui():
        index_file = os.path.join(FRONTEND_DIR, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        return JSONResponse({"message": "Frontend UI directory exists, but index.html was not found."})
