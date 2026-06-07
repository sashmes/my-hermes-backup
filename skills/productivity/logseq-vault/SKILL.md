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

---

## Linked Files & Assets
This skill includes built-in scripts and templates to enable fast and robust setups:
*   `templates/config.json` — Starter configuration file.
*   `scripts/logseq_git_sync.py` — Verbatim background git pull/push/append script.
*   `scripts/logseq_search.py` — Fast file & content regex search tool.
*   `scripts/logseq_memory_sync.py` — Double-daily memory pulling and printing check.

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
