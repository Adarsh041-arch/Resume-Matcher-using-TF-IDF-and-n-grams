"""
Tests for Scorer: TF-IDF, Cosine Similarity, Jaccard Overlap, and Missing Skill Ranking.
"""

import pytest
from src.scorer import ResumeScorer, PureTfidfVectorizer, cosine_similarity_dicts


def test_pure_tfidf_vectorizer():
    docs = [
        "Python developer with machine learning experience",
        "DevOps engineer with Kubernetes and Docker experience",
        "Python engineer working on Kubernetes deployment"
    ]
    vec = PureTfidfVectorizer()
    vec.fit(docs)
    
    v0 = vec.transform_single(docs[0])
    v2 = vec.transform_single(docs[2])
    
    sim = cosine_similarity_dicts(v0, v2)
    assert 0.0 < sim <= 1.0
    assert "python" in v0


def test_scorer_metrics():
    scorer = ResumeScorer()
    resume = "Senior Python developer with FastAPI, PostgreSQL, and Docker."
    jd = "Seeking Python developer with FastAPI, Kubernetes, and Docker."
    
    res = scorer.score(resume, jd)
    assert 0.0 <= res["composite_score"] <= 100.0
    assert 0.0 <= res["tfidf_similarity"] <= 100.0
    assert 0.0 <= res["skill_overlap_pct"] <= 100.0
    
    matched = [m["skill"] for m in res["matched_skills"]]
    assert "Python" in matched
    assert "FastAPI" in matched
    assert "Docker" in matched
    
    missing = [m["skill"] for m in res["missing_skills"]]
    assert "Kubernetes" in missing


def test_missing_skill_importance_ranking():
    scorer = ResumeScorer()
    resume = "Python software engineer"
    jd = "Need Kubernetes expert. Must have deep Kubernetes knowledge, Kubernetes clustering, and Docker with AWS."
    
    res = scorer.score(resume, jd)
    missing = res["missing_skills"]
    assert len(missing) >= 2
    # Kubernetes is repeated 3 times in JD, so it should rank highest in priority
    assert missing[0]["skill"] == "Kubernetes"
    assert missing[0]["priority"] == "High"
