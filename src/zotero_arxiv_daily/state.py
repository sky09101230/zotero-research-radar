"""Persistent local state for avoiding repeated recommendations."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from .protocol import Paper


def paper_id(paper: Paper) -> str:
    """Return the stable source identifier used by the local state store."""
    return f"{paper.source}:{paper.url}"


class StateStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS recommendations (
                    paper_id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    first_recommended_at TEXT NOT NULL,
                    last_score REAL
                )
                """
            )
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS feedback (
                    paper_id TEXT PRIMARY KEY,
                    action TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def has_recommendation(self, paper: Paper) -> bool:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT 1 FROM recommendations WHERE paper_id = ?", (paper_id(paper),)
            ).fetchone()
        return row is not None

    def record_recommendations(self, papers: list[Paper]) -> None:
        now = datetime.now(timezone.utc).isoformat()
        rows = [(paper_id(paper), paper.title, now, paper.score) for paper in papers]
        with self._connect() as connection:
            connection.executemany(
                """
                INSERT INTO recommendations (paper_id, title, first_recommended_at, last_score)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET last_score = excluded.last_score
                """,
                rows,
            )

    def record_feedback(self, identifier: str, action: str) -> None:
        now = datetime.now(timezone.utc).isoformat()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO feedback (paper_id, action, updated_at)
                VALUES (?, ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET action = excluded.action, updated_at = excluded.updated_at
                """,
                (identifier, action, now),
            )
