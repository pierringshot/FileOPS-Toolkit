"""Logging utilities for FileOps Toolkit.

Provides simple helpers to write CSV and JSON logs for operations.  The
``CSVLogger`` writes each record immediately, while ``JSONLogger`` stores
records in a list and writes them to disk when flushed.
"""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Iterable, List

from ..deduplication.engine import DedupResult


class CSVLogger:
    def __init__(self, path: Path, fieldnames: Iterable[str]):
        self.path = path
        self.file = path.open('w', newline='', encoding='utf-8')
        self.writer = csv.DictWriter(self.file, fieldnames=fieldnames)
        self.writer.writeheader()

    def log_result(self, result: DedupResult, run_id: str, worker: str) -> None:
        record = {
            'run_id': run_id,
            'timestamp': result.src.mtime,
            'worker': worker,
            'src_path': str(result.src.path),
            'dst_path': '',
            'size_bytes': result.src.size_bytes,
            'mtime_unix': result.src.mtime,
            'hash': result.src.checksum or '',
            'decision': result.decision.name.lower(),
            'reason': result.reason,
            'duration_ms': '',
            'rsync_exit': '',
            'error_msg': '',
        }
        self.writer.writerow(record)
        self.file.flush()

    def close(self) -> None:
        self.file.close()


class JSONLogger:
    def __init__(self, path: Path):
        self.path = path
        self.records: List[Any] = []

    def add_record(self, result: DedupResult) -> None:
        self.records.append(asdict(result))

    def flush(self) -> None:
        with self.path.open('w', encoding='utf-8') as f:
            json.dump(self.records, f, indent=2)
