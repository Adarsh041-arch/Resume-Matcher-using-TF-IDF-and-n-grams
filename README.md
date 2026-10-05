# Resume & Job Description Matcher (NLP System)

An end-to-end NLP system that parses resumes (PDF, DOCX, TXT), extracts structured skills using a custom spaCy `EntityRuler` with a curated 450+ skill taxonomy, calculates dual **TF-IDF Semantic Cosine Similarity** and **Structured Skill Overlap (Jaccard Index)**, ranks missing keywords by job description importance, and provides an interactive web dashboard and REST API.

---

## Architecture Overview

```
Resume (PDF / DOCX / TXT) ──────────────┐
                                         ├──► [Text Extraction & Clean Text Normalizer]
Job Description (Raw Text) ─────────────┘                   │
                                                            ├──► [spaCy EntityRuler + Taxonomy]
                                                            │           │
                                                            │     Skill Set A (Resume)
                                                            │     Skill Set B (JD)
                                                            │           │
                                                            ▼           ├──► Missing Skills = Set B - Set A
                                             [TF-IDF Vectorizer]        │    (Ranked by JD TF-IDF weight)
                                                    │                   │
                                                    ▼                   ▼
                                            Cosine Similarity   Jaccard Overlap
                                                    │                   │
                                                    └─────────┬─────────┘
                                                              ▼
                                                     [Composite Score &
                                                   Category Breakdown]
                                                              │
                                                              ▼
                                            [FastAPI Backend + Web Dashboard]
```

---

## Key Features

1. **Robust Multi-Format Parsing (`src/parser.py`)**:
   - Parses multi-column and tabular resumes from PDF (`pymupdf` / `pypdf`), DOCX (`python-docx`), and plain text.
   - Handles messy PDF artifacts: broken hyphenated line wraps (`con- \n tainer` -> `container`), merged bullet points (`•`, `*`, `►`), and footer clutter.
   - Preserves critical technical acronyms (`AWS`, `GCP`, `CI/CD`, `SQL`, `TF-IDF`, `NLP`, `RAG`, `BERT`, `GPT`, `EC2`).

2. **Entity & Skill Extraction (`src/skill_extractor.py`)**:
   - Curated taxonomy of **450+ skills** structured across 6 technical domains (`data/skill_taxonomy.json`).
   - Normalizes alias variations (`k8s` -> `Kubernetes`, `postgres` -> `PostgreSQL`, `cicd` -> `CI/CD`, `hf` -> `Hugging Face`).
   - Benchmarking comparison module demonstrating why custom rule-based EntityRuler dramatically outperforms off-the-shelf statistical NER models for technical skills.

3. **Dual Lexical & Structured Vector Scoring (`src/scorer.py`)**:
   - **TF-IDF Vectorizer & Cosine Similarity**: Evaluates document-level vocabulary, terminology weighting, and contextual overlap.
   - **Structured Skill Overlap & Jaccard Index**: Computes exact taxonomic overlap `|Resume ∩ JD| / |JD|`.
   - **Composite Match Score**: Calibrated weighted combination (default 45% TF-IDF + 55% Skill Overlap).

4. **Ranked Missing Keyword Gap Analysis (`src/scorer.py`)**:
   - Performs set difference: $\text{Missing Skills} = \text{JD Skills} - \text{Resume Skills}$.
   - Ranks missing skills by occurrence frequency and TF-IDF weight inside the JD.
   - Assigns priority tiers (`High`, `Medium`, `Low`) so candidates can prioritize key skill gaps.

5. **Empirical Evaluation & Benchmarking (`eval.py`, `notebooks/eval.ipynb`)**:
   - Ground-truth evaluation on labeled test sets:
     - **Skill Extraction Precision**: `95.7%`
     - **Skill Extraction Recall**: `97.8%`
     - **Skill Extraction F1 Score**: `96.7%`
     - **Spearman Rank Correlation ($r_s$)**: `0.7857` (statistically significant alignment with human ratings)
     - **Pearson Linear Correlation ($r$)**: `0.9372`
     - **Target Match vs Mismatch Discrimination Margin**: `+33.1%` separation

6. **Full-Featured Interface & Deployment**:
   - **FastAPI REST API**: Endpoints for file upload, text matching, taxonomy, and sample presets.
   - **Modern Web Dashboard**: Drag-and-drop file upload, animated SVG radial score gauge, 1-click sample presets, category breakdown matrix, and JSON export.
   - **CLI Mode**: Direct terminal matching with rich colored output tables.
   - **Containerization**: `Dockerfile` ready for deployment.

---

## Project Structure

```
NLP mini_project/
├── data/
│   ├── skill_taxonomy.json          # Curated taxonomy (450+ skills, 6 domains, aliases)
│   ├── generate_samples.py          # Generator for sample PDFs, DOCX, and JDs
│   └── samples/
│       ├── resumes/                 # Sample resumes (Data Scientist, DevOps, Backend)
│       └── job_descriptions/        # Sample real-world JDs
├── src/
│   ├── __init__.py
│   ├── parser.py                    # Multi-format PDF/DOCX/TXT text extractor & cleaner
│   ├── skill_extractor.py           # Taxonomy loader, EntityRuler & alias resolver
│   ├── scorer.py                    # TF-IDF, Cosine Similarity, Jaccard & ranked gap analysis
│   └── api.py                       # FastAPI application & static file routes
├── frontend/
│   ├── index.html                   # Interactive web dashboard
│   ├── styles.css                   # Glassmorphic dark theme stylesheet
│   └── app.js                       # Frontend state, animations, presets, and charts
├── notebooks/
│   └── eval.ipynb                   # Jupyter evaluation notebook with visual analysis
├── tests/
│   ├── test_parser.py               # Unit tests for text cleaning and extraction
│   ├── test_skill_extractor.py      # Unit tests for taxonomy, aliases, and categories
│   ├── test_scorer.py               # Unit tests for vectorizer, scoring, and ranking
│   └── test_api.py                  # Integration tests for FastAPI endpoints
├── conftest.py                      # Pytest environment configuration
├── eval.py                          # Ground-truth evaluation & Spearman correlation benchmark
├── main.py                          # CLI runner & Web server entrypoint
├── Dockerfile                       # Container definition
├── requirements.txt                 # Project dependencies
└── README.md
```

---

## Quick Start Guide

### 1. Installation

Ensure Python 3.10+ is installed:

```bash
pip install -r requirements.txt
```

### 2. Launch Interactive Web Dashboard

Run the main server:

```bash
python main.py
```

Open your browser to: **`http://127.0.0.1:8000`**

- Drag and drop any `.pdf`, `.docx`, or `.txt` resume.
- Use the quick preset buttons (**Data Scientist**, **DevOps**, **Backend**) to load realistic scenarios in 1-click.
- View animated radial match score, TF-IDF cosine similarity, category breakdown, and ranked missing keywords.

### 3. Run via Command-Line Interface (CLI)

Score any resume against a job description directly in your terminal:

```bash
python main.py --resume data/samples/resumes/data_scientist_resume.pdf --jd data/samples/job_descriptions/senior_data_scientist_jd.txt
```

### 4. Run Evaluation & Benchmarking

Execute the evaluation pipeline to reproduce precision, recall, and correlation metrics:

```bash
python eval.py
```

### 5. Run Test Suite

Run all automated unit and integration tests:

```bash
python -m pytest tests/ -v
```

---

## API Endpoints Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | Service health status and indexed skill count |
| `GET` | `/api/taxonomy` | Complete skill categories, aliases, and canonical names |
| `GET` | `/api/samples` | Pre-loaded realistic sample resumes and job descriptions |
| `POST` | `/api/match` | Accepts multipart resume file upload (`.pdf`, `.docx`, `.txt`) + JD text |
| `POST` | `/api/match-text` | Accepts JSON `{ "resume_text": "...", "jd_text": "..." }` |
| `POST` | `/api/benchmark-ner` | Compares rule-based vs statistical NER on provided text |

---

## Docker Deployment

Build and run using Docker:

```bash
docker build -t resume-matcher .
docker run -p 8000:8000 resume-matcher
```

Then visit `http://localhost:8000`.
