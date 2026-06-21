#!/bin/sh
# Claude Code working-state signal for Hermes to poll (no TUI parsing).
# Writes /tmp/claude-state.json as {"status":"working"|"idle"|"prompt","ts":<unix_ms>}.
# Usage: claude-state.sh <working|idle|prompt> [target_file]
status="$1"
target="${2:-/tmp/claude-state.json}"

case "$status" in
  working | idle | prompt) ;;
  *)
    echo "claude-state.sh: invalid status '$status' (expected working|idle|prompt)" >&2
    exit 2
    ;;
esac

printf '{"status":"%s","ts":%s}\n' "$status" "$(date +%s%3N)" > "$target"
