#!/usr/bin/env bash
# Upload a local file to Railway OpenClaw volume via SSH in base64 chunks
set -euo pipefail

LOCAL_FILE="$1"
REMOTE_PATH="$2"
CHUNK_SIZE=20000  # ~20KB base64 per chunk (safe for Windows arg limit)

echo "Uploading $(basename "$LOCAL_FILE") -> $REMOTE_PATH"

# Remove any existing file
MSYS_NO_PATHCONV=1 railway ssh "rm -f $REMOTE_PATH" 2>/dev/null || true

# Base64 encode and split into chunks
B64=$(base64 -w0 "$LOCAL_FILE")
TOTAL=${#B64}
OFFSET=0
CHUNK_NUM=0

while [ $OFFSET -lt $TOTAL ]; do
  CHUNK="${B64:$OFFSET:$CHUNK_SIZE}"
  CHUNK_NUM=$((CHUNK_NUM + 1))
  SENT=$((OFFSET + ${#CHUNK}))
  PCT=$((SENT * 100 / TOTAL))
  echo "  chunk $CHUNK_NUM: $SENT/$TOTAL bytes ($PCT%)"

  MSYS_NO_PATHCONV=1 railway ssh "python3 -c 'import base64,sys; open(sys.argv[1],\"ab\").write(base64.b64decode(sys.argv[2]))' $REMOTE_PATH $CHUNK"

  OFFSET=$((OFFSET + CHUNK_SIZE))
done

# Verify
REMOTE_SIZE=$(MSYS_NO_PATHCONV=1 railway ssh "wc -c < $REMOTE_PATH" 2>&1 | tr -d '[:space:]')
LOCAL_SIZE=$(wc -c < "$LOCAL_FILE" | tr -d '[:space:]')
echo "Done. Local: $LOCAL_SIZE bytes, Remote: $REMOTE_SIZE bytes"

if [ "$LOCAL_SIZE" = "$REMOTE_SIZE" ]; then
  echo "OK: sizes match"
else
  echo "WARNING: size mismatch!"
fi
