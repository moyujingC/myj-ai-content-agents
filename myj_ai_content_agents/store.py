"""SQLite 持久化."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .models import ContentUnit, Material, Topic


class ContentStore:
    """内容单元数据存储."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS topics (
                    id TEXT PRIMARY KEY,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS content_units (
                    id TEXT PRIMARY KEY,
                    topic_id TEXT NOT NULL,
                    account_id TEXT NOT NULL,
                    data TEXT NOT NULL,
                    status TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_cu_status ON content_units(status);
                CREATE INDEX IF NOT EXISTS idx_cu_topic ON content_units(topic_id);
                """
            )

    def save_topic(self, topic: Topic) -> None:
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO topics (id, data, created_at) VALUES (?, ?, ?)",
                (topic.id, topic.model_dump_json(), topic.created_at),
            )

    def get_topic(self, topic_id: str) -> Topic | None:
        with self._connect() as conn:
            row = conn.execute("SELECT data FROM topics WHERE id = ?", (topic_id,)).fetchone()
            return Topic.model_validate_json(row["data"]) if row else None

    def save_unit(self, unit: ContentUnit) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO content_units
                (id, topic_id, account_id, data, status, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    unit.id,
                    unit.topic_id,
                    unit.account_id,
                    unit.model_dump_json(),
                    unit.status,
                    unit.created_at,
                    unit.updated_at,
                ),
            )

    def get_unit(self, unit_id: str) -> ContentUnit | None:
        with self._connect() as conn:
            row = conn.execute("SELECT data FROM content_units WHERE id = ?", (unit_id,)).fetchone()
            return ContentUnit.model_validate_json(row["data"]) if row else None

    def list_units(self, status: str | None = None, limit: int = 50) -> list[ContentUnit]:
        with self._connect() as conn:
            if status:
                rows = conn.execute(
                    "SELECT data FROM content_units WHERE status = ? ORDER BY updated_at DESC LIMIT ?",
                    (status, limit),
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT data FROM content_units ORDER BY updated_at DESC LIMIT ?", (limit,)
                ).fetchall()
            return [ContentUnit.model_validate_json(row["data"]) for row in rows]
