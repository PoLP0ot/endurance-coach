#!/bin/bash
# Block dangerous commands
if echo "$CLAUDE_CODE_COMMAND" | grep -qE 'rm -rf|sudo|chmod 777'; then
  echo "BLOCKED: dangerous command" >&2
  exit 1
fi
