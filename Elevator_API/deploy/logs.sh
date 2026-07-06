#!/bin/bash
# View logs from the remote server

REMOTE_HOST="${REMOTE_HOST:-dell-cloudflare}"
REMOTE_USER="${REMOTE_USER:-$USER}"
SERVICE_NAME="elevator-system"

echo "Viewing logs from ${REMOTE_HOST}..."
echo "Press Ctrl+C to exit"
echo ""

ssh -t "${REMOTE_USER}@${REMOTE_HOST}" "sudo journalctl -u ${SERVICE_NAME} -f --no-pager"
