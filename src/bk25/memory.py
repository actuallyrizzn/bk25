from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional


class ConversationMemory:
    def __init__(self, db_path: str = "./data/bk25.db") -> None:
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._ensure_db()

    def _ensure_db(self) -> None:
        data_dir = Path(self.db_path).parent
        data_dir.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self) -> None:
        assert self._conn is not None
        cur = self._conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS automations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                description TEXT NOT NULL,
                script TEXT NOT NULL,
                documentation TEXT,
                filename TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                used_count INTEGER DEFAULT 0
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT NOT NULL,
                frequency INTEGER DEFAULT 1,
                last_used DATETIME DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self._conn.commit()

    async def add_message(self, role: str, content: str, context: Dict[str, Any]) -> int:
        assert self._conn is not None
        cur = self._conn.cursor()
        cur.execute(
            "INSERT INTO conversations (role, content, context) VALUES (?, ?, ?)",
            (role, content, json_dumps(context)),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    async def get_recent_messages(self, limit: int = 10) -> List[Dict[str, Any]]:
        assert self._conn is not None
        cur = self._conn.cursor()
        cur.execute(
            "SELECT role, content, context, timestamp FROM conversations ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        )
        rows = cur.fetchall()
        # Reverse to chronological order
        messages = [
            {
                "role": row["role"],
                "content": row["content"],
                "context": json_loads(row["context"]) if row["context"] else {},
                "timestamp": row["timestamp"],
            }
            for row in rows[::-1]
        ]
        return messages

    async def add_automation(self, automation: Dict[str, Any]) -> int:
        assert self._conn is not None
        cur = self._conn.cursor()
        cur.execute(
            """
            INSERT INTO automations (platform, description, script, documentation, filename)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                automation.get("platform"),
                automation.get("description"),
                automation.get("script"),
                automation.get("documentation", ""),
                automation.get("filename", ""),
            ),
        )
        self._conn.commit()
        return int(cur.lastrowid)

    async def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None


def json_dumps(obj: Any) -> str:
    import json

    return json.dumps(obj, separators=(",", ":"))


def json_loads(s: str) -> Any:
    import json

    return json.loads(s)

