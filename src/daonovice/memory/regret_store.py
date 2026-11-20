"""悔恨驱动存储：SQLite 安全短连接。

修复早期版本“全局单连接在 async 下复用”导致的 database is locked 问题：
每次读写都打开独立连接、用完即关，连接不跨任务持有。
"""
from __future__ import annotations

import sqlite3
import time
from pathlib import Path
from typing import Any, Dict, List, Optional


class RegretStore:
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gaps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL,
                    capabilities TEXT,
                    postponed INTEGER,
                    regret_score REAL
                )
                """
            )
            conn.commit()

    def add_gap(self, capabilities: str, regret_score: float, postponed: int = 0) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO gaps (timestamp, capabilities, postponed, regret_score) VALUES (?, ?, ?, ?)",
                (time.time(), capabilities, postponed, regret_score),
            )
            conn.commit()
            return int(cur.lastrowid)

    def fetch_high_score(self, threshold: float) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, timestamp, capabilities, postponed, regret_score "
                "FROM gaps WHERE regret_score > ? ORDER BY regret_score DESC",
                (threshold,),
            ).fetchall()
            return [dict(r) for r in rows]

    def delete_gap(self, gap_id: int) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM gaps WHERE id = ?", (gap_id,))
            conn.commit()

    def count_pending(self, threshold: float) -> int:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM gaps WHERE regret_score > ?", (threshold,)
            ).fetchone()
            return int(row["n"])

    def snapshot(self) -> Optional[Dict[str, Any]]:
        """返回最近悔恨记录，用于自检与仪表盘展示。"""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, timestamp, capabilities, regret_score FROM gaps "
                "ORDER BY regret_score DESC LIMIT 1"
            ).fetchone()
            return dict(row) if row else None
