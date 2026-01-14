"""Persistence layer for storing task history."""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
from contextlib import contextmanager


@dataclass
class ExecutionStepRecord:
    """Record of a single execution step."""

    step_number: int
    description: str
    timestamp: str


@dataclass
class TaskRecord:
    """Record of a completed task."""

    id: Optional[int]
    input_text: str
    output_text: str
    tools_used: list[str]
    execution_steps: list[ExecutionStepRecord]
    created_at: str
    thread_id: str

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "input_text": self.input_text,
            "output_text": self.output_text,
            "tools_used": self.tools_used,
            "execution_steps": [asdict(step) for step in self.execution_steps],
            "created_at": self.created_at,
            "thread_id": self.thread_id,
        }


class TaskStorage:
    """SQLite-based storage for task history."""

    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = Path(db_path)
        self._init_db()

    @contextmanager
    def _get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_db(self):
        """Initialize the database schema."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    input_text TEXT NOT NULL,
                    output_text TEXT NOT NULL,
                    tools_used TEXT NOT NULL,
                    execution_steps TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    thread_id TEXT NOT NULL
                )
            """
            )

    def save_task(self, record: TaskRecord) -> int:
        """Save a task record and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (input_text, output_text, tools_used, execution_steps, created_at, thread_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """,
                (
                    record.input_text,
                    record.output_text,
                    json.dumps(record.tools_used),
                    json.dumps([asdict(step) for step in record.execution_steps]),
                    record.created_at,
                    record.thread_id,
                ),
            )
            return cursor.lastrowid

    def get_task(self, task_id: int) -> Optional[TaskRecord]:
        """Get a specific task by ID."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()

            if row:
                return self._row_to_record(row)
            return None

    def get_all_tasks(self, limit: int = 100, offset: int = 0) -> list[TaskRecord]:
        """Get all tasks with pagination."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()

            return [self._row_to_record(row) for row in rows]

    def get_tasks_by_thread(self, thread_id: str) -> list[TaskRecord]:
        """Get all tasks for a specific thread."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE thread_id = ? ORDER BY created_at DESC",
                (thread_id,),
            ).fetchall()

            return [self._row_to_record(row) for row in rows]

    def delete_task(self, task_id: int) -> bool:
        """Delete a task by ID."""
        with self._get_connection() as conn:
            cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            return cursor.rowcount > 0

    def clear_all(self):
        """Clear all tasks (useful for testing)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM tasks")

    def export_to_json(self, filepath: str):
        """Export all tasks to a JSON file."""
        tasks = self.get_all_tasks(limit=10000)
        with open(filepath, "w") as f:
            json.dump([task.to_dict() for task in tasks], f, indent=2)

    def _row_to_record(self, row: sqlite3.Row) -> TaskRecord:
        """Convert a database row to a TaskRecord."""
        steps_data = json.loads(row["execution_steps"])
        return TaskRecord(
            id=row["id"],
            input_text=row["input_text"],
            output_text=row["output_text"],
            tools_used=json.loads(row["tools_used"]),
            execution_steps=[ExecutionStepRecord(**step) for step in steps_data],
            created_at=row["created_at"],
            thread_id=row["thread_id"],
        )
