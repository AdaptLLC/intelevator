#!/bin/bash
# Restart the service on the remote server

REMOTE_HOST="${REMOTE_HOST:-dell-cloudflare}"
REMOTE_USER="${REMOTE_USER:-$USER}"
SERVICE_NAME="elevator-system"

echo "Restarting service on ${REMOTE_HOST}..."

ssh "${REMOTE_USER}@${REMOTE_HOST}" "sudo systemctl restart ${SERVICE_NAME}"

echo "Waiting for service to start..."
sleep 3

ssh "${REMOTE_USER}@${REMOTE_HOST}" bash << REMOTE_SCRIPT
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo "✅ Service restarted successfully"
    sudo systemctl status ${SERVICE_NAME} --no-pager
else
    echo "❌ Service failed to restart"
    sudo journalctl -u ${SERVICE_NAME} -n 30 --no-pager
    exit 1
fi
REMOTE_SCRIPT
