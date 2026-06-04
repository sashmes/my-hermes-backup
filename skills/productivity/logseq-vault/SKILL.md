---
name: logseq-vault
description: "Manage and search your Logseq second brain graph, append meeting notes, and sync via Git."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [logseq, notes, second-brain, sync, git, productivity, timezone]
---

# Logseq Vault Management

This skill handles managing, appending to, and searching a Logseq "second brain" graph hosted on this server and synchronized via Git.

## Vault Location
The canonical path of the Logseq graph is:
`/workspace/second-brain`

Journals are stored under `/workspace/second-brain/journals/` and page files under `/workspace/second-brain/pages/`.

## Appending to Daily Journal
To add a new note, thought, clipping, meeting note, or message to today's daily journal page, run the sync script:
```bash
/home/agentuser/.hermes/skills/productivity/logseq-vault/scripts/logseq_git_sync.py append "Your note content"
```
This script will automatically:
1. Try to pull the latest changes from the Git remote to avoid conflicts.
2. Format the bullet point with a timestamp (`- **HH:MM**: Your note content`).
3. Append it to today's journal file (formatted as `YYYY_MM_DD.md` under `journals/`).
4. Commit and push the changes to the Git remote repository.

## Searching the Vault
To search across the entire second brain (both journals and pages), run:
```bash
/home/agentuser/.hermes/skills/productivity/logseq-vault/scripts/logseq_search.py search "keyword/query"
```
This is extremely fast and outputs matched files and lines with line numbers.

## Viewing Recent Notes
To inspect recent daily journals and see what's been captured, run:
```bash
/home/agentuser/.hermes/skills/productivity/logseq-vault/scripts/logseq_search.py recent [limit]
```
Where `limit` is the number of recent journals to show (defaults to 5).

## Manual Git Sync
If you need to manually pull or push the vault:
- **Pull**: `logseq_git_sync.py pull`
- **Push**: `logseq_git_sync.py push "Commit Message"`

---

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

## Technical Pitfalls & Troubleshooting

### 1. Timezone Mismatches (UTC vs Local)
*   **The Problem**: Headless servers run in UTC. If the server is in UTC (e.g., June 1st) and the user's laptop/phone is in EDT (e.g., May 31st), writing a note using `datetime.now()` will create a file for tomorrow (`2026_06_01.md`). The user will not see it on their current Logseq dashboard because it is in the "future".
*   **The Solution**: Configure `"timezone"` (e.g., `"America/New_York"`) in `config.json` and resolve datetime using Python's standard `zoneinfo` module:
    ```python
    from zoneinfo import ZoneInfo
    tz = ZoneInfo(config.get("timezone", "UTC"))
    now = datetime.now(tz)
    ```

### 2. Git Prompts Freezing Background Sessions
*   **The Problem**: If a private Git repository fails authentication, Git will prompt for credentials. In headless/gateway runs, this will block the session and freeze the agent process.
*   **The Solution**: Always copy the current environment and set `GIT_TERMINAL_PROMPT = "0"` before running Git subprocesses to force immediate non-interactive failure instead of hanging:
    ```python
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    subprocess.run(["git"] + args, env=env, ...)
    ```

### 3. Git Branch Mismatches (master vs main)
*   **The Problem**: A freshly initialized repository (`git init`) might default to `master`, whereas the remote GitHub repository uses `main`, resulting in push errors like `src refspec main does not match any`.
*   **The Solution**: Rename the local branch immediately and track the remote upstream during initialization:
    ```bash
    git branch -m master main
    git branch --set-upstream-to=origin/main main
    ```

---

## Agentic Life Operating System (@LOS) Plan
The vault structure is designed to support the **Pillars, Pipelines, and Vaults (PPV)** framework by August Bradley.
*   **Pillars**: Page directory prefix `pillar/` (e.g., `[[pillar/Business]]`). High-level domains of life.
*   **Pipelines**:
    *   **Goals**: Targets prefixed with `goal/` (e.g., `[[goal/Build-SaaS]]`).
    *   **Projects**: Specific, time-bound initiatives prefixed with `project/` (e.g., `[[project/OAuth-Service]]`).
    *   **Tasks**: Standard outliner bullets starting with `- TODO` or `- DOING` mapped to their respective project pages via double-brackets `#[[project/OAuth-Service]]`.
*   **Vaults**: Long-term resources prefixed with `vault/` (e.g., `[[vault/Prompt-Stacking]]`). Used for knowledge curation.
