"""Transfer engine for FileOps Toolkit.

Wraps file copying and remote transfer operations.  By default this
implementation uses ``rsync`` via subprocess for local transfers.  More
advanced implementations may integrate ``rclone`` or SSH transfers using
Paramiko.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Iterable, Optional


def transfer_file(src: Path, dst: Path, tool: str = 'rsync', args: Optional[Iterable[str]] = None) -> int:
    """Transfer a single file from ``src`` to ``dst`` using the specified tool.

    Args:
        src: Source file path.
        dst: Destination file path.
        tool: Transfer tool, currently only ``rsync`` is supported.
        args: Additional arguments to pass to the transfer command.

    Returns:
        The exit code of the transfer command.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    if tool == 'rsync':
        cmd = ['rsync']
        if args:
            cmd.extend(args)
        cmd.extend([str(src), str(dst)])
        result = subprocess.run(cmd, capture_output=True)
        return result.returncode
    else:
        raise ValueError(f'Unsupported transfer tool: {tool}')
