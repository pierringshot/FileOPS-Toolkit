"""Metadata scanning for FileOps Toolkit.

Collects filesystem metadata and optional checksums for files discovered
by the discovery engine.  Hash algorithms are selected via configuration.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

try:
    import xxhash
except ImportError:  # pragma: no cover
    xxhash = None  # type: ignore


@dataclass
class FileMetadata:
    path: Path
    size_bytes: int
    mtime: float
    checksum: Optional[str] = None


def compute_checksum(path: Path, algo: str) -> str:
    """Compute a checksum of a file using the given algorithm.

    Supported algorithms: ``md5``, ``sha1``, ``xxh128`` (requires ``xxhash``).
    """
    if algo.lower() == 'md5':
        h = hashlib.md5()
    elif algo.lower() == 'sha1':
        h = hashlib.sha1()
    elif algo.lower() == 'xxh128':
        if xxhash is None:
            raise RuntimeError('xxhash module not installed')
        h = xxhash.xxh3_128()
    else:
        raise ValueError(f'Unsupported checksum algorithm: {algo}')
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()


def get_file_metadata(path: Path, checksum_algo: Optional[str] = None) -> FileMetadata:
    """Gather file metadata and optional checksum.

    Args:
        path: The file path.
        checksum_algo: Name of checksum algorithm to compute (or ``None`` to skip).

    Returns:
        ``FileMetadata`` with size, modification time and optional checksum.
    """
    stat = path.stat()
    checksum = compute_checksum(path, checksum_algo) if checksum_algo else None
    return FileMetadata(
        path=path,
        size_bytes=stat.st_size,
        mtime=stat.st_mtime,
        checksum=checksum,
    )
