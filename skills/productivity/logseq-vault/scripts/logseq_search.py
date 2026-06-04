#!/usr/bin/env python3
import os
import sys
import json
import glob
import re

CONFIG_PATH = "/workspace/second-brain/config.json"

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
        sys.exit(1)

def search_notes(config, query, case_sensitive=False):
    vault = config["vault_path"]
    pattern = re.compile(query if case_sensitive else query, re.IGNORECASE)
    matches = []
    
    # Search both journals and pages
    search_paths = [
        os.path.join(vault, "journals", "*.md"),
        os.path.join(vault, "pages", "*.md")
    ]
    
    for path_pattern in search_paths:
        for file_path in glob.glob(path_pattern):
            rel_path = os.path.relpath(file_path, vault)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                    
                for idx, line in enumerate(lines):
                    if pattern.search(line):
                        matches.append({
                            "file": rel_path,
                            "line_num": idx + 1,
                            "text": line.strip()
                        })
            except Exception as e:
                # Silently ignore read errors
                pass
                
    return matches

def get_recent_journals(config, limit=5):
    vault = config["vault_path"]
    journals_dir = os.path.join(vault, "journals")
    if not os.path.exists(journals_dir):
        return []
        
    journal_files = glob.glob(os.path.join(journals_dir, "*.md"))
    # Sort files by name (which is date YYYY_MM_DD.md) in descending order
    journal_files.sort(reverse=True)
    
    recent = []
    for file_path in journal_files[:limit]:
        filename = os.path.basename(file_path)
        date_str = filename.replace(".md", "").replace("_", "-")
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            recent.append({
                "date": date_str,
                "file": os.path.relpath(file_path, vault),
                "content": content
            })
        except Exception:
            pass
            
    return recent

if __name__ == "__main__":
    config = load_config()
    
    if len(sys.argv) < 2:
        print("Usage: logseq_search.py [search | recent] [query/limit]")
        sys.exit(1)
        
    cmd = sys.argv[1]
    
    if cmd == "search":
        if len(sys.argv) < 3:
            print("Error: Missing search query.")
            sys.exit(1)
        query = " ".join(sys.argv[2:])
        results = search_notes(config, query)
        
        if not results:
            print(f"No matches found for '{query}'.")
        else:
            print(f"Found {len(results)} matches for '{query}':")
            # Group by file
            by_file = {}
            for r in results:
                by_file.setdefault(r["file"], []).append(r)
                
            for file, items in by_file.items():
                print(f"\n--- {file} ---")
                for item in items:
                    print(f"  Line {item['line_num']}: {item['text']}")
                    
    elif cmd == "recent":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        journals = get_recent_journals(config, limit)
        if not journals:
            print("No journals found.")
        for j in journals:
            print(f"\n==================== Journal: {j['date']} ====================")
            print(j["content"].strip())
            
    else:
        print(f"Unknown command: {cmd}")
        sys.exit(1)
