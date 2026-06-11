---
name: logseq-vault
description: "Manage and search your Logseq second brain graph, append meeting notes, and sync via Git."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [logseq, notes, second-brain, sync, git, productivity, cron, timezone]
---

# Logseq Vault Management

This skill handles managing, appending to, and searching a Logseq "second brain" graph hosted on this server and synchronized via Git.

## Vault Location
The canonical path of the Logseq graph is:
`/workspace/second-brain`

Journals are stored under `/workspace/second-brain/journals/` and page files under `/workspace/second-brain/pages/`.

## Appending to Daily Journal
To add a new note, thought, clipping, meeting note, or message to today's daily journal page, run:
```bash
/workspace/second-brain/logseq_git_sync.py append "Your note content"
```
This script will automatically:
1. Try to pull the latest changes from the Git remote to avoid conflicts.
2. Format the bullet point with a timestamp (`- **HH:MM**: Your note content`).
3. Append it to today's journal file (formatted as `YYYY_MM_DD.md` under `journals/`).
4. Commit and push the changes to the Git remote repository.

## Searching the Vault
To search across the entire second brain (both journals and pages), run:
```bash
/workspace/second-brain/logseq_search.py search "keyword/query"
```
This is extremely fast and outputs matched files and lines with line numbers.

## Viewing Recent Notes
To inspect recent daily journals and see what's been captured, run:
```bash
/workspace/second-brain/logseq_search.py recent [limit]
```
Where `limit` is the number of recent journals to show (defaults to 5).

## Manual Git Sync
If you need to manually pull or push the vault:
- **Pull**: `/workspace/second-brain/logseq_git_sync.py pull`
- **Push**: `/workspace/second-brain/logseq_git_sync.py push "Commit Message"`

## Outliner Format Conventions (Logseq spec)
Logseq is a bulleted outliner. Every top-level node and block must start with a bullet `- `.
- Use `[[Page Name]]` syntax to link to another page.
- Use `#tag-name` or `[[tag-name]]` for tags.
- Use `TODO` or `LATER` (all caps) at the start of a bullet to define a task:
  `- TODO Read this article #reading`
- Block indentation (tab / spaces) creates a hierarchical outline:
  ```markdown
  - Main topic
    - Sub-bullet with more details
    - Another detail
  ```

## Durable Automation & Memory Integration
To maintain a high-precision, low-clutter environment:
1. **Durable Memory Synchronization**: We maintain a bi-directional sync cron job `Logseq Memory Sync` (job_id: `cbed372c3598`) running every hour (`0 * * * *`). It uses `scripts/logseq_memory_sync.py` to check the timezone. At exactly 06:00 and 13:00 local New York time, it:
   - Git-pulls the latest changes from the remote.
   - Reads `pages/hermes_user.md` and `pages/hermes_memory.md`.
   - Ingests new preferences and memories into our server-side SQLite store.
   - Overwrites the markdown pages with the complete, updated server-side database.
   - Git-pushes the files back so they synchronize seamlessly to the user's laptop and phone.
2. **Resource Ingestion Rule**: Always automatically draft, generate, and populate a structured `Summary [AI Generated]` block whenever the user asks to add or ingest a new reading, bookmark, article, or resource asset into the Logseq second-brain vault.
3. **Communication Channel Preference**: The user prefers a single, unified gateway channel (specifically, their Telegram cloud server bot) to capture information and coordinate with their notes to prevent the distraction of juggling multiple messaging platforms or bots. Always favor this channel.


## Bi-directional Memory & Preference Sync
To maintain a unified context across separate Hermes instances (e.g., local laptop assistant vs. remote server-hosted gateway), set up a bi-directional memory bridge:
1.  **Ingest (Pull Phase)**:
    *   Pull the latest commits from the Git remote.
    *   Read the contents of `/pages/hermes_user.md` (user preferences) and `/pages/hermes_memory.md` (learned memories).
    *   Ingest the preferences and memories into the server-side persistent database (SQLite) using semantic deduplication to avoid redundant entries.
2.  **Export (Push Phase)**:
    *   Fetch the complete, unified state of your active database memories.
    *   Overwrite `/pages/hermes_user.md` and `/pages/hermes_memory.md` with the newly compiled lists, structured cleanly in Logseq outliner bullets.
    *   Commit and push these updated files back to GitHub.
3.  **Automation**:
    *   Deploy this loop as an hourly cron job (`0 * * * *`) that dynamically filters for the user's specific local hours (e.g., exactly 6:00 AM and 1:00 PM) to ensure timezone-safe alignment.

---

## Linked Files & Assets
This skill includes built-in scripts and templates to enable fast and robust setups:
*   `templates/config.json` — Starter configuration file.
*   `templates/Life_OS_Dashboard_Mockup.html` — Gorgeous, glassmorphic, dotted-background dashboard mockup with centered FOCUS/CAPTURE/PLAN tabs.
*   `scripts/logseq_git_sync.py` — Verbatim background git pull/push/append script.
*   `scripts/logseq_search.py` — Fast file & content regex search tool.
*   `scripts/logseq_memory_sync.py` — Double-daily memory pulling and printing check.
*   `scripts/dream_sequence.py` — Automated orphan-detection, health lint, and operational ledger log script.
*   `scripts/run_web_server.py` — Fully featured python REST API server to serve real Logseq data to the web dashboard.

---

## Pitfalls & Critical Learnings

### 1. Server Timezone Mismatch (UTC vs User)
*   **The Pitfall**: Servers run on UTC, while users are typically in different local timezones (e.g. `America/New_York`). If you resolve dates using `datetime.now()`, the server may write to a future date file (e.g., `2026_06_01.md` instead of `2026_05_31.md`), causing the notes to be hidden from the user's current daily journal view in Logseq.
*   **The Fix**: Always resolve dates using the user's local timezone. Configure `"timezone": "America/New_York"` in `config.json` and use:
    ```python
    from zoneinfo import ZoneInfo
    now = datetime.now(ZoneInfo(tz_name))
    ```

### 2. Interactive Git Prompts Prevention
*   **The Pitfall**: When Git operations are run from background processes, cron jobs, or non-interactive terminals, any authentication failure will prompt for user credentials, causing the subprocess to hang indefinitely and block the agent queue.
*   **The Fix**: Always copy `os.environ` and explicitly set `env["GIT_TERMINAL_PROMPT"] = "0"` in the subprocess runner so Git fails fast on credential errors rather than blocking.

### 3. Git Ignore Security Rules
*   **The Pitfall**: Committing local config files (like `config.json` holding raw tokens), SSH keys (`id_rsa`), or helper scripts to the user's repository creates clutter and security risks.
*   **The Fix**: Immediately write a `.gitignore` to explicitly ignore `.gitignore`, `config.json`, `*.py`, `*.sh`, `id_rsa`, and `venv/`. The user's GitHub repository should only contain raw markdown graph pages (`journals/` and `pages/`).

### 4. Hourly Timezone-Safe Cron Filtering
*   **The Pitfall**: Scheduling a cron job for specific hours (e.g., daily at 6 AM) using UTC triggers will drift when the user's local time shifts during Daylight Saving transitions (EST vs EDT).
*   **The Fix**: Set the cron scheduler to trigger every hour (`0 * * * *`). At the start of the execution, run a Python check to see if the current local hour in `America/New_York` is exactly the target hour (e.g. 6 or 13), and exit cleanly if not. This ensures zero drift and saves CPU/token costs.

### 5. Logseq Graph Fragmentation and Orphan Pages
*   **The Pitfall**: As a self-improving second brain grows, pages can become fragmented, orphaned (having 0 inbound links), or filled with empty structures. In standard RAG, these are dead weight; in Logseq, they clutter the index.
*   **The Fix**: Deploy a python maintenance script (`scripts/dream_sequence.py`) that scans the graph pages, parses markdown link structures, detects orphans, and appends a `#orphan` tag to their first bullet node. This allows the user to easily review and link them to core pillars during weekly reviews.


## Andrej Karpathy's LLM Wiki Pattern
Rather than relying on narrow, raw RAG (retrieval-augmented generation) which only fetches isolated blocks on-the-fly, a self-improving knowledge base uses an LLM to incrementally compile, structure, and link flat-file markdown notes.
*   **The Operating Manual (`HERMES.md`)**: Lives in the root directory (one level above the graph) and defines standard naming structures, formatting conventions, and automation cron parameters.
*   **System Files**: Exactly three tracking pages inside the `pages/` directory:
    *   `system.index.md` — Active master index of all namespaces.
    *   `system.log.md` — Append-only operational ledger using standard timestamps.
    *   `system.processed.md` — Clean registry of raw source files that have been integrated.
*   **Assets Storeroom (`assets/storeroom/`)**: Immutable raw ingestion directory for untouched web clips and notes.

## High-Performance Glassmorphic Dashboard Design
For a truly commanding, minimalistic "Operations Center" dashboard:
1.  **3-Button Master Control**: Collapse complex layouts into three centered, uppercase, bracketless tab controls: **`FOCUS`** (daily tasks & habits), **`CAPTURE`** (inbox clips & logs), and **`PLAN`** (projects & strategic goals).
2.  **Extended Sidebar Layout**: On the `FOCUS` tab, run a full-length, vertical `CALENDAR` on the left edge (with integrated Schedule/Week/Month views) and a curated, highly refined `DAILY BRIEF` on the right edge. Keep your main actionable lists centered.
3.  **Dotted Matrix Background**: Translate React dotted background layouts into high-performance SVG code: `#215769` dots spaced at exactly `12px` (2.4px dot size) with radial vignette and inner glow overlays. Style cards with frosted glass (`bg-slate-950/40` and `backdrop-blur-sm`) so the matrix grid subtly shines through!

