"""
Tests for Skill Extractor, Taxonomy, and Alias Resolution.
"""

import pytest
from src.skill_extractor import SkillExtractor


@pytest.fixture
def extractor():
    return SkillExtractor()


def test_taxonomy_loaded(extractor):
    assert len(extractor.categories) >= 5
    assert len(extractor.canonical_skills) > 200
    assert "Python" in extractor.canonical_skills
    assert "Docker" in extractor.canonical_skills
    assert "Kubernetes" in extractor.canonical_skills


def test_alias_resolution(extractor):
    # k8s -> Kubernetes, postgres -> PostgreSQL, cicd -> CI/CD
    text = "Deploying applications with k8s and postgres using modern cicd."
    res = extractor.extract_skills(text)
    assert "Kubernetes" in res["skills"]
    assert "PostgreSQL" in res["skills"]
    assert "CI/CD" in res["skills"]


def test_multi_word_skill_extraction(extractor):
    text = "Extensive background in Natural Language Processing and Retrieval Augmented Generation."
    res = extractor.extract_skills(text)
    assert "Natural Language Processing" in res["skills"] or "NLP" in res["skills"]
    assert "Retrieval Augmented Generation" in res["skills"] or "RAG" in res["skills"]


def test_category_breakdown(extractor):
    text = "Python engineer using PyTorch, AWS, and PostgreSQL for machine learning."
    res = extractor.extract_skills(text)
    cats = res["category_breakdown"]
    assert "Python" in cats.get("Languages", [])
    assert "PyTorch" in cats.get("Frameworks & Libraries", [])
    assert "AWS" in cats.get("Cloud & DevOps", [])
    assert "PostgreSQL" in cats.get("Databases & Big Data", [])
