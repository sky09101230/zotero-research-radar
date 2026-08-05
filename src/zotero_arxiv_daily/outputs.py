"""Stable JSON and Markdown output contracts for the radar CLI."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
from typing import Any

from .protocol import Paper
from .state import paper_id


def paper_record(paper: Paper) -> dict[str, Any]:
    return {
        "id": paper_id(paper),
        "source": paper.source,
        "title": paper.title,
        "authors": paper.authors,
        "abstract": paper.abstract,
        "score": paper.score,
        "summary": paper.tldr,
        "affiliations": paper.affiliations,
        "source_url": paper.url,
        "pdf_url": paper.pdf_url,
    }


def report_document(papers: list[Paper], query: dict[str, Any]) -> dict[str, Any]:
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "query": query,
        "papers": [paper_record(paper) for paper in papers],
    }


def render_markdown(document: dict[str, Any]) -> str:
    query = document["query"]
    lines = ["# Zotero Research Radar", "", f"Generated: {document['generated_at']}", ""]
    lines.append(f"Sources: {', '.join(query['sources'])}")
    lines.append("")
    if not document["papers"]:
        return "\n".join(lines + ["No unseen papers matched this run.", ""])
    for index, paper in enumerate(document["papers"], start=1):
        score = "n/a" if paper["score"] is None else f"{paper['score']:.3f}"
        lines.extend([f"## {index}. {paper['title']}", "", f"Score: {score}", ""])
        if paper["authors"]:
            lines.extend([f"Authors: {', '.join(paper['authors'])}", ""])
        if paper["summary"]:
            lines.extend([paper["summary"], ""])
        elif paper["abstract"]:
            lines.extend([paper["abstract"], ""])
        lines.extend([f"Source: {paper['source_url']}", ""])
        if paper["pdf_url"]:
            lines.extend([f"PDF: {paper['pdf_url']}", ""])
    return "\n".join(lines)


def write_report(document: dict[str, Any], output: str | Path, output_format: str) -> None:
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if output_format == "json":
        path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return
    path.write_text(render_markdown(document), encoding="utf-8")
