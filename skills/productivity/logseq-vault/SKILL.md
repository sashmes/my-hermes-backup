---
name: logseq-vault
description: "Manage and search your Logseq second brain graph, append meeting notes, and sync via Git."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [logseq, notes, second-brain, sync, git, productivity]
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

## Technical Workarounds & Troubleshooting

### 1. Avoiding Git Credential Hangs in Automated Scripts
In automated or non-interactive agent environments, Git may hang indefinitely if it prompts for credentials (e.g. if the PAT expires or is incorrect). 
*   **Fix**: Always inject `GIT_TERMINAL_PROMPT=0` into the environment variables when executing Git commands in subprocesses (e.g., `os.environ["GIT_TERMINAL_PROMPT"] = "0"` in Python). This forces Git to fail immediately with a clean stderr message rather than hanging the agent turn.

### 2. Push Failure: "src refspec main does not match any"
This error occurs when you run `git init` on a new server that defaults to the branch name `master` (or doesn't create any branch yet until the first commit), while the remote repository is configured for `main`.
*   **Resolution**:
    1. Rename the local branch to match the remote: `git branch -m master main` (or the corresponding default name).
    2. Set up upstream tracking for the remote branch: `git branch --set-upstream-to=origin/main main`.
    3. Ensure a `.gitignore` is in place to ignore active agent files (`config.json`, scripts, `.gitignore` itself) so that ONLY Logseq markdown content (`journals/`, `pages/`) gets tracked.

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
