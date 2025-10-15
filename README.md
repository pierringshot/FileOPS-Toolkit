# FileOps Toolkit – Python CLI Version

This repository contains a Python implementation of the **FileOps Toolkit**, a modular framework for high‑performance file discovery, deduplication, transfer and verification.  The design is based on the training specification provided, and aims to provide a solid starting point for building a fully functional tool with a command‑line interface and future TUI support.

## Project layout

```
FileOPS-Toolkit/
  versions/v1/
    src/
      fileops_toolkit/
        discovery/          # file discovery utilities
        metadata/           # metadata and checksum extraction
        deduplication/      # deduplication logic and policies
        transfer/           # parallel transfer engine (rsync/rclone wrappers)
        verification/       # verification routines for transferred files
        logging/            # unified logging to CSV/JSON and console
        console/            # CLI interface built with Click/Rich
        supervisor/         # worker supervision and scheduling
    config/
      config.yml            # example configuration file
    logs/                   # runtime logs will be written here
    LICENSE
    setup.py
    README.md               # you are here
```

The `src/fileops_toolkit` package is broken down into modules that align with the architecture described in the training document.  Each module currently contains stubs and placeholders; you can fill in the implementation details incrementally.

## Getting started

1. **Install dependencies** – the toolkit uses standard libraries only, but you may wish to install third‑party packages such as `rich` and `click` for a better CLI experience:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install rich click xxhash paramiko
   ```

2. **Configure sources and policies** – edit `config/config.yml` to define your source directories, destination, deduplication policy and other options.  See the file for an example.

3. **Run the CLI** – a basic entrypoint is provided in `src/fileops_toolkit/console/main.py`.  You can execute it with:

   ```bash
   python -m fileops_toolkit.console.main --help
   ```

This will show the available commands.  The default implementation includes a simple `scan` command for discovery and metadata collection.

## License

This project is provided under the MIT License.  See `LICENSE` for details.
