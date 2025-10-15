"""Discovery engine for FileOps Toolkit.

This module provides utilities to recursively search source directories for
files matching a set of extensions.  It yields absolute file paths for
downstream processing.  The current implementation uses Python's
``os.walk`` and is designed to be replaced or augmented with faster tools
such as ``fd``/``fdfind`` via subprocess if desired.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, Iterator, Sequence


def discover_files(sources: Sequence[str], extensions: Sequence[str]) -> Iterator[Path]:
    """Yield paths of files under ``sources`` whose suffix matches ``extensions``.

    Args:
        sources: Iterable of directory paths to search.
        extensions: File suffixes (without leading dot) to include, case‑insensitive.

    Yields:
        ``pathlib.Path`` objects pointing to matching files.

    This function traverses each source directory recursively using ``os.walk``.
    For performance on large directories, consider using the ``fdfind`` tool and
    parsing its output externally.
    """
    normalized_exts = {ext.lower().lstrip('.') for ext in extensions}
    for src in sources:
        for root, _, files in os.walk(src):
            for name in files:
                if name.lower().split('.')[-1] in normalized_exts:
                    yield Path(root) / name
