#!/usr/bin/env python3
import os
import sys
import json
import glob
import re
import subprocess
from datetime import datetime

DIRECTORY = "/workspace/second-brain"
CONFIG_PATH = os.path.join(DIRECTORY, "config.json")

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

def find_orphans(pages_dir, files):
    pages_map = {}
    for f in files:
        base = os.path.basename(f).replace(".md", "")
        pages_map[base.lower()] = base

    inbound_counts = {p: 0 for p in pages_map}

    link_pattern = re.compile(r'\[\[(.*?)\]\]')
    tag_pattern = re.compile(r'#(\S+)')

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
                
            filename = os.path.basename(file_path).lower()
            if "system.index" in filename or "system.log" in filename or "system.processed" in filename:
                continue

            for link in link_pattern.findall(content):
                clean_link = link.split("/")[-1].lower()
                if clean_link in inbound_counts:
                    inbound_counts[clean_link] += 1

            for tag in tag_pattern.findall(content):
                clean_tag = tag.replace("[[", "").replace("]]", "").split("/")[-1].lower()
                if clean_tag in inbound_counts:
                    inbound_counts[clean_tag] += 1
        except Exception:
            pass

    orphans = [pages_map[p] for p, count in inbound_counts.items() if count == 0 and p not in ["brain", "templates", "life_os_dashboard"]]
    return orphans

def update_index_and_log(vault, orphans):
    log_file = os.path.join(vault, "pages", "system.log.md")
    today_str = datetime.now().strftime("%Y-%m-%d")

    try:
        with open(log_file, "r", encoding="utf-8") as f:
            log_content = f.read()
            
        new_log_entry = f"\t\t- ### [{today_str}] dream - Automated Dream Sequence maintenance run\n"
        
        if "## Log Ledger" in log_content:
            log_content = log_content.replace("## Log Ledger\n\t  collapsed:: false\n", f"## Log Ledger\n\t  collapsed:: false\n{new_log_entry}")
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(log_content)
    except Exception as e:
        print(f"Error updating log: {e}")

    if orphans:
        for orphan in orphans:
            path = os.path.join(vault, "pages", f"{orphan}.md")
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "#orphan" not in content:
                    lines = content.splitlines()
                    if len(lines) > 0 and lines[0].startswith("- "):
                        lines[0] = lines[0] + " #orphan"
                    else:
                        lines.append("- #orphan")
                    with open(path, "w", encoding="utf-8") as f:
                        f.write("\n".join(lines) + "\n")
            except Exception as e:
                pass

def main():
    config = load_config()
    vault = config["vault_path"]
    pages_dir = os.path.join(vault, "pages")
    
    run_git_cmd(["pull", "origin", config["branch"], "--rebase"], vault)
    
    files = glob.glob(os.path.join(pages_dir, "*.md"))
    orphans = find_orphans(pages_dir, files)
    update_index_and_log(vault, orphans)
    
    run_git_cmd(["add", "."], vault)
    success, commit_msg = run_git_cmd(["commit", "-m", f"dream - Automated Dream Sequence {datetime.now().strftime('%Y-%m-%d')}"], vault)
    if success:
        run_git_cmd(["push", "origin", config["branch"]], vault)
