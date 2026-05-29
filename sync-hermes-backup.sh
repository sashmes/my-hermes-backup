#!/usr/bin/env bash
set -euo pipefail

SRC="/home/agentuser/.hermes"
DST="/home/agentuser/hermes-backup"

mkdir -p "$DST"

rsync -a --delete \
  --exclude=".env" \
  --exclude="auth.lock" \
  --exclude="gateway.lock" \
  --exclude="gateway.pid" \
  --exclude="gateway_state.json" \
  --exclude="channel_directory.json" \
  --exclude="logs/" \
  --exclude="audio_cache/" \
  --exclude="image_cache/" \
  --exclude="cache/" \
  --exclude="hermes-agent/" \
  --exclude="node_modules/" \
  --exclude="__pycache__/" \
  "$SRC/config.yaml" \
  "$SRC/SOUL.md" \
  "$SRC/cron" \
  "$SRC/memories" \
  "$SRC/skills" \
  "$DST/"

cd "$DST"
git add .
if ! git diff --cached --quiet; then
  git commit -m "Hermes backup: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
else
  echo "No Hermes backup changes to commit."
fi

if git remote get-url origin >/dev/null 2>&1; then
  git push
else
  echo "No GitHub remote configured yet; local backup is complete."
fi
