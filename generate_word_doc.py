"""
Comprehensive Word Document (.docx) Generator for Resume Matcher NLP Project.
Generates a publication-grade report with tables, callouts, and embedded high-res screenshots.
"""

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGES_DIR = os.path.join(PROJECT_DIR, "docs", "images")
OUTPUT_DOCX = os.path.join(PROJECT_DIR, "Resume_Matcher_NLP_Project_Report.docx")

# Styling Palette Constants
COLOR_PRIMARY = RGBColor(26, 54, 93)      # Deep Navy #1A365D
COLOR_SECONDARY = RGBColor(43, 108, 176)  # Slate Blue #2B6CB0
COLOR_ACCENT = RGBColor(79, 70, 229)     # Indigo #4F46E5
COLOR_DARK = RGBColor(15, 23, 42)        # Slate 900 #0F172A
COLOR_MUTED = RGBColor(100, 116, 139)    # Slate 500 #64748B
COLOR_SUCCESS = RGBColor(16, 185, 129)   # Emerald #10B981


def set_cell_background(cell, hex_color: str):
    """Sets background shading color for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)


def set_cell_margins(cell, top=140, bottom=140, left=200, right=200):
    """Sets cell internal padding."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(
        f'<w:tcMar {nsdecls("w")}>'
        f'<w:top w:w="{top}" w:type="dxa"/>'
        f'<w:bottom w:w="{bottom}" w:type="dxa"/>'
        f'<w:left w:w="{left}" w:type="dxa"/>'
        f'<w:right w:w="{right}" w:type="dxa"/>'
        f'</w:tcMar>'
    )
    tcPr.append(tcMar)


def add_callout_box(doc, text: str, title: str = "KEY HIGHLIGHT"):
    """Adds a stylish bordered callout box."""
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, "F1F5F9")
    set_cell_margins(cell, top=160, bottom=160, left=220, right=200)
    
    # Left border only (accent)
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>'
        f'<w:top w:val="none"/>'
        f'<w:left w:val="single" w:sz="24" w:space="0" w:color="4F46E5"/>'
        f'<w:bottom w:val="none"/>'
        f'<w:right w:val="none"/>'
        f'</w:tcBorders>'
    )
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(2)
    p.paragraph_format.space_after = Pt(4)
    run_title = p.add_run(f"📌 {title}: ")
    run_title.bold = True
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(10.5)
    run_title.font.color.rgb = COLOR_ACCENT
    
    run_text = p.add_run(text)
    run_text.font.name = "Calibri"
    run_text.font.size = Pt(10)
    run_text.font.color.rgb = COLOR_DARK
    
    # Add spacing after table
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def format_table(table, col_widths, headers, data, align_right_cols=[]):
    """Formats a clean, modern striped data table."""
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False

    # Header Row
    hdr_cells = table.rows[0].cells
    for i, title in enumerate(headers):
        hdr_cells[i].text = title
        set_cell_background(hdr_cells[i], "1E293B")
        set_cell_margins(hdr_cells[i], top=140, bottom=140, left=150, right=150)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if i in align_right_cols else WD_ALIGN_PARAGRAPH.LEFT
        for run in p.runs:
            run.font.name = "Calibri"
            run.font.bold = True
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Data Rows
    for r_idx, row_data in enumerate(data):
        row = table.add_row()
        bg_color = "F8FAFC" if r_idx % 2 == 1 else "FFFFFF"
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = str(val)
            set_cell_background(cell, bg_color)
            set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if c_idx in align_right_cols else WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Calibri"
                run.font.size = Pt(9.5)
                run.font.color.rgb = COLOR_DARK

    # Column Widths
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = Inches(w)


def build_word_document():
    print("Generating comprehensive Word Project Report...")
    doc = Document()

    # Configure 1-inch margins
    sections = doc.sections
    for s in sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    # ----------------------------------------------------
    # COVER / HEADER BLOCK
    # ----------------------------------------------------
    title_p = doc.add_paragraph()
    title_p.paragraph_format.space_before = Pt(10)
    title_p.paragraph_format.space_after = Pt(4)
    run_title = title_p.add_run("Automated Resume & Job Description Semantic Matcher")
    run_title.font.name = "Calibri"
    run_title.font.size = Pt(26)
    run_title.font.bold = True
    run_title.font.color.rgb = COLOR_PRIMARY

    sub_p = doc.add_paragraph()
    sub_p.paragraph_format.space_after = Pt(18)
    run_sub = sub_p.add_run("An End-to-End Natural Language Processing System for Entity Extraction, TF-IDF Vector Similarity, and Ranked Skill Gap Analysis")
    run_sub.font.name = "Calibri"
    run_sub.font.size = Pt(13)
    run_sub.font.italic = True
    run_sub.font.color.rgb = COLOR_SECONDARY

    # Metadata pill box
    meta_table = doc.add_table(rows=1, cols=3)
    meta_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    meta_table.columns[0].width = Inches(2.1)
    meta_table.columns[1].width = Inches(2.2)
    meta_table.columns[2].width = Inches(2.2)
    
    meta_items = [
        ("PROJECT DOMAIN", "Applied NLP & IR"),
        ("TECH STACK", "FastAPI, spaCy, Scikit-Learn"),
        ("STATUS", "Production Complete (v1.0)")
    ]
    for i, (k, v) in enumerate(meta_items):
        cell = meta_table.cell(0, i)
        set_cell_background(cell, "F1F5F9")
        set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
        p = cell.paragraphs[0]
        r1 = p.add_run(f"{k}\n")
        r1.font.bold = True
        r1.font.size = Pt(8.5)
        r1.font.color.rgb = COLOR_MUTED
        r2 = p.add_run(v)
        r2.font.bold = True
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = COLOR_DARK

    doc.add_paragraph().paragraph_format.space_after = Pt(14)

    # ----------------------------------------------------
    # EXECUTIVE SUMMARY
    # ----------------------------------------------------
    h1 = doc.add_heading("Executive Summary", level=1)
    h1.paragraph_format.space_before = Pt(14)
    h1.paragraph_format.space_after = Pt(6)
    
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(10)
    p.add_run(
        "Modern technical hiring is constrained by massive volumes of unstructured resumes and complex job descriptions. "
        "Standard Applicant Tracking Systems (ATS) rely either on primitive keyword exact-matching (which fails to detect synonyms "
        "or acronyms) or generic semantic embeddings that hallucinate skills or fail to pinpoint actionable gaps. "
        "This project implements a robust, end-to-end NLP system that couples deterministic rule-based Named Entity Recognition (NER) "
        "using a curated taxonomy of 450+ technical skills with TF-IDF lexical vectorization. The system computes a dual-faceted match score, "
        "categorizes technical competencies, and performs set-difference gap analysis ranked by job description TF-IDF prominence."
    )

    add_callout_box(
        doc,
        "The system achieves 95.7% Precision and 97.8% Recall in skill extraction, coupled with a Spearman Rank Correlation of rs = 0.786 "
        "and Pearson Linear Correlation of r = 0.937 against human benchmark evaluations, delivering a +33.1% discrimination margin between "
        "matching and mismatched candidates.",
        "BENCHMARK RESULTS"
    )

    # ----------------------------------------------------
    # CHAPTER 1: PROBLEM FRAMING & OBJECTIVES
    # ----------------------------------------------------
    h1 = doc.add_heading("1. Problem Framing & Core Objectives", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "The objective of the system is to take two unstructured documents—a candidate resume (in PDF, DOCX, or TXT format) "
        "and a target job description (raw text)—and automatically produce:\n"
    )
    p.paragraph_format.space_after = Pt(6)

    bullets = [
        ("Document Text Extraction & Normalization: ", "Handling multi-column PDF layouts, bullet merging, broken hyphenated line wraps, and preserving critical technical acronyms (e.g., AWS, GCP, CI/CD, SQL, TF-IDF)."),
        ("Taxonomic Skill Extraction: ", "Detecting canonical technical entities across Languages, Frameworks, Cloud, Databases, AI/ML, and Methodologies with alias resolution (e.g., 'k8s' -> 'Kubernetes')."),
        ("Dual Vector Similarity Scoring: ", "Reporting both lexical/semantic TF-IDF Cosine Similarity and structured skill-set Jaccard Overlap, combined into a calibrated composite match score (0–100%)."),
        ("Ranked Missing Keyword Gap Analysis: ", "Calculating the set difference (JD Skills - Resume Skills) and ranking missing terms by their TF-IDF importance weight and frequency in the job description."),
        ("Interactive Delivery: ", "Serving results through an enterprise FastAPI backend and a glassmorphic web dashboard.")
    ]
    for b_title, b_desc in bullets:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(4)
        r_bt = bp.add_run(b_title)
        r_bt.bold = True
        r_bt.font.color.rgb = COLOR_PRIMARY
        bp.add_run(b_desc)

    # ----------------------------------------------------
    # CHAPTER 2: SYSTEM ARCHITECTURE
    # ----------------------------------------------------
    h1 = doc.add_heading("2. System Architecture & End-to-End Workflow", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "The system pipeline is cleanly decoupled into five modular layers: Ingestion & Text Normalization, "
        "Taxonomic Entity Extraction, Dual Vector Scoring & Gap Ranking, Application Layer (FastAPI), and Presentation (Web UI). "
        "The diagram below illustrates the exact data transformation flow:"
    )
    p.paragraph_format.space_after = Pt(10)

    # Architecture summary table
    arch_table = doc.add_table(rows=1, cols=3)
    format_table(
        arch_table,
        [1.8, 2.2, 2.5],
        ["Pipeline Phase", "Module / Tool", "Key Transformation"],
        [
            ["1. Ingestion & Clean", "src/parser.py (PyMuPDF / docx)", "Multi-column block parsing, acronym preservation, line wrap fixes"],
            ["2. Skill Extraction", "src/skill_extractor.py", "spaCy EntityRuler pattern matching, 450+ taxonomy, alias resolution"],
            ["3. Vector Scoring", "src/scorer.py (TfidfVectorizer)", "Unigram/bigram sublinear TF-IDF, Cosine Similarity, Jaccard Index"],
            ["4. Gap Ranking", "src/scorer.py", "Set difference (JD - Resume), weighted by (0.4*freq + 0.6*tfidf)"],
            ["5. Delivery", "src/api.py & frontend/", "FastAPI REST endpoints, JSON report export, SVG radial gauge UI"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ----------------------------------------------------
    # CHAPTER 3: METHODOLOGY & NLP ALGORITHMS
    # ----------------------------------------------------
    h1 = doc.add_heading("3. Methodology & Mathematical Formulations", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    doc.add_heading("3.1 Text Normalization & Acronym Preservation", level=2)
    p = doc.add_paragraph(
        "PDF extraction frequently suffers from hyphenation artifacts (e.g. 'con- \\n tainer' broken across lines) "
        "and merged bullet characters. The parser normalizes whitespace, standardizes bullet encodings, and strictly preserves "
        "casing for a whitelist of protected technical acronyms (AWS, GCP, SQL, CI/CD, TF-IDF, RAG, BERT, GPT, EC2, K8S) "
        "to prevent information loss before NLP tokenization."
    )

    doc.add_heading("3.2 Taxonomic Skill Extraction with spaCy EntityRuler", level=2)
    p = doc.add_paragraph(
        "Generic statistical NER models trained on news corpora (such as standard en_core_web_sm) fail dramatically "
        "on technical resumes: they often misclassify software tools (e.g. tagging 'Docker' as an ORG or skipping 'FastAPI' entirely). "
        "Our system implements a custom EntityRuler backed by a curated 450+ skill taxonomy categorized into six domains:\n"
    )
    tax_items = [
        ("Languages: ", "Python, TypeScript, Java, C++, Go, Rust, SQL, Bash, R, Scala, etc."),
        ("Frameworks & Libraries: ", "React, Next.js, FastAPI, Django, PyTorch, TensorFlow, Scikit-Learn, LangChain, Hugging Face, etc."),
        ("Cloud & DevOps: ", "AWS, Azure, GCP, Docker, Kubernetes, Terraform, CI/CD, GitHub Actions, Prometheus, Grafana, etc."),
        ("Databases & Big Data: ", "PostgreSQL, MongoDB, Redis, Snowflake, BigQuery, Kafka, Airflow, Spark, Pinecone, ChromaDB, etc."),
        ("AI & Machine Learning: ", "NLP, Computer Vision, LLM, Generative AI, RAG, BERT, Fine-Tuning, MLOps, Weights & Biases, etc."),
        ("Methodologies & Soft Skills: ", "Agile, Scrum, System Design, Microservices, TDD, Unit Testing, Code Review, Communication, etc.")
    ]
    for cat_name, cat_examples in tax_items:
        bp = doc.add_paragraph(style='List Bullet')
        bp.paragraph_format.space_after = Pt(3)
        r = bp.add_run(cat_name)
        r.bold = True
        bp.add_run(cat_examples)

    doc.add_heading("3.3 Dual Lexical & Structured Scoring", level=2)
    p = doc.add_paragraph(
        "Rather than relying on a single opaque metric, the system computes two complementary scores:\n"
    )
    
    p1 = doc.add_paragraph()
    p1.paragraph_format.left_indent = Inches(0.25)
    r1 = p1.add_run("1. Lexical TF-IDF Cosine Similarity:\n")
    r1.bold = True
    r1.font.color.rgb = COLOR_SECONDARY
    p1.add_run(
        "Documents are tokenized into unigrams and bigrams with English stop-word filtering. "
        "Term frequency is scaled sublinearly (1 + ln(tf)) to prevent keyword stuffing, and smooth IDF weighting is applied: "
        "idf(t) = ln((1 + n)/(1 + df(t))) + 1. The cosine similarity between L2-normalized vector representations quantifies vocabulary alignment."
    )

    p2 = doc.add_paragraph()
    p2.paragraph_format.left_indent = Inches(0.25)
    r2 = p2.add_run("2. Structured Skill Overlap (Jaccard Index):\n")
    r2.bold = True
    r2.font.color.rgb = COLOR_SECONDARY
    p2.add_run(
        "Measures exact coverage of required taxonomy entities: Ratio = |Resume_Skills ∩ JD_Skills| / |JD_Skills|. "
        "This ensures that even if a resume has eloquent prose, it is penalized if core required technical proficiencies are absent."
    )

    p3 = doc.add_paragraph()
    p3.paragraph_format.left_indent = Inches(0.25)
    r3 = p3.add_run("3. Composite Match Score:\n")
    r3.bold = True
    r3.font.color.rgb = COLOR_SECONDARY
    p3.add_run(
        "Calculated as: Score = (w_tfidf × Cosine_Sim) + (w_skill × Skill_Overlap), where default weights are 45% and 55% respectively "
        "(dynamically tunable by the user in the dashboard)."
    )

    doc.add_heading("3.4 Ranked Missing Keyword Priority Formula", level=2)
    p = doc.add_paragraph(
        "Unranked dumps of missing keywords overwhelm candidates and hiring managers. "
        "Our system computes the set difference (JD_Skills - Resume_Skills) and scores each missing term using an importance metric:\n"
        "Importance(s) = 0.4 × Frequency_in_JD(s) + 0.6 × TF-IDF_Weight_in_JD(s)\n"
        "Missing skills are then partitioned into High, Medium, and Low priority tiers."
    )

    # ----------------------------------------------------
    # CHAPTER 4: USER INTERFACE & DASHBOARD (WITH SCREENSHOT)
    # ----------------------------------------------------
    h1 = doc.add_heading("4. Interactive Dashboard & User Experience", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "To provide a production-quality experience, the system includes an enterprise-grade dark-mode web dashboard "
        "featuring glassmorphic panels, animated SVG radial score indicators, dynamic weight sliders, and 1-click scenario presets."
    )
    p.paragraph_format.space_after = Pt(10)

    # Embed Dashboard Screenshot
    ui_image_path = os.path.join(IMAGES_DIR, "dashboard_ui.jpg")
    if os.path.exists(ui_image_path):
        doc.add_picture(ui_image_path, width=Inches(6.5))
        caption_p = doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_p.paragraph_format.space_before = Pt(4)
        caption_p.paragraph_format.space_after = Pt(14)
        run_cap = caption_p.add_run("Figure 1: ResumeMatcher Modern Interactive Web Dashboard (Live Matching & Gap Analysis)")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9)
        run_cap.font.color.rgb = COLOR_MUTED

    p = doc.add_paragraph(
        "The interface offers:\n"
        "• Drag-and-drop document upload (.pdf, .docx, .txt) with automatic format detection and fallback.\n"
        "• One-click scenario presets for rapid testing (Senior Data Scientist, Lead DevOps, Senior Backend).\n"
        "• Real-time dual progress bars for Lexical TF-IDF Cosine Similarity and Structured Skill Overlap.\n"
        "• Ranked missing keywords grid with priority tags (High in Coral, Medium in Amber) and frequency badges.\n"
        "• Category skill coverage matrix detailing completion ratios per technical domain.\n"
        "• Exportable JSON summary report for integration with downstream HR pipelines."
    )

    # ----------------------------------------------------
    # CHAPTER 5: EMPIRICAL BENCHMARK EVALUATION
    # ----------------------------------------------------
    h1 = doc.add_heading("5. Empirical Benchmarks & Evaluation", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "To guarantee objective validation without fabricating metrics, an empirical evaluation suite was executed "
        "across ground-truth labeled skill benchmarks and pairwise matching scenarios."
    )

    doc.add_heading("5.1 Skill Extraction Performance (Rule-Based vs Statistical NER)", level=2)
    p = doc.add_paragraph(
        "The rule-based taxonomy extractor was evaluated against ground-truth skill annotations across multiple domain samples. "
        "It achieved near-perfect recall and precision compared to generic off-the-shelf statistical NER models:"
    )
    p.paragraph_format.space_after = Pt(8)

    # Embed Benchmark Chart
    bm_chart_path = os.path.join(IMAGES_DIR, "benchmark_performance.png")
    if os.path.exists(bm_chart_path):
        doc.add_picture(bm_chart_path, width=Inches(6.0))
        caption_p = doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_p.paragraph_format.space_before = Pt(4)
        caption_p.paragraph_format.space_after = Pt(12)
        run_cap = caption_p.add_run("Figure 2: Skill Extraction Performance: Curated EntityRuler vs Statistical Baseline NER")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9)
        run_cap.font.color.rgb = COLOR_MUTED

    eval_table = doc.add_table(rows=1, cols=4)
    format_table(
        eval_table,
        [2.2, 1.4, 1.4, 1.5],
        ["Model Approach", "Precision", "Recall", "F1-Score"],
        [
            ["Rule-Based EntityRuler (Curated)", "95.7%", "97.8%", "96.7%"],
            ["- Data Science Sample", "89.5%", "100.0%", "94.4%"],
            ["- DevOps Sample", "100.0%", "100.0%", "100.0%"],
            ["- Backend Engineering Sample", "100.0%", "92.9%", "96.3%"],
            ["Generic Statistical NER (Baseline)", "68.4%", "38.2%", "49.0%"]
        ],
        align_right_cols=[1, 2, 3]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_heading("5.2 Resume-JD Matching Correlation with Human Ground Truth", level=2)
    p = doc.add_paragraph(
        "A benchmark matrix of resume-JD pairs was evaluated across high-alignment matches, partial-overlap transfers, "
        "and cross-domain mismatches. The model's composite score was correlated against human expert ground-truth ratings."
    )
    p.paragraph_format.space_after = Pt(8)

    # Embed Correlation Scatter Plot
    corr_chart_path = os.path.join(IMAGES_DIR, "correlation_scatter.png")
    if os.path.exists(corr_chart_path):
        doc.add_picture(corr_chart_path, width=Inches(6.0))
        caption_p = doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_p.paragraph_format.space_before = Pt(4)
        caption_p.paragraph_format.space_after = Pt(12)
        run_cap = caption_p.add_run("Figure 3: Linear & Monotonic Correlation Between Model Scores and Human Ground-Truth Ratings")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9)
        run_cap.font.color.rgb = COLOR_MUTED

    corr_table = doc.add_table(rows=1, cols=4)
    format_table(
        corr_table,
        [2.8, 1.2, 1.2, 1.3],
        ["Benchmark Pair Scenario", "Human Rating", "Model Score", "Alignment Tier"],
        [
            ["Data Scientist Resume vs DS JD", "95%", "48.5%", "High Match"],
            ["DevOps Resume vs DevOps JD", "92%", "60.3%", "High Match"],
            ["Backend Resume vs Backend JD", "90%", "54.5%", "High Match"],
            ["Backend Resume vs DevOps JD (Docker/Linux overlap)", "40%", "25.0%", "Moderate Match"],
            ["Backend Resume vs DS JD (Python/SQL overlap)", "35%", "18.0%", "Moderate Match"],
            ["DevOps Resume vs DS JD (Cloud vs NLP/Math)", "15%", "15.0%", "Low / Mismatch"],
            ["DS Resume vs DevOps JD (NLP vs K8s/Infra)", "20%", "27.7%", "Low / Mismatch"]
        ],
        align_right_cols=[1, 2]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(10)

    add_callout_box(
        doc,
        "Statistical Validation Summary: Spearman Rank Correlation rs = 0.7857 confirms strong monotonic ranking consistency. "
        "Pearson Correlation r = 0.9372 demonstrates exceptional linear alignment. Average Target Match (54.4%) vs Average Mismatch (21.4%) "
        "yields a clean +33.1% discrimination separation.",
        "CORRELATION METRICS"
    )

    doc.add_heading("5.3 Category Skill Coverage Matrix", level=2)
    p = doc.add_paragraph(
        "Granular category breakdown allows recruiters and applicants to identify domain-specific strengths and deficiencies. "
        "Figure 4 shows the coverage breakdown for the Senior Data Scientist scenario:"
    )
    p.paragraph_format.space_after = Pt(8)

    # Embed Category Coverage Chart
    cat_chart_path = os.path.join(IMAGES_DIR, "category_coverage.png")
    if os.path.exists(cat_chart_path):
        doc.add_picture(cat_chart_path, width=Inches(6.0))
        caption_p = doc.add_paragraph()
        caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption_p.paragraph_format.space_before = Pt(4)
        caption_p.paragraph_format.space_after = Pt(12)
        run_cap = caption_p.add_run("Figure 4: Category Skill Coverage Breakdown: Required vs Matched Skills")
        run_cap.font.italic = True
        run_cap.font.size = Pt(9)
        run_cap.font.color.rgb = COLOR_MUTED

    # ----------------------------------------------------
    # CHAPTER 6: IMPLEMENTATION & REPOSITORY STRUCTURE
    # ----------------------------------------------------
    h1 = doc.add_heading("6. Implementation Details & API Specifications", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "The project follows a clean, modular Python repository structure with automated test suites and Docker support:"
    )
    p.paragraph_format.space_after = Pt(8)

    repo_table = doc.add_table(rows=1, cols=2)
    format_table(
        repo_table,
        [2.2, 4.3],
        ["File / Directory", "Responsibility & Description"],
        [
            ["src/parser.py", "Multi-format text extraction (PyMuPDF, docx) and robust text cleaning"],
            ["src/skill_extractor.py", "Taxonomy loader, EntityRuler engine, alias resolver, and NER benchmark"],
            ["src/scorer.py", "Pure TF-IDF vectorizer, Cosine Similarity, Jaccard overlap, and ranked gap analysis"],
            ["src/api.py", "FastAPI server exposing /match, /match-text, /taxonomy, and static UI routes"],
            ["frontend/", "Interactive Web Dashboard (HTML5, Vanilla CSS glassmorphic theme, app.js)"],
            ["data/skill_taxonomy.json", "Curated taxonomy containing 450+ skills across 6 domains with alias mapping"],
            ["data/generate_samples.py", "Automated generator for realistic sample PDF/DOCX resumes and JDs"],
            ["eval.py & notebooks/eval.ipynb", "Reproducible evaluation pipeline computing Precision, Recall, and Spearman rs"],
            ["tests/", "Comprehensive test suite covering parser, extractor, scorer, and API (18/18 passing)"],
            ["main.py", "CLI execution tool and web server entrypoint with colored Rich console tables"],
            ["Dockerfile", "Production container specification for cross-platform deployment"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    doc.add_heading("6.1 FastAPI REST Endpoints", level=2)
    api_table = doc.add_table(rows=1, cols=3)
    format_table(
        api_table,
        [1.2, 1.8, 3.5],
        ["Method", "Endpoint", "Functionality"],
        [
            ["GET", "/api/health", "Health status, version, and total indexed skills count"],
            ["GET", "/api/taxonomy", "Complete list of categories, canonical skills, and alias dictionary"],
            ["GET", "/api/samples", "Pre-loaded realistic sample resumes and job descriptions for 1-click testing"],
            ["POST", "/api/match", "Multipart upload accepting resume file (.pdf, .docx, .txt) + JD text"],
            ["POST", "/api/match-text", "Direct JSON payload comparison {resume_text, jd_text}"],
            ["POST", "/api/benchmark-ner", "Compares rule-based taxonomy extraction against statistical NER"]
        ]
    )
    doc.add_paragraph().paragraph_format.space_after = Pt(12)

    # ----------------------------------------------------
    # CHAPTER 7: CONCLUSION & FUTURE WORK
    # ----------------------------------------------------
    h1 = doc.add_heading("7. Conclusion & Future Roadmap", level=1)
    h1.paragraph_format.space_before = Pt(16)
    h1.paragraph_format.space_after = Pt(6)

    p = doc.add_paragraph(
        "This project successfully delivers an end-to-end NLP solution addressing the core pain points of automated resume screening. "
        "By pairing deterministic, curated taxonomic NER with continuous lexical TF-IDF vectorization, the system achieves the following key advantages:\n"
        "1. Predictable, explainable matching: Eliminates hallucinations and 'black-box' embedding drift.\n"
        "2. Actionable candidate feedback: Prioritizes missing skills by actual occurrence and term weight in the job description.\n"
        "3. High operational efficiency: Sub-second inference time with zero heavy GPU dependency, running cleanly in lightweight containers."
    )
    p.paragraph_format.space_after = Pt(6)

    p_future = doc.add_paragraph(
        "Future Enhancements:\n"
        "• Dense Embedding Hybridization: Experimenting with hybrid cross-encoder rerankers (e.g. BGE-M3 or MiniLM) combined with taxonomy filtering.\n"
        "• Contextual Seniority Parsing: Extracting years of experience associated with individual skills (e.g., '5 years of Python' vs 'introductory Python').\n"
        "• Multilingual Taxonomy Extension: Broadening technical vocabularies to support German, French, and Japanese job postings."
    )

    # Save document
    doc.save(OUTPUT_DOCX)
    print(f"Report generated successfully at: {OUTPUT_DOCX}")


if __name__ == "__main__":
    build_word_document()
