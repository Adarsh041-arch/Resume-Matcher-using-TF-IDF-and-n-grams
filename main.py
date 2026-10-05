"""
Resume Matcher Main Application Entrypoint.

Supports both:
1. Web Dashboard Server mode: `python main.py` or `python main.py --serve`
2. CLI Matching mode: `python main.py --resume resume.pdf --jd job_desc.txt`
"""

import sys
import argparse
import uvicorn
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from src.parser import extract_text
from src.skill_extractor import SkillExtractor
from src.scorer import ResumeScorer

console = Console()


def run_cli_match(resume_path: str, jd_path: str):
    """Executes CLI resume and JD matching and prints rich formatted reports."""
    console.print(Panel.fit("[bold cyan]Resume & Job Description NLP Matcher[/bold cyan]", border_style="cyan"))

    try:
        resume_text = extract_text(resume_path)
    except Exception as e:
        console.print(f"[bold red]Error reading resume:[/bold red] {e}")
        sys.exit(1)

    try:
        jd_text = extract_text(jd_path)
    except Exception as e:
        console.print(f"[bold red]Error reading job description:[/bold red] {e}")
        sys.exit(1)

    extractor = SkillExtractor()
    scorer = ResumeScorer(extractor)

    results = scorer.score(resume_text, jd_text)

    # Score Summary Table
    score_table = Table(title="Matching Performance Summary", style="blue")
    score_table.add_column("Metric", style="bold")
    score_table.add_column("Score", justify="right")
    
    comp_score = results['composite_score']
    status_style = "bold green" if comp_score >= 70 else "bold yellow" if comp_score >= 45 else "bold red"

    score_table.add_row("Composite Match Score", f"[{status_style}]{comp_score:.1f}%[/{status_style}]")
    score_table.add_row("TF-IDF Semantic Cosine Similarity", f"{results['tfidf_similarity']:.1f}%")
    score_table.add_row("Structured Skill Overlap (Jaccard)", f"{results['skill_overlap_pct']:.1f}%")
    score_table.add_row("JD Skills Demanded", str(results["jd_total_skills"]))
    score_table.add_row("Candidate Skills Matched", f"[green]{results['matched_skills_count']}[/green]")
    score_table.add_row("Missing Skills Identified", f"[red]{results['missing_skills_count']}[/red]")
    console.print(score_table)

    # Ranked Missing Keywords Table
    if results["missing_skills"]:
        missing_table = Table(title="Top Missing Keywords (Ranked by JD Importance)", style="red")
        missing_table.add_column("Rank", justify="center")
        missing_table.add_column("Missing Skill", style="bold")
        missing_table.add_column("Category")
        missing_table.add_column("Priority")
        missing_table.add_column("JD Frequency", justify="center")
        
        for idx, item in enumerate(results["missing_skills"][:10], 1):
            pri_color = "red" if item["priority"] == "High" else "yellow" if item["priority"] == "Medium" else "white"
            missing_table.add_row(
                str(idx),
                item["skill"],
                item["category"],
                f"[{pri_color}]{item['priority']}[/{pri_color}]",
                f"{item['frequency_in_jd']}x"
            )
        console.print(missing_table)

    # Matched Skills
    if results["matched_skills"]:
        matched_names = [f"[green]{m['skill']}[/green]" for m in results["matched_skills"]]
        console.print(f"\n[bold green][+] Matched Skills ({len(matched_names)}):[/bold green] " + ", ".join(matched_names))


def start_web_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = False):
    """Starts FastAPI web server."""
    console.print(f"\n[bold green][>>] Launching ResumeMatcher Dashboard on http://{host}:{port}[/bold green]\n")
    uvicorn.run("src.api:app", host=host, port=port, reload=reload)


def main():
    parser = argparse.ArgumentParser(description="Resume & Job Description Matcher NLP CLI and Server")
    parser.add_argument("--resume", type=str, help="Path to resume file (PDF, DOCX, or TXT)")
    parser.add_argument("--jd", type=str, help="Path to job description file (TXT or PDF)")
    parser.add_argument("--serve", action="store_true", help="Launch interactive web server")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="Host address for web server")
    parser.add_argument("--port", type=int, default=8000, help="Port for web server")

    args = parser.parse_args()

    if args.resume and args.jd:
        run_cli_match(args.resume, args.jd)
    else:
        start_web_server(host=args.host, port=args.port)


if __name__ == "__main__":
    main()
