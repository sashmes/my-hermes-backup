#!/usr/bin/env python3
"""
Fetch a YouTube video transcript and output it as structured JSON.

Usage:
    python fetch_transcript.py <url_or_video_id> [--language en,tr] [--timestamps]

Output (JSON):
    {
        "video_id": "...",
        "language": "en",
        "segments": [{"text": "...", "start": 0.0, "duration": 2.5}, ...],
        "full_text": "complete transcript as plain text",
        "timestamped_text": "00:00 first line\n00:05 second line\n..."
    }

Install dependency:  pip install youtube-transcript-api
"""

import argparse
import json
import re
import sys
import socket
import urllib.request
import random


def extract_video_id(url_or_id: str) -> str:
    """Extract the 11-character video ID from various YouTube URL formats."""
    url_or_id = url_or_id.strip()
    patterns = [
        r'(?:v=|youtu\.be/|shorts/|embed/|live/)([a-zA-Z0-9_-]{11})',
        r'^([a-zA-Z0-9_-]{11})$',
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id


def format_timestamp(seconds: float) -> str:
    """Convert seconds to HH:MM:SS or MM:SS format."""
    total = int(seconds)
    h, remainder = divmod(total, 3600)
    m, s = divmod(remainder, 60)
    if h > 0:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def fetch_transcript_with_proxies(video_id: str, languages: list = None):
    """Fallback method to fetch transcripts via public proxies when direct fetching is blocked."""
    print("Direct transcript retrieval blocked. Initiating fast proxy fallback...", file=sys.stderr)
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api.proxies import GenericProxyConfig
    except ImportError:
        return None

    # Set short global socket timeout so dead proxies fail fast
    original_timeout = socket.getdefaulttimeout()
    socket.setdefaulttimeout(3.0)

    # Download a reliable public HTTP proxy list
    proxy_url = "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt"
    try:
        req = urllib.request.Request(proxy_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8.0) as response:
            content = response.read().decode('utf-8')
            proxies = [line.strip() for line in content.split('\n') if line.strip()]
    except Exception as e:
        print(f"Failed to fetch proxy list: {e}", file=sys.stderr)
        socket.setdefaulttimeout(original_timeout)
        return None

    random.shuffle(proxies)
    print(f"Downloaded {len(proxies)} proxies. Trying up to 100...", file=sys.stderr)

    for idx, proxy in enumerate(proxies[:100]):
        proxy_href = f"http://{proxy}"
        proxy_config = GenericProxyConfig(http_url=proxy_href, https_url=proxy_href)
        try:
            api = YouTubeTranscriptApi(proxy_config=proxy_config)
            if languages:
                result = api.fetch(video_id, languages=languages)
            else:
                result = api.fetch(video_id)
            
            print(f"Proxy attempt {idx+1} succeeded with {proxy}!", file=sys.stderr)
            socket.setdefaulttimeout(original_timeout)
            return result
        except Exception:
            # Silent fail for individual proxies to keep output clean
            continue

    socket.setdefaulttimeout(original_timeout)
    print("All proxy attempts failed.", file=sys.stderr)
    return None


def fetch_transcript(video_id: str, languages: list = None):
    """Fetch transcript segments from YouTube.

    Returns a list of dicts with 'text', 'start', and 'duration' keys.
    Compatible with youtube-transcript-api v1.x.
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        print("Error: youtube-transcript-api not installed. Run: pip install youtube-transcript-api",
              file=sys.stderr)
        sys.exit(1)

    api = YouTubeTranscriptApi()
    
    # Try fetching directly first
    try:
        if languages:
            result = api.fetch(video_id, languages=languages)
        else:
            result = api.fetch(video_id)
    except Exception as e:
        err_str = str(e).lower()
        # If blocked or experiencing bot detection, try proxy fallback
        if "blocked" in err_str or "bot" in err_str or "login" in err_str or "cookies" in err_str or "unplayable" in err_str:
            result = fetch_transcript_with_proxies(video_id, languages)
            if not result:
                raise e
        else:
            raise e

    # v1.x returns FetchedTranscriptSnippet objects; normalize to dicts
    return [
        {"text": seg.text, "start": seg.start, "duration": seg.duration}
        for seg in result
    ]


def main():
    parser = argparse.ArgumentParser(description="Fetch YouTube transcript as JSON")
    parser.add_argument("url", help="YouTube URL or video ID")
    parser.add_argument("--language", "-l", default=None,
                        help="Comma-separated language codes (e.g. en,tr). Default: auto")
    parser.add_argument("--timestamps", "-t", action="store_true",
                        help="Include timestamped text in output")
    parser.add_argument("--text-only", action="store_true",
                        help="Output plain text instead of JSON")
    args = parser.parse_args()

    video_id = extract_video_id(args.url)
    languages = [l.strip() for l in args.language.split(",")] if args.language else None

    try:
        segments = fetch_transcript(video_id, languages)
    except Exception as e:
        error_msg = str(e)
        if "disabled" in error_msg.lower():
            print(json.dumps({"error": "Transcripts are disabled for this video."}))
        elif "no transcript" in error_msg.lower():
            print(json.dumps({"error": f"No transcript found. Try specifying a language with --language."}))
        else:
            print(json.dumps({"error": error_msg}))
        sys.exit(1)

    full_text = " ".join(seg["text"] for seg in segments)
    timestamped = "\n".join(
        f"{format_timestamp(seg['start'])} {seg['text']}" for seg in segments
    )

    if args.text_only:
        print(timestamped if args.timestamps else full_text)
        return

    result = {
        "video_id": video_id,
        "segment_count": len(segments),
        "duration": format_timestamp(segments[-1]["start"] + segments[-1]["duration"]) if segments else "0:00",
        "full_text": full_text,
    }
    if args.timestamps:
        result["timestamped_text"] = timestamped

    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
