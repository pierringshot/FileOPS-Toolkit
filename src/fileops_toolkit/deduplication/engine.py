"""Deduplication engine for FileOps Toolkit.

Implements simple policies for resolving duplicates based on file name,
size, modification time and checksum.  This is a stub designed to be
extended; it currently performs a basic selection of the preferred file
and returns a list of decisions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict, Iterable, List

from ..metadata.scanner import FileMetadata


class Decision(Enum):
    COPY = auto()
    SKIP = auto()
    REPLACE = auto()
    DUPLICATE = auto()


@dataclass
class DedupResult:
    src: FileMetadata
    dst_exists: bool
    decision: Decision
    reason: str


def deduplicate(files: Iterable[FileMetadata], policy: str = 'prefer_newer') -> List[DedupResult]:
    """Perform deduplication over an iterable of ``FileMetadata``.

    This naive implementation groups files by basename and picks the largest
    file or the newest file according to the selected ``policy``.  It
    produces a list of ``DedupResult`` entries indicating what action
    should be taken.  Real implementations should also consult existing
    destination directories to decide whether to replace or skip.

    Args:
        files: Iterable of file metadata objects.
        policy: ``prefer_newer`` or ``keep_both_with_suffix``.

    Returns:
        List of deduplication results.
    """
    grouped: Dict[str, List[FileMetadata]] = {}
    for meta in files:
        grouped.setdefault(meta.path.name, []).append(meta)
    results: List[DedupResult] = []
    for name, metas in grouped.items():
        if len(metas) == 1:
            results.append(DedupResult(src=metas[0], dst_exists=False, decision=Decision.COPY, reason='unique'))
            continue
        if policy == 'prefer_newer':
            chosen = max(metas, key=lambda m: (m.size_bytes, m.mtime))
            for meta in metas:
                if meta is chosen:
                    results.append(DedupResult(src=meta, dst_exists=False, decision=Decision.COPY, reason='chosen'))
                else:
                    results.append(DedupResult(src=meta, dst_exists=False, decision=Decision.DUPLICATE, reason='duplicate'))
        elif policy == 'keep_both_with_suffix':
            for meta in metas:
                results.append(DedupResult(src=meta, dst_exists=False, decision=Decision.COPY, reason='keep_both'))
        else:
            raise ValueError(f'Unknown policy {policy}')
    return results
