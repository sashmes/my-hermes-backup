#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime
from zoneinfo import ZoneInfo

CONFIG_PATH = "/workspace/second-brain/config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def run_git_cmd(args, cwd):
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

def check_time(config):
    tz_name = config.get("timezone", "America/New_York")
    try:
        tz = ZoneInfo(tz_name)
    except Exception:
        tz = ZoneInfo("America/New_York")
        
    now = datetime.now(tz)
    current_hour = now.hour
    
    # We sync at exactly 6:00 AM (hour 6) and 1:00 PM (hour 13)
    if current_hour in [6, 13]:
        return True, now.strftime("%Y-%m-%d %H:%M:%S %Z")
    else:
        return False, now.strftime("%Y-%m-%d %H:%M:%S %Z")

def main():
    config = load_config()
    vault = config["vault_path"]
    
    is_sync_hour, time_str = check_time(config)
    
    # Check if force flag is passed for manual testing
    force = len(sys.argv) > 1 and sys.argv[1] == "--force"
    
    if not is_sync_hour and not force:
        print(f"SKIP_SYNC: Current time {time_str} is not a scheduled sync hour (6:00 AM or 1:00 PM).")
        return
        
    print(f"RUN_SYNC: Sync hour confirmed at {time_str}. Initiating Logseq memory pull...")
    
    # Run pull
    pull_success, pull_msg = run_git_cmd(["pull", "origin", config["branch"], "--rebase"], vault)
    if not pull_success:
        print(f"ERROR_GIT_PULL: {pull_msg}")
        return
        
    print("GIT_PULL_SUCCESS: Successfully pulled latest notes from GitHub.")
    
    # Read files
    user_file = os.path.join(vault, "pages", "hermes_user.md")
    memory_file = os.path.join(vault, "pages", "hermes_memory.md")
    
    print("\n--- hermes_user.md ---")
    if os.path.exists(user_file):
        try:
            with open(user_file, "r", encoding="utf-8") as f:
                print(f.read())
        except Exception as e:
            print(f"ERROR_READ_USER: {e}")
    else:
        print("File not found.")
        
    print("\n--- hermes_memory.md ---")
    if os.path.exists(memory_file):
        try:
            with open(memory_file, "r", encoding="utf-8") as f:
                print(f.read())
        except Exception as e:
            print(f"ERROR_READ_MEMORY: {e}")
    else:
        print("File not found.")

if __name__ == "__main__":
    main()
