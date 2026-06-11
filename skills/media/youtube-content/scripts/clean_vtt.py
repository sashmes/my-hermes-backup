#!/usr/bin/env python3
import sys
import re

def clean_vtt_line(line):
    # Strip word-level sub-timestamps and markup (e.g. <00:00:00.960><c> text </c>)
    line = re.sub(r'<[^>]+>', '', line)
    return line.strip()

def parse_youtube_vtt(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cues = []
    current_cue = []
    is_text = False
    
    for line in lines:
        line_stripped = line.strip()
        if not line_stripped:
            continue
        if '-->' in line_stripped:
            is_text = True
            if current_cue:
                cues.append(current_cue)
                current_cue = []
            continue
        if line_stripped.startswith('WEBVTT') or line_stripped.startswith('Kind:') or line_stripped.startswith('Language:'):
            is_text = False
            continue
        if is_text:
            cleaned = clean_vtt_line(line)
            if cleaned:
                current_cue.append(cleaned)
                
    if current_cue:
        cues.append(current_cue)
        
    # De-duplicate overlapping progressive speech-captions
    clean_lines = []
    for cue in cues:
        for line in cue:
            if not clean_lines or clean_lines[-1] != line:
                # Deduplicate lines appearing in the local rolling window
                if line not in clean_lines[-5:]:
                    clean_lines.append(line)
                    
    return clean_lines

def main():
    if len(sys.argv) < 2:
        print("Usage: clean_vtt.py <path_to_vtt_file> [output_file]")
        sys.exit(1)
        
    vtt_path = sys.argv[1]
    try:
        cleaned = parse_youtube_vtt(vtt_path)
        out_text = "\n".join(cleaned)
        
        if len(sys.argv) > 2:
            with open(sys.argv[2], 'w', encoding='utf-8') as out_f:
                out_f.write(out_text)
            print(f"Cleaned transcript written to {sys.argv[2]}")
        else:
            print(out_text)
    except Exception as e:
        print(f"Error parsing VTT: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
