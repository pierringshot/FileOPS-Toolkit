"""Verification module for FileOps Toolkit.

After files are transferred, this module checks that the destination file
matches the source file in size and (optionally) checksum.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from ..metadata.scanner import compute_checksum


def verify_file(src: Path, dst: Path, checksum_algo: Optional[str] = None) -> bool:
    """Verify that ``dst`` matches ``src``.

    This function checks that the file sizes match and, if a checksum
    algorithm is provided, that the checksums are identical.  Returns
    ``True`` if verification succeeds, otherwise ``False``.
    """
    try:
        if src.stat().st_size != dst.stat().st_size:
            return False
        if checksum_algo:
            return compute_checksum(src, checksum_algo) == compute_checksum(dst, checksum_algo)
        return True
    except FileNotFoundError:
        return False
