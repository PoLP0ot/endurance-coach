#!/bin/bash
# Block reading secret files
if echo "$CLAUDE_CODE_FILE" | grep -qE '\.env$|id_rsa|credentials'; then
  echo "BLOCKED: secret file" >&2
  exit 1
fi
