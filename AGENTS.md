# 🧠 FileOps Toolkit – Unified File Deduplication & Transfer Framework

**AI/DevOps Training Specification Document**

---

## 🎯 Ümumi Məqsəd

Yüksək performanslı, paralel, təhlükəsiz və idarə olunan fayl deduplikasiya və transfer sistemi yaratmaq. Məqsəd:

- `/mnt/f` və `/mnt/d` kimi mənbələrdəki `.iso` (və digər seçilmiş uzantılı) faylları tapmaq,
- onları `/mnt/e/ISO/` kimi mərkəzi qovluğa toplamaq,
- eyni adlı və ya eyni məzmunlu fayllar üçün ölçü → tarix → hash müqayisəsi aparmaq,
- ən uyğun faylı saxlamaq (digərini köçürməmək və ya backup-dir-ə saxlamaq),
- əməliyyatların hamısını rəngli çıxış, CSV/JSON log, retry/recovery və interaktiv konfiqurasiya menyusu ilə müşayiət etmək.

---

## 🧱 Arxitektura və Modul Dizaynı

| Modul | Təsvir |
| --- | --- |
| **1️⃣ Discovery Engine** | `find` və ya `fdfind` vasitəsilə mənbə qovluqları skan edir, `.iso` və `.ISO` faylları tapır, null-delimited fayl siyahısı çıxarır. |
| **2️⃣ Metadata Scanner** | Hər fayl üçün `stat` məlumatlarını və istəyə görə `xxh128`, `sha1`, `md5` və s. hash dəyərlərini çıxarır. |
| **3️⃣ Deduplication Core** | Eyni ad və ya eyni hash-ə malik faylları aşkar edir və konfiqurasiya siyasətinə əsasən qərar verir (saxla, əvəz et, backup et, atla). |
| **4️⃣ Transfer Engine** | `rsync` və ya `rclone` əsasında paralel köçürmə. Local və ya SSH üzərindən. Retry və partial resume dəstəyi var. |
| **5️⃣ Verification Module** | Köçürülən faylların ölçü və hash uyğunluğunu yoxlayır. |
| **6️⃣ Logging & Analytics** | Bütün əməliyyatlar CSV, JSON və human-readable loglara yazılır. Realtime progress bar və statistikalar göstərilir. |
| **7️⃣ Interactive Console (CLI/TUI)** | İstifadəçi interfeysi — parametrləri dəyişmək, əməliyyatlara nəzarət etmək, logları izləmək. |
| **8️⃣ Supervisor / Scheduler** | Worker-ləri idarə edir, çökmə və retry-ləri nəzarətdə saxlayır, uzunmüddətli əməliyyatları davam etdirir. |

---

## 🧩 Əsas Məntiq (Deduplication Logic)

| Addım | Qayda | Əməliyyat |
| --- | --- | --- |
| 1️⃣ | Fayl adı eynidirsə | Müqayisəyə keç |
| 2️⃣ | Ölçülər fərqlidirsə | Böyük olan qalır |
| 3️⃣ | Ölçülər eynidirsə | Modifikasiya tarixi müqayisə olunur |
| 4️⃣ | Tarixlər eynidirsə | Hash müqayisəsi (`xxh128`, `sha1`, `md5`) aparılır |
| 5️⃣ | Hash eynidirsə | Duplicate — skip və log |
| 6️⃣ | Hash fərqlidirsə | `keep_both_with_suffix` və ya `prefer_newer` siyasəti ilə saxlanılır |

Nəticə hər zaman log və CSV faylında qeyd olunur.

---

## ⚙️ Konfiqurasiya Nümunəsi (`config.yml`)

```yaml
sources:
  - /mnt/f
  - /mnt/d
destination: /mnt/e/ISO
extensions: ['iso', 'ISO']
parallel_workers: 12
checksum_algo: xxh128
deduplication_policy: prefer_newer
transfer_tool: rsync
rsync_args:
  - "-aHAX"
  - "--sparse"
  - "--preallocate"
  - "--partial"
  - "--info=progress2,stats4"
logging:
  dir: /var/log/fileops
  csv_file: operations-$(date +%F_%T).csv
  json_file: summary.json
dry_run: false
verify_after_transfer: true
backup_duplicates_to: /mnt/e/Backup
```

---

## 💻 Interaktiv Menyu (TUI/CLI)

```
╔══════════════════════════════════╗
║       FILEOPS TOOLKIT MENU       ║
╚══════════════════════════════════╝
 1) Start full scan & collect
 2) Dry-run mode (simulation)
 3) Edit configuration (YAML)
 4) Show current progress
 5) Review dedup decisions
 6) View CSV/JSON logs
 7) Manage retry queue
 8) SSH source management
 9) Stop / Resume operations
 0) Exit
```

---

## 📊 CSV Log Format

| Sütun | İzah |
| --- | --- |
| run_id | Cari iş sessiyası ID-si |
| timestamp | UTC vaxtı |
| worker | İcra edən işçi |
| src_path | Mənbə fayl yolu |
| dst_path | Hədəf fayl yolu |
| size_bytes | Fayl ölçüsü |
| mtime_unix | Modifikasiya vaxtı |
| hash | Faylın hash dəyəri |
| decision | copied / skipped / replaced / duplicate |
| reason | size_diff / newer / hash_match / error |
| duration_ms | İşin müddəti |
| rsync_exit | Rsync çıxış kodu |
| error_msg | Səhv baş verdikdə mesaj |

---

## 🧾 Pre-checks (İcra öncəsi yoxlamalar)

- `find`, `rsync`, `xargs` və `xxh*` komandalarının mövcudluğu
- Mənbə və hədəf qovluqların mövcudluğu və icazələri
- Diskdə minimum boş yer (`min_free_bytes`)
- Rsync versiyası və flag dəstəkləri (`--preallocate`, `--mkpath`)
- SSH bağlantısı (əgər uzaq host göstərilibsə)
- Uzaq hostlar üçün `remote_staging_dir` yazıla bilməlidir və parol istifadə olunursa `sshpass` mövcudluğu təsdiqlənməlidir

---

## ⚡ Paralel İş Modeli (Bash versiya üçün nümunə)

```bash
find /mnt/f /mnt/d -type f -iname '*.iso' -print0 |
  xargs -0 -n1 -P 12 /usr/local/bin/iso-worker.sh
```

**iso-worker.sh** faylı isə:

- fayl üçün `stat` toplayır,
- hədəfi yoxlayır,
- müqayisə aparır,
- `rsync` çağırır,
- nəticəni CSV-yə əlavə edir,
- konsola rəngli nəticə verir (`green=success`, `yellow=duplicate`, `red=error`).

---

## 📈 Əməliyyat Axını

```
┌────────────┐
│ Discovery  │
└─────┬──────┘
      │
      ▼
┌──────────────┐
│ Metadata Scan│
└─────┬────────┘
      │
      ▼
┌──────────────┐
│ Dedup Engine │
└─────┬────────┘
      │
      ▼
┌──────────────┐
│ Transfer Core│
└─────┬────────┘
      │
      ▼
┌──────────────┐
│ CSV / Logger │
└──────────────┘
```

---

## 🧰 Tövsiyə Olunan Texnologiyalar

| Səviyyə | Dillər / Kitabxanalar | Xüsusiyyətlər |
| --- | --- | --- |
| 🟢 Bash Edition | find, xargs, rsync, awk, xxh128sum | Minimalist, portativ |
| 🟣 Python Edition | rich, click, xxhash, concurrent.futures, paramiko | Interaktiv CLI, TUI, CSV, çoxlu worker |
| 🟡 Go Edition | cobra, go-xxhash, rsync wrapper | Enterprise səviyyəli, statik binary, çox sürətli |

---

## 🔒 Təhlükəsizlik və Retry Mexanizmləri

- `--remove-source-files` yalnız uğurlu transferdən sonra aktivləşir
- Hər əməliyyat üçün maksimum 3 retry (exponential backoff ilə)
- IO səhvləri `errors.log` faylında qeyd olunur
- `dry-run` rejimi default aktiv olur (istifadəçi təsdiq etməsə, heç nə dəyişmir)
- Backup-dir bütün overwrite əməliyyatlarında istifadə olunur

---

## 🧠 AI Model üçün Təlim Təlimatı (Training Prompt)

> “Develop an AI or automation system that can execute the **FileOps Toolkit** pipeline described above — capable of discovering, deduplicating, transferring, logging, and verifying files across local and remote paths using parallel workers, rsync, and interactive configuration. The system should ensure safety, high performance, recoverability, and full traceability in all operations.”

---

## 🧭 Repository Description (GitHub üçün qısa versiya)

---

## 🔁 Əlavə Funksionallıq (v0.2)

- **Pattern Discovery** — `patterns` və `pattern_mode` (glob/regex) vasitəsilə istənilən fayl maskalarını dəstəkləyir, `pattern_case_sensitive` parametrilə idarə olunur.
- **Əməliyyat Modları** — `operation_mode: flatten` deduplikasiya olunmuş toplama; `operation_mode: mirror` isə qovluq strukturunu olduğu kimi saxlayır (`mirror_prefix_with_root` seçimi ilə).
- **Duplikat Strategiyası** — `duplicates_policy` (`skip`, `archive`, `delete`) və `duplicates_archive_dir` ilə eyni məzmunlu fayllar üçün idarə olunan davranış.
- **Verbosity Profiləri** — CLI çıxışını `minimal`, `standard`, `maximal` rejimlərinə bölür, menyuda da dinamik göstərilir.
- **Interaktiv Konfiq Editoru** — menyuda yeni alt-menyu mənbə/destination/pattern/mode/dry-run kimi parametrləri redaktə edir və çatışmayan qovluqları avtomatik yaradır.
- **Remote Staging & SSH Sync** — `remote_sources`, `remote_rsync_args`, `remote_staging_dir` parametrləri ilə `rsync` üzərindən uzaq hostları lokal keşə gətirir, menyuda idarə olunur, `sshpass` dəstəyi ilə parol/SSH açarı ilə işləyir.
- **ASCII Banner** — CLI açılışında FileOps Toolkit üçün xüsusi ASCII art + müəllif imzası (PierringShot Electronics / github.com/pierringshot).


> 🔧 **FileOps Toolkit** — Modular, parallel, and intelligent file deduplication & transfer system.
> Finds, compares, merges, and verifies large files (ISO, media, archives) with rsync integration, real-time logs, and an interactive console.

---

## 📜 License

MIT License © 2025 — FileOps Toolkit Authors

---

## 🧑‍💻 Contributing

Pull requests və plugin təklifləri açıqdır. İstifadəçi modulları, transfer alətləri və dedup strategiyaları üçün API-lər planlaşdırılıb.

---

İndi sən sadəcə deməlisən:
- “Bash prototipi üçün repo skeleton yarat”  
  yaxud  
- “Python CLI versiyası üçün tam struktur yarat (src/, config/, logs/, setup.py, README.md, LICENSE və s.)”

Hansı versiyanı istəyirsən ki tam işlək GitHub reposu kimi formalaşdıraq?
# FileOps Toolkit – Python CLI Edition

Modular, parallel, and intelligent file deduplication & transfer system described in the training brief.  
The current repository provides a Python-first skeleton with Click/Rich based CLI, pluggable modules, and configuration-driven policies ready to be extended into a production-grade toolkit.

## Repository layout

```
FileOPS-Toolkit/
  src/fileops_toolkit/
    console/        # CLI entrypoints (Rich tables, Click commands, future TUI)
    discovery/      # File discovery walkers (fd/find wrappers welcome)
    metadata/       # Metadata + checksum collection (md5/sha1/xxh128)
    deduplication/  # Policy engine for deciding copy/skip/replace
    transfer/       # rsync-backed transfer utilities with retry hooks
    verification/   # Post-transfer verification helpers
    logging/        # CSV/JSON logging helpers and analytics stubs
    supervisor/     # Worker orchestration + retry scaffolding
    config_loader.py
  config/config.yml # Example configuration mirrors the spec
  logs/             # Runtime logs (ignored by git)
  requirements.txt
  setup.py
  LICENSE
  AGENTS.md         # Full AI/DevOps training specification
```

Every module is intentionally lightweight but documented so new contributors can grow it toward the target behaviour (parallel workers, retries, remote transfer, etc.).

## Architecture overview

| Module | Purpose |
| --- | --- |
| **Discovery Engine** | Scans configured sources (`find`, `fd`, or native walker) and emits candidate files as pathlib paths. |
| **Metadata Scanner** | Collects stat info + checksums (`md5`, `sha1`, `xxh128`) for downstream dedup decisions. |
| **Deduplication Core** | Implements policies such as `prefer_newer` or `keep_both_with_suffix`, comparing name → size → mtime → hash. |
| **Transfer Engine** | Wraps `rsync` (extensible to `rclone`/SSH) with directory pre-creation, retry hooks, and resumable flags. |
| **Verification Module** | Confirms size/hash parity after transfer before marking success. |
| **Logging & Analytics** | Writes CSV/JSON/human logs, intended to back progress dashboards and audit trails. |
| **Interactive Console** | Click/Rich CLI providing scan/show-config today, with placeholders for full menu-driven control. |
| **Supervisor / Scheduler** | Thread-based worker orchestration scaffold; extend with `concurrent.futures`, retry queues, and resume logic. |

## Features roadmap

- Parallel discovery & transfer workers with resumable retries.
- Policy-driven deduplication decisions (size → mtime → hash).
- Rich-powered CLI with colour themes, progress indicators, and verbose toggles.
- Dry-run mode by default; confirmation required before destructive work.
- Backup directory support for overwrite scenarios.
- Future TUI for interactive monitoring and configuration edits.

## CLI usage

The CLI currently exposes `scan`, `show-config`, and `menu`, complete with progress bars, verbose detail toggles, and a colour-off switch. Extend `src/fileops_toolkit/console/main.py` with additional commands for dedup, transfer, verification, etc.

```bash
python -m fileops_toolkit.console.main --help
python -m fileops_toolkit.console.main scan --config config/config.yml
python -m fileops_toolkit.console.main scan --config config/config.yml --verbose
python -m fileops_toolkit.console.main scan --no-color
python -m fileops_toolkit.console.main show-config
python -m fileops_toolkit.console.main menu
```

Running directly from the repository root? Export `PYTHONPATH=src` (or install the package in editable mode) so Python picks up the local modules rather than any previously installed wheel.

Future menu (as per spec) is sketched below for reference:

```
╔══════════════════════════════════╗
║       FILEOPS TOOLKIT MENU       ║
╚══════════════════════════════════╝
 1) Start full scan & collect
 2) Dry-run mode (simulation)
 3) Edit configuration (YAML)
 4) Show current progress
 5) Review dedup decisions
 6) View CSV/JSON logs
 7) Manage retry queue
 8) SSH source management
 9) Stop / Resume operations
 0) Exit
```

## Configuration

`config/config.yml` mirrors the sample in the specification. Adjust paths, policies, or checksum algorithms to suit your environment.

```yaml
sources:
  - /mnt/f
  - /mnt/d
destination: /mnt/e/ISO
extensions: ['iso', 'ISO']
parallel_workers: 12
checksum_algo: xxh128
deduplication_policy: prefer_newer
transfer_tool: rsync
rsync_args:
  - "-aHAX"
  - "--sparse"
  - "--preallocate"
  - "--partial"
  - "--info=progress2,stats4"
logging:
  dir: ./logs
  csv_file: operations-$(date +%F_%T).csv
  json_file: summary.json
dry_run: true
verify_after_transfer: true
backup_duplicates_to: /mnt/e/Backup
```

## Logging format

The logging helper sets up CSV columns ready for full telemetry:

`run_id`, `timestamp`, `worker`, `src_path`, `dst_path`, `size_bytes`, `mtime_unix`, `hash`, `decision`, `reason`, `duration_ms`, `rsync_exit`, `error_msg`.

JSON logs capture serialised `DedupResult` objects for downstream dashboards or analytics.

## Pre-checks

- Ensure `find`, `rsync`, `xargs`, and configured hash utilities are installed.
- Confirm source/destination directories exist with sufficient permissions and free space.
- Validate your `rsync` supports `--preallocate`, `--partial`, `--info=progress2`.
- Test SSH connectivity when remote hosts appear in configuration.

## Example parallel runner (bash sketch)

```bash
find /mnt/f /mnt/d -type f -iname '*.iso' -print0 \
  | xargs -0 -n1 -P 12 /usr/local/bin/iso-worker.sh
```

`iso-worker.sh` should gather metadata, consult dedup policy, invoke `rsync`, append to CSV, and emit color-coded console results (`green=success`, `yellow=duplicate`, `red=error`).

## Workflow snapshot

```
Discovery → Metadata Scan → Dedup Engine → Transfer Core → CSV / Logger → Verification
```

## Getting started

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m fileops_toolkit.console.main scan
```

## License

MIT License © 2025 — FileOps Toolkit Authors
