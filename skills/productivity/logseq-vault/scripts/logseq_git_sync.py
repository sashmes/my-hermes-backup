#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime

CONFIG_PATH = "/workspace/second-brain/config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def run_git_cmd(args, cwd):
    # Prevent Git from prompting for credentials in non-interactive sessions
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            env=env
        )
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return False, f"Git error: {e.stderr.strip() or e.stdout.strip()}"

def init_git_repo(config):
    vault = config["vault_path"]
    
    # Check if git is initialized
    if not os.path.exists(os.path.join(vault, ".git")):
        print("Initializing new Git repository...")
        success, out = run_git_cmd(["init"], vault)
        if not success:
            return False, out
            
    # Set local configs
    run_git_cmd(["config", "user.name", config["git_username"]], vault)
    run_git_cmd(["config", "user.email", config["git_email"]], vault)
    
    # If remote is set in config, update it
    if config["remote_url"]:
        # Check if remote already exists
        success, out = run_git_cmd(["remote"], vault)
        if success and "origin" in out.split():
            run_git_cmd(["remote", "set-url", "origin", config["remote_url"]], vault)
        else:
            run_git_cmd(["remote", "add", "origin", config["remote_url"]], vault)
            
    return True, "Git repository initialized and configured."

def sync_pull(config):
    vault = config["vault_path"]
    if not os.path.exists(os.path.join(vault, ".git")):
        return False, "Git repository not initialized."
    
    if not config["remote_url"]:
        return True, "No remote configured, skipped pull."
        
    # Fetch and pull
    success, out = run_git_cmd(["fetch", "origin"], vault)
    if not success:
        return False, f"Fetch failed: {out}"
        
    success, out = run_git_cmd(["pull", "origin", config["branch"], "--rebase"], vault)
    if not success:
        return False, f"Pull failed: {out}"
        
    return True, "Successfully pulled changes from remote."

def sync_push(config, commit_msg="Update from Hermes Agent"):
    vault = config["vault_path"]
    if not os.path.exists(os.path.join(vault, ".git")):
        return False, "Git repository not initialized."
        
    # Check if there are changes
    success, status_out = run_git_cmd(["status", "--porcelain"], vault)
    if not success:
        return False, f"Status check failed: {status_out}"
        
    if not status_out:
        return True, "No changes to commit/push."
        
    # Add, commit, push
    success, out = run_git_cmd(["add", "."], vault)
    if not success:
        return False, f"Git add failed: {out}"
        
    success, out = run_git_cmd(["commit", "-m", commit_msg], vault)
    if not success:
        return False, f"Git commit failed: {out}"
        
    if not config["remote_url"]:
        return True, "Committed locally (no remote configured)."
        
    success, out = run_git_cmd(["push", "origin", config["branch"]], vault)
    if not success:
        return False, f"Push failed: {out}"
        
    return True, f"Successfully committed and pushed to remote: {commit_msg}"

def append_to_journal(config, content):
    vault = config["vault_path"]
    journals_dir = os.path.join(vault, "journals")
    os.makedirs(journals_dir, exist_ok=True)
    
    # Load timezone if configured
    from zoneinfo import ZoneInfo
    tz_name = config.get("timezone", "UTC")
    try:
        tz = ZoneInfo(tz_name)
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
        
    # Logseq journal date format is YYYY_MM_DD.md
    today = now.strftime("%Y_%m_%d")
    journal_file = os.path.join(journals_dir, f"{today}.md")
    
    # Sync remote first to get latest notes
    pull_success, pull_msg = sync_pull(config)
    if not pull_success:
        print(f"Warning during sync pull: {pull_msg}")
        
    # Format the node with timestamp
    timestamp = now.strftime("%H:%M")
    formatted_bullet = f"- **{timestamp}**: {content}\n"
    
    # Read existing content to avoid duplicate line or see if empty
    file_exists = os.path.exists(journal_file)
    
    with open(journal_file, "a") as f:
        # If new file, add some frontmatter if needed, or just append
        if not file_exists:
            # Simple Logseq page frontmatter or empty
            pass
        f.write(formatted_bullet)
        
    # Sync push changes
    push_success, push_msg = sync_push(config, f"Add journal entry at {timestamp}")
    return push_success, f"Entry added to journal {today}.md. Push status: {push_msg}"

if __name__ == "__main__":
    config = load_config()
    
    if len(sys.argv) < 2:
        print("Usage: logseq_git_sync.py [init | pull | push | append] [args...]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "init":
        success, msg = init_git_repo(config)
        print(msg)
        sys.exit(0 if success else 1)
        
    elif cmd == "pull":
        success, msg = sync_pull(config)
        print(msg)
        sys.exit(0 if success else 1)
        
    elif cmd == "push":
        msg_arg = sys.argv[2] if len(sys.argv) > 2 else "Manual sync from Hermes"
        success, msg = sync_push(config, msg_arg)
        print(msg)
        sys.exit(0 if success else 1)
        
    elif cmd == "append":
        if len(sys.argv) < 3:
            print("Error: Missing content to append.")
            sys.exit(1)
        content = " ".join(sys.argv[2:])
        success, msg = append_to_journal(config, content)
        print(msg)
        sys.exit(0 if success else 1)
        
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
