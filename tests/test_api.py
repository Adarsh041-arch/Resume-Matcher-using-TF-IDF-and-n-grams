"""
Integration tests for FastAPI REST endpoints.
"""

import io
from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)


def test_api_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["skills_indexed"] > 200


def test_api_taxonomy():
    response = client.get("/api/taxonomy")
    assert response.status_code == 200
    data = response.json()
    assert "categories" in data
    assert "Languages" in data["categories"]


def test_api_samples():
    response = client.get("/api/samples")
    assert response.status_code == 200
    data = response.json()
    assert "resumes" in data
    assert "job_descriptions" in data


def test_api_match_text():
    payload = {
        "resume_text": "Experienced Python developer with Docker, FastAPI, and AWS.",
        "jd_text": "Looking for Python engineer with FastAPI, Docker, and Kubernetes on AWS."
    }
    response = client.post("/api/match-text", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "composite_score" in data
    assert "tfidf_similarity" in data
    assert "skill_overlap_pct" in data
    assert len(data["matched_skills"]) >= 3
    assert any(m["skill"] == "Kubernetes" for m in data["missing_skills"])


def test_api_match_file_upload():
    resume_content = b"Alex Chen - Machine Learning Engineer proficient in PyTorch, Scikit-Learn, and Python."
    file_tuple = ("resume.txt", io.BytesIO(resume_content), "text/plain")
    data = {
        "jd_text": "Seeking ML Engineer with PyTorch, Scikit-Learn, and Python."
    }
    response = client.post("/api/match", files={"resume_file": file_tuple}, data=data)
    assert response.status_code == 200
    res = response.json()
    assert res["composite_score"] > 50.0
    assert len(res["matched_skills"]) >= 2
