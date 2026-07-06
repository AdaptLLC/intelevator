#!/bin/bash
# Deploy nginx configuration for Elevator System

set -e

# Configuration
REMOTE_HOST="${REMOTE_HOST:-dell-cloudflare}"
REMOTE_USER="${REMOTE_USER:-$USER}"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_info "Deploying nginx configuration to ${REMOTE_HOST}"

# Check if nginx config file exists
if [ ! -f "deploy/nginx-elevator-system.conf" ]; then
    log_error "nginx config file not found: deploy/nginx-elevator-system.conf"
    exit 1
fi

# Copy nginx config to remote
log_info "Copying nginx configuration..."
scp deploy/nginx-elevator-system.conf "${REMOTE_USER}@${REMOTE_HOST}:/tmp/"

# Install and configure nginx on remote
ssh "${REMOTE_USER}@${REMOTE_HOST}" bash << 'REMOTE_SCRIPT'
set -e

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Nginx not found. Installing..."
    sudo apt-get update
    sudo apt-get install -y nginx
fi

# Move config file
sudo mv /tmp/nginx-elevator-system.conf /etc/nginx/sites-available/elevator-system

# Enable site
sudo ln -sf /etc/nginx/sites-available/elevator-system /etc/nginx/sites-enabled/

# Remove default site if it exists
if [ -f /etc/nginx/sites-enabled/default ]; then
    echo "Disabling default nginx site..."
    sudo rm -f /etc/nginx/sites-enabled/default
fi

# Test nginx configuration
echo "Testing nginx configuration..."
sudo nginx -t

# Reload nginx
echo "Reloading nginx..."
sudo systemctl reload nginx

# Enable nginx to start on boot
sudo systemctl enable nginx

echo "Nginx configuration deployed successfully"
REMOTE_SCRIPT

log_info "Nginx deployed successfully!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_info "Nginx is now proxying to the Python backend"
echo ""
echo "Access the application:"
echo "  • Health check:     http://${REMOTE_HOST}/health"
echo "  • GraphQL:          http://${REMOTE_HOST}/graphql"
echo "  • API:              http://${REMOTE_HOST}/api/*"
echo "  • Frontend:         http://${REMOTE_HOST}/"
echo ""
echo "Nginx commands:"
echo "  • View logs:        ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo tail -f /var/log/nginx/elevator-system-access.log'"
echo "  • Check status:     ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl status nginx'"
echo "  • Reload:           ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl reload nginx'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
