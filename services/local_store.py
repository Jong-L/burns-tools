from __future__ import annotations

import json
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any


class LocalStore:
    """Single-user local SQLite storage with one-time JSON migration."""

    DB_FILENAME = "burns_tools.db"
    JOURNAL_FILE = "消极思维日志.json"
    COUNT_FILE = "消极思维计数.json"
    DAILY_PLAN_FILE = "每日活动计划表.json"

    AUTOMATIC_THOUGHT_KEY = "下意识思维"
    COGNITIVE_DISTORTION_KEY = "认知扭曲"
    EMOTION_KEY = "情绪"
    RATIONAL_RESPONSE_KEY = "理性回应"
    RESULT_KEY = "结果"
    SITUATION_KEY = "情况"

    def __init__(self, data_dir: str | Path | None = None) -> None:
        base_dir = Path(data_dir) if data_dir is not None else Path(__file__).resolve().parent.parent / "data"
        self.data_dir = base_dir
        self.db_path = self.data_dir / self.DB_FILENAME
        self.initialize()

    def initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            self._create_tables(connection)
            self._migrate_legacy_json(connection)

    def get_journal_logs(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            log_rows = connection.execute(
                """
                SELECT
                    id,
                    type,
                    timestamp,
                    situation,
                    emotion,
                    automatic_thought,
                    rational_response,
                    result
                FROM journal_logs
                ORDER BY
                    CASE WHEN TRIM(COALESCE(rational_response, '')) = '' THEN 0 ELSE 1 END,
                    timestamp ASC
                """
            ).fetchall()

            distortions_by_log_id: dict[int, list[list[str]]] = {}
            distortion_rows = connection.execute(
                """
                SELECT log_id, name, note
                FROM journal_distortions
                ORDER BY log_id, position
                """
            ).fetchall()
            for row in distortion_rows:
                distortions_by_log_id.setdefault(row["log_id"], []).append([row["name"], row["note"] or ""])

        logs: list[dict[str, Any]] = []
        for row in log_rows:
            logs.append(
                {
                    "type": row["type"],
                    "timestamp": row["timestamp"],
                    "data": {
                        self.SITUATION_KEY: row["situation"] or "",
                        self.EMOTION_KEY: row["emotion"] or "",
                        self.AUTOMATIC_THOUGHT_KEY: row["automatic_thought"] or "",
                        self.COGNITIVE_DISTORTION_KEY: distortions_by_log_id.get(row["id"], []),
                        self.RATIONAL_RESPONSE_KEY: row["rational_response"] or "",
                        self.RESULT_KEY: row["result"] or "",
                    },
                }
            )
        return logs

    def upsert_journal_log(self, log_type: str, timestamp: float, data: dict[str, Any]) -> None:
        clean_type = str(log_type).strip() or "three_column"
        clean_timestamp = float(timestamp)
        distortions = self._normalize_distortions(data.get(self.COGNITIVE_DISTORTION_KEY, []))

        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO journal_logs (
                    type,
                    timestamp,
                    situation,
                    emotion,
                    automatic_thought,
                    rational_response,
                    result
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(timestamp) DO UPDATE SET
                    type = excluded.type,
                    situation = excluded.situation,
                    emotion = excluded.emotion,
                    automatic_thought = excluded.automatic_thought,
                    rational_response = excluded.rational_response,
                    result = excluded.result
                """,
                (
                    clean_type,
                    clean_timestamp,
                    self._as_text(data.get(self.SITUATION_KEY, "")),
                    self._as_text(data.get(self.EMOTION_KEY, "")),
                    self._as_text(data.get(self.AUTOMATIC_THOUGHT_KEY, "")),
                    self._as_text(data.get(self.RATIONAL_RESPONSE_KEY, "")),
                    self._as_text(data.get(self.RESULT_KEY, "")),
                ),
            )

            log_id = connection.execute(
                "SELECT id FROM journal_logs WHERE timestamp = ?",
                (clean_timestamp,),
            ).fetchone()["id"]

            connection.execute("DELETE FROM journal_distortions WHERE log_id = ?", (log_id,))
            connection.executemany(
                """
                INSERT INTO journal_distortions (log_id, position, name, note)
                VALUES (?, ?, ?, ?)
                """,
                [
                    (log_id, position, name, note)
                    for position, (name, note) in enumerate(distortions)
                ],
            )

    def delete_journal_log(self, timestamp: float) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM journal_logs WHERE timestamp = ?", (float(timestamp),))

    def get_thought_counts(self) -> dict[str, int]:
        with self._connect() as connection:
            rows = connection.execute(
                "SELECT day, count FROM thought_counts ORDER BY day"
            ).fetchall()
        return {row["day"]: int(row["count"]) for row in rows}

    def save_thought_count(self, day: str, count: int) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                INSERT INTO thought_counts (day, count)
                VALUES (?, ?)
                ON CONFLICT(day) DO UPDATE SET count = excluded.count
                """,
                (day, max(0, int(count))),
            )

    def get_daily_plan(self, day: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT time_slot, plan, actual, mastery_score, pleasure_score
                FROM daily_activity_entries
                WHERE day = ?
                ORDER BY slot_index
                """,
                (day,),
            ).fetchall()
        return [
            {
                "time_slot": row["time_slot"],
                "plan": row["plan"] or "",
                "actual": row["actual"] or "",
                "mastery_score": row["mastery_score"],
                "pleasure_score": row["pleasure_score"],
            }
            for row in rows
        ]

    def save_daily_plan(self, day: str, entries: list[dict[str, Any]]) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM daily_activity_entries WHERE day = ?", (day,))
            connection.executemany(
                """
                INSERT INTO daily_activity_entries (
                    day,
                    slot_index,
                    time_slot,
                    plan,
                    actual,
                    mastery_score,
                    pleasure_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        day,
                        index,
                        self._as_text(entry.get("time_slot", "")),
                        self._as_text(entry.get("plan", "")),
                        self._as_text(entry.get("actual", "")),
                        self._nullable_score(entry.get("mastery_score")),
                        self._nullable_score(entry.get("pleasure_score")),
                    )
                    for index, entry in enumerate(entries)
                ],
            )

    def get_anti_procrastination_entries(self, day: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT
                    activity,
                    predicted_difficulty,
                    predicted_satisfaction,
                    actual_difficulty,
                    actual_satisfaction
                FROM anti_procrastination_entries
                WHERE day = ?
                ORDER BY row_index
                """,
                (day,),
            ).fetchall()
        return [
            {
                "activity": row["activity"] or "",
                "predicted_difficulty": row["predicted_difficulty"],
                "predicted_satisfaction": row["predicted_satisfaction"],
                "actual_difficulty": row["actual_difficulty"],
                "actual_satisfaction": row["actual_satisfaction"],
            }
            for row in rows
        ]

    def save_anti_procrastination_entries(self, day: str, entries: list[dict[str, Any]]) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM anti_procrastination_entries WHERE day = ?", (day,))
            connection.executemany(
                """
                INSERT INTO anti_procrastination_entries (
                    day,
                    row_index,
                    activity,
                    predicted_difficulty,
                    predicted_satisfaction,
                    actual_difficulty,
                    actual_satisfaction
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    (
                        day,
                        index,
                        self._as_text(entry.get("activity", "")),
                        self._nullable_percent(entry.get("predicted_difficulty")),
                        self._nullable_percent(entry.get("predicted_satisfaction")),
                        self._nullable_percent(entry.get("actual_difficulty")),
                        self._nullable_percent(entry.get("actual_satisfaction")),
                    )
                    for index, entry in enumerate(entries)
                ],
            )

    def get_but_rebuttal_entries(self, day: str) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT excuse_text, rebuttal_text
                FROM but_rebuttal_entries
                WHERE day = ?
                ORDER BY row_index
                """,
                (day,),
            ).fetchall()
        return [
            {
                "excuse_text": row["excuse_text"] or "",
                "rebuttal_text": row["rebuttal_text"] or "",
            }
            for row in rows
        ]

    def save_but_rebuttal_entries(self, day: str, entries: list[dict[str, Any]]) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM but_rebuttal_entries WHERE day = ?", (day,))
            connection.executemany(
                """
                INSERT INTO but_rebuttal_entries (
                    day,
                    row_index,
                    excuse_text,
                    rebuttal_text
                )
                VALUES (?, ?, ?, ?)
                """,
                [
                    (
                        day,
                        index,
                        self._as_text(entry.get("excuse_text", "")),
                        self._as_text(entry.get("rebuttal_text", "")),
                    )
                    for index, entry in enumerate(entries)
                ],
            )

    @contextmanager
    def _connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
            connection.commit()
        finally:
            connection.close()

    def _create_tables(self, connection: sqlite3.Connection) -> None:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS journal_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT NOT NULL,
                timestamp REAL NOT NULL UNIQUE,
                situation TEXT NOT NULL DEFAULT '',
                emotion TEXT NOT NULL DEFAULT '',
                automatic_thought TEXT NOT NULL DEFAULT '',
                rational_response TEXT NOT NULL DEFAULT '',
                result TEXT NOT NULL DEFAULT ''
            );

            CREATE TABLE IF NOT EXISTS journal_distortions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_id INTEGER NOT NULL,
                position INTEGER NOT NULL,
                name TEXT NOT NULL,
                note TEXT NOT NULL DEFAULT '',
                FOREIGN KEY(log_id) REFERENCES journal_logs(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS thought_counts (
                day TEXT PRIMARY KEY,
                count INTEGER NOT NULL DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS daily_activity_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                slot_index INTEGER NOT NULL,
                time_slot TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT '',
                actual TEXT NOT NULL DEFAULT '',
                mastery_score INTEGER,
                pleasure_score INTEGER,
                UNIQUE(day, slot_index)
            );

            CREATE TABLE IF NOT EXISTS anti_procrastination_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                row_index INTEGER NOT NULL,
                activity TEXT NOT NULL DEFAULT '',
                predicted_difficulty INTEGER,
                predicted_satisfaction INTEGER,
                actual_difficulty INTEGER,
                actual_satisfaction INTEGER,
                UNIQUE(day, row_index)
            );

            CREATE TABLE IF NOT EXISTS but_rebuttal_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                day TEXT NOT NULL,
                row_index INTEGER NOT NULL,
                excuse_text TEXT NOT NULL DEFAULT '',
                rebuttal_text TEXT NOT NULL DEFAULT '',
                UNIQUE(day, row_index)
            );
            """
        )

    def _migrate_legacy_json(self, connection: sqlite3.Connection) -> None:
        if self._table_is_empty(connection, "journal_logs"):
            self._migrate_journal_json(connection)
        if self._table_is_empty(connection, "thought_counts"):
            self._migrate_count_json(connection)
        if self._table_is_empty(connection, "daily_activity_entries"):
            self._migrate_daily_plan_json(connection)

    def _migrate_journal_json(self, connection: sqlite3.Connection) -> None:
        path = self.data_dir / self.JOURNAL_FILE
        legacy_logs = self._load_json_file(path, default=[])
        if not isinstance(legacy_logs, list):
            return

        for log in legacy_logs:
            if not isinstance(log, dict):
                continue
            timestamp = log.get("timestamp")
            if timestamp is None:
                continue
            self._upsert_journal_log_in_connection(
                connection=connection,
                log_type=str(log.get("type", "three_column")),
                timestamp=float(timestamp),
                data=log.get("data", {}) if isinstance(log.get("data"), dict) else {},
            )

    def _migrate_count_json(self, connection: sqlite3.Connection) -> None:
        path = self.data_dir / self.COUNT_FILE
        legacy_counts = self._load_json_file(path, default={})
        if not isinstance(legacy_counts, dict):
            return

        connection.executemany(
            """
            INSERT INTO thought_counts (day, count)
            VALUES (?, ?)
            ON CONFLICT(day) DO UPDATE SET count = excluded.count
            """,
            [
                (str(day), max(0, int(count)))
                for day, count in legacy_counts.items()
                if self._is_int_like(count)
            ],
        )

    def _migrate_daily_plan_json(self, connection: sqlite3.Connection) -> None:
        path = self.data_dir / self.DAILY_PLAN_FILE
        legacy_plans = self._load_json_file(path, default={})
        if not isinstance(legacy_plans, dict):
            return

        for day, entries in legacy_plans.items():
            if not isinstance(entries, list):
                continue
            connection.executemany(
                """
                INSERT INTO daily_activity_entries (
                    day,
                    slot_index,
                    time_slot,
                    plan,
                    actual,
                    mastery_score,
                    pleasure_score
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(day, slot_index) DO UPDATE SET
                    time_slot = excluded.time_slot,
                    plan = excluded.plan,
                    actual = excluded.actual,
                    mastery_score = excluded.mastery_score,
                    pleasure_score = excluded.pleasure_score
                """,
                [
                    (
                        str(day),
                        index,
                        self._as_text(entry.get("time_slot", "")),
                        self._as_text(entry.get("plan", "")),
                        self._as_text(entry.get("actual", "")),
                        self._nullable_score(entry.get("mastery_score")),
                        self._nullable_score(entry.get("pleasure_score")),
                    )
                    for index, entry in enumerate(entries)
                    if isinstance(entry, dict)
                ],
            )

    def _upsert_journal_log_in_connection(
        self,
        connection: sqlite3.Connection,
        log_type: str,
        timestamp: float,
        data: dict[str, Any],
    ) -> None:
        connection.execute(
            """
            INSERT INTO journal_logs (
                type,
                timestamp,
                situation,
                emotion,
                automatic_thought,
                rational_response,
                result
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(timestamp) DO UPDATE SET
                type = excluded.type,
                situation = excluded.situation,
                emotion = excluded.emotion,
                automatic_thought = excluded.automatic_thought,
                rational_response = excluded.rational_response,
                result = excluded.result
            """,
            (
                log_type,
                timestamp,
                self._as_text(data.get(self.SITUATION_KEY, "")),
                self._as_text(data.get(self.EMOTION_KEY, "")),
                self._as_text(data.get(self.AUTOMATIC_THOUGHT_KEY, "")),
                self._as_text(data.get(self.RATIONAL_RESPONSE_KEY, "")),
                self._as_text(data.get(self.RESULT_KEY, "")),
            ),
        )

        log_id = connection.execute(
            "SELECT id FROM journal_logs WHERE timestamp = ?",
            (timestamp,),
        ).fetchone()["id"]
        connection.execute("DELETE FROM journal_distortions WHERE log_id = ?", (log_id,))
        connection.executemany(
            """
            INSERT INTO journal_distortions (log_id, position, name, note)
            VALUES (?, ?, ?, ?)
            """,
            [
                (log_id, position, name, note)
                for position, (name, note) in enumerate(
                    self._normalize_distortions(data.get(self.COGNITIVE_DISTORTION_KEY, []))
                )
            ],
        )

    @staticmethod
    def _table_is_empty(connection: sqlite3.Connection, table_name: str) -> bool:
        row = connection.execute(f"SELECT COUNT(*) AS count FROM {table_name}").fetchone()
        return row is not None and int(row["count"]) == 0

    @staticmethod
    def _load_json_file(path: Path, default: Any) -> Any:
        if not path.exists() or path.stat().st_size == 0:
            return default
        try:
            with path.open("r", encoding="utf-8") as file:
                return json.load(file)
        except (OSError, json.JSONDecodeError):
            return default

    @staticmethod
    def _normalize_distortions(value: Any) -> list[tuple[str, str]]:
        normalized: list[tuple[str, str]] = []
        if not isinstance(value, list):
            return normalized
        for item in value:
            if isinstance(item, (list, tuple)) and item:
                name = str(item[0]).strip()
                note = str(item[1]).strip() if len(item) > 1 else ""
                if name:
                    normalized.append((name, note))
        return normalized

    @staticmethod
    def _nullable_score(value: Any) -> int | None:
        if value in (None, ""):
            return None
        number = int(value)
        if 0 <= number <= 5:
            return number
        raise ValueError("score must be between 0 and 5")

    @staticmethod
    def _nullable_percent(value: Any) -> int | None:
        if value in (None, ""):
            return None
        number = int(value)
        if 0 <= number <= 100:
            return number
        raise ValueError("percent must be between 0 and 100")

    @staticmethod
    def _as_text(value: Any) -> str:
        return str(value).strip() if value is not None else ""

    @staticmethod
    def _is_int_like(value: Any) -> bool:
        try:
            int(value)
        except (TypeError, ValueError):
            return False
        return True
