"""Durable asynchronous uploader for ITS test-cycle statistics."""

from __future__ import annotations

import json
import sqlite3
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

import requests


DEFAULT_TEST_STATISTICS_PATH = "/api/v1/automation/its-cycle-results"


class ITMSTestStatisticsUploader:
    """Persist cycle results locally and upload them in a background thread."""

    def __init__(
        self,
        api_base_url: str,
        access_key: str,
        queue_file: str,
        api_path: str = DEFAULT_TEST_STATISTICS_PATH,
        timeout: float = 10.0,
        retry_interval: float = 30.0,
    ):
        self.api_base_url = str(api_base_url or "").rstrip("/")
        self.access_key = str(access_key or "").strip()
        self.api_path = str(api_path or DEFAULT_TEST_STATISTICS_PATH).strip()
        self.timeout = max(1.0, float(timeout))
        self.retry_interval = max(5.0, float(retry_interval))
        self.queue_file = Path(queue_file)
        self.queue_file.parent.mkdir(parents=True, exist_ok=True)
        self._stop_event = threading.Event()
        self._wake_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._init_db()

    def _db(self) -> sqlite3.Connection:
        connection = sqlite3.connect(str(self.queue_file), timeout=10)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_db(self) -> None:
        with self._db() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS itms_test_statistics_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_id TEXT NOT NULL UNIQUE,
                    payload TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    attempts INTEGER NOT NULL DEFAULT 0,
                    next_attempt REAL NOT NULL DEFAULT 0,
                    last_error TEXT NOT NULL DEFAULT '',
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
                """
            )

    def _url(self) -> str:
        if self.api_path.startswith(("http://", "https://")):
            return self.api_path
        return f"{self.api_base_url}/{self.api_path.lstrip('/')}"

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._upload_loop,
            name="itms-test-statistics-uploader",
            daemon=True,
        )
        self._thread.start()

    def stop(self, timeout: float = 2.0) -> None:
        self._stop_event.set()
        self._wake_event.set()
        if self._thread:
            self._thread.join(timeout=max(0.1, timeout))
            self._thread = None

    def enqueue(self, payload: Dict[str, Any]) -> str:
        event_id = str(
            payload.get("eventId")
            or f"{payload.get('testTaskId', 'ITS')}:cycle:{payload.get('cycleNo', uuid.uuid4())}"
        )
        payload = dict(payload)
        payload["eventId"] = event_id
        now = datetime.now().isoformat(timespec="seconds")
        with self._db() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO itms_test_statistics_queue
                    (event_id, payload, status, attempts, next_attempt, last_error, created_at, updated_at)
                VALUES (?, ?, 'pending', 0, 0, '', ?, ?)
                """,
                (event_id, json.dumps(payload, ensure_ascii=False), now, now),
            )
        self._wake_event.set()
        return event_id

    def pending_count(self) -> int:
        with self._db() as connection:
            row = connection.execute(
                """
                SELECT COUNT(*) AS count
                FROM itms_test_statistics_queue
                WHERE status != 'uploaded'
                """
            ).fetchone()
        return int(row["count"] if row else 0)

    def _next_item(self) -> Optional[sqlite3.Row]:
        now = time.time()
        with self._db() as connection:
            return connection.execute(
                """
                SELECT *
                FROM itms_test_statistics_queue
                WHERE status != 'uploaded' AND next_attempt <= ?
                ORDER BY id
                LIMIT 1
                """,
                (now,),
            ).fetchone()

    def _mark_uploaded(self, item_id: int) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        with self._db() as connection:
            connection.execute(
                """
                UPDATE itms_test_statistics_queue
                SET status = 'uploaded', updated_at = ?, last_error = ''
                WHERE id = ?
                """,
                (now, item_id),
            )

    def _mark_failed(self, item_id: int, attempts: int, error: str) -> None:
        now = datetime.now().isoformat(timespec="seconds")
        next_attempt = time.time() + min(self.retry_interval * max(1, attempts), 30 * 60)
        with self._db() as connection:
            connection.execute(
                """
                UPDATE itms_test_statistics_queue
                SET status = 'pending', attempts = ?, next_attempt = ?, last_error = ?, updated_at = ?
                WHERE id = ?
                """,
                (attempts, next_attempt, str(error)[:1000], now, item_id),
            )

    def _post(self, payload: Dict[str, Any]) -> None:
        headers = {"Content-Type": "application/json"}
        if self.access_key:
            headers["X-ITMS-Test-Statistics-Key"] = self.access_key

        response = requests.post(
            self._url(),
            json=payload,
            headers=headers,
            timeout=self.timeout,
        )
        if response.status_code == 409:
            return
        response.raise_for_status()
        if not response.content:
            return
        try:
            result = response.json()
        except ValueError:
            return
        if isinstance(result, dict) and "code" in result:
            code = result.get("code")
            if code not in (0, 200, "0", "200"):
                raise RuntimeError(result.get("message") or f"ITMS code={code}")

    def _upload_one(self, item: sqlite3.Row) -> None:
        attempts = int(item["attempts"] or 0) + 1
        try:
            self._post(json.loads(item["payload"]))
        except Exception as error:
            self._mark_failed(int(item["id"]), attempts, error)
            return
        self._mark_uploaded(int(item["id"]))

    def _upload_loop(self) -> None:
        while not self._stop_event.is_set():
            item = self._next_item()
            if item is not None:
                self._upload_one(item)
                continue
            self._wake_event.wait(timeout=1.0)
            self._wake_event.clear()
