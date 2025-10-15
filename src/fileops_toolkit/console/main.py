"""Command‑line interface for FileOps Toolkit.

This minimal CLI exposes a `scan` command that discovers files in the
configured sources and prints basic metadata.  It serves as an entry
point for further commands such as deduplicate, transfer, verify, etc.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from ..config_loader import load_config
from ..discovery.engine import discover_files
from ..metadata.scanner import get_file_metadata


console = Console()


@click.group()
def cli() -> None:
    """FileOps Toolkit CLI."""
    pass


@cli.command()
@click.option('--config', 'config_path', type=click.Path(exists=True), default='config/config.yml', help='Path to configuration file.')
def scan(config_path: str) -> None:
    """Scan configured sources and display discovered files."""
    cfg = load_config(Path(config_path))
    sources = cfg['sources']
    extensions = cfg['extensions']
    checksum_algo = cfg.get('checksum_algo')

    table = Table(title='Discovered files')
    table.add_column('Path')
    table.add_column('Size (bytes)', justify='right')
    table.add_column('Modified', justify='right')
    table.add_column('Checksum')

    for path in discover_files(sources, extensions):
        meta = get_file_metadata(path, checksum_algo=checksum_algo)
        table.add_row(str(meta.path), str(meta.size_bytes), str(int(meta.mtime)), meta.checksum or '')

    console.print(table)


@cli.command()
@click.option('--config', 'config_path', type=click.Path(exists=True), default='config/config.yml', help='Path to configuration file.')
def show_config(config_path: str) -> None:
    """Print the current configuration."""
    cfg = load_config(Path(config_path))
    console.print_json(json.dumps(cfg, indent=2))


if __name__ == '__main__':  # pragma: no cover
    cli()
