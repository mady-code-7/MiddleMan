"""
database.py

Tracks job status and results in SQLite, per Section 7 of PROJECT_PLAN.md.
Each /process request creates one job row. /download/<job_id> looks up
the row to serve the right compressed file.

Kept deliberately simple: one table, no ORM. This is a solo 3-month
college project, not a production system -- a plain sqlite3 connection
per call is the right amount of complexity here.
"""

import sqlite3
import uuid
from contextlib import contextmanager

DB_PATH = "database.db"


def init_db():
    """Create the jobs table if it doesn't already exist. Safe to call
    every time the app starts."""
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                source_type TEXT NOT NULL,
                original_size INTEGER,
                compressed_size INTEGER,
                compressed_path TEXT,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


@contextmanager
def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def create_job(source_type: str) -> str:
    """Insert a new job row with status 'processing'. Returns the new job_id."""
    job_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            "INSERT INTO jobs (id, status, source_type) VALUES (?, ?, ?)",
            (job_id, "processing", source_type),
        )
        conn.commit()
    return job_id


def mark_job_success(job_id: str, original_size: int, compressed_size: int, compressed_path: str):
    with _connect() as conn:
        conn.execute(
            """
            UPDATE jobs
            SET status = 'done', original_size = ?, compressed_size = ?, compressed_path = ?
            WHERE id = ?
            """,
            (original_size, compressed_size, compressed_path, job_id),
        )
        conn.commit()


def mark_job_failed(job_id: str, error_message: str):
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status = 'failed', error_message = ? WHERE id = ?",
            (error_message, job_id),
        )
        conn.commit()


def get_job(job_id: str):
    """Returns the job row as a dict, or None if it doesn't exist."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
        return dict(row) if row else None
