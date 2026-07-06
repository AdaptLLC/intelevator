#!/bin/bash
# Deployment script for Elevator System Python Backend
# Deploys to remote SSH server (dell-cloudflare dev server)

set -e  # Exit on error

# Configuration
REMOTE_HOST="${REMOTE_HOST:-dell-cloudflare}"
REMOTE_USER="${REMOTE_USER:-$USER}"
REMOTE_PATH="${REMOTE_PATH:-/opt/elevator-system}"
SERVICE_NAME="elevator-system"
SERVICE_PORT="${SERVICE_PORT:-8000}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the backend directory
if [ ! -f "pyproject.toml" ]; then
    log_error "Must be run from backend/ directory"
    exit 1
fi

log_info "Starting deployment to ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}"

# Step 1: Test SSH connection
log_info "Testing SSH connection..."
if ! ssh -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" "echo 'SSH connection successful'" > /dev/null 2>&1; then
    log_error "Cannot connect to ${REMOTE_USER}@${REMOTE_HOST}"
    log_error "Check your SSH configuration or use: ssh ${REMOTE_USER}@${REMOTE_HOST}"
    exit 1
fi
log_info "SSH connection verified"

# Step 2: Create remote directory structure
log_info "Setting up remote directory structure..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" "sudo mkdir -p ${REMOTE_PATH} && sudo chown ${REMOTE_USER}:${REMOTE_USER} ${REMOTE_PATH}"

# Step 3: Sync files (excluding venv, __pycache__, .env)
log_info "Syncing files to remote server..."
rsync -avz \
    --exclude 'venv/' \
    --exclude '.venv/' \
    --exclude '__pycache__/' \
    --exclude '*.pyc' \
    --exclude '.env' \
    --exclude '.git/' \
    --delete \
    ./ "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/"

log_info "Files synced successfully"

# Step 4: Install dependencies and set up environment
log_info "Installing dependencies on remote server..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" bash << 'REMOTE_SCRIPT'
set -e

REMOTE_PATH="${REMOTE_PATH:-/opt/elevator-system}"
cd "${REMOTE_PATH}"

# Check if Python 3.11+ is available
if ! command -v python3.11 &> /dev/null; then
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    else
        echo "Error: Python 3.11+ not found"
        exit 1
    fi
else
    PYTHON_CMD="python3.11"
fi

echo "Using Python: $($PYTHON_CMD --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON_CMD -m venv venv
fi

# Activate and install dependencies
source venv/bin/activate

# Try to install uv for faster package management
if ! command -v uv &> /dev/null; then
    echo "Installing uv (fast package manager)..."
    pip install --quiet uv || echo "Could not install uv, falling back to pip"
fi

# Install the package
if command -v uv &> /dev/null; then
    echo "Installing with uv..."
    uv pip install -e .
else
    echo "Installing with pip..."
    pip install -e .
fi

echo "Dependencies installed successfully"
REMOTE_SCRIPT

log_info "Dependencies installed"

# Step 5: Check if .env file exists on remote
log_info "Checking environment configuration..."
if ! ssh "${REMOTE_USER}@${REMOTE_HOST}" "test -f ${REMOTE_PATH}/.env"; then
    log_warn ".env file not found on remote server"
    log_warn "Copying .env.example as template..."
    ssh "${REMOTE_USER}@${REMOTE_HOST}" "cd ${REMOTE_PATH} && cp .env.example .env"
    log_warn "Please edit ${REMOTE_PATH}/.env with your configuration:"
    log_warn "  ssh ${REMOTE_USER}@${REMOTE_HOST}"
    log_warn "  nano ${REMOTE_PATH}/.env"
    log_warn "  # Set RESEND_API_KEY and other values"
else
    log_info ".env file exists on remote server"
fi

# Step 6: Deploy systemd service
log_info "Deploying systemd service..."
scp deploy/elevator-system.service "${REMOTE_USER}@${REMOTE_HOST}:/tmp/"

ssh "${REMOTE_USER}@${REMOTE_HOST}" bash << REMOTE_SCRIPT
set -e

REMOTE_PATH="${REMOTE_PATH:-/opt/elevator-system}"
SERVICE_NAME="elevator-system"

# Update the service file with actual paths and user
sudo sed -i "s|/opt/elevator-system|${REMOTE_PATH}|g" /tmp/elevator-system.service
sudo sed -i "s|User=.*|User=${REMOTE_USER}|g" /tmp/elevator-system.service
sudo sed -i "s|Group=.*|Group=${REMOTE_USER}|g" /tmp/elevator-system.service

# Move service file
sudo mv /tmp/elevator-system.service /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

echo "Systemd service deployed"
REMOTE_SCRIPT

log_info "Systemd service deployed"

# Step 7: Start or restart the service
log_info "Starting service..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" bash << REMOTE_SCRIPT
set -e

SERVICE_NAME="elevator-system"

# Enable service to start on boot
sudo systemctl enable ${SERVICE_NAME}

# Restart service
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo "Restarting existing service..."
    sudo systemctl restart ${SERVICE_NAME}
else
    echo "Starting new service..."
    sudo systemctl start ${SERVICE_NAME}
fi

# Wait a moment for service to start
sleep 2

# Check service status
if sudo systemctl is-active --quiet ${SERVICE_NAME}; then
    echo "Service is running"
    sudo systemctl status ${SERVICE_NAME} --no-pager
else
    echo "Service failed to start"
    sudo journalctl -u ${SERVICE_NAME} -n 50 --no-pager
    exit 1
fi
REMOTE_SCRIPT

log_info "Service started successfully"

# Step 8: Display connection information
log_info "Deployment complete!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
log_info "Service is running on ${REMOTE_HOST}:${SERVICE_PORT}"
echo ""
echo "Useful commands:"
echo "  • View logs:    ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo journalctl -u ${SERVICE_NAME} -f'"
echo "  • Check status: ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl status ${SERVICE_NAME}'"
echo "  • Restart:      ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl restart ${SERVICE_NAME}'"
echo "  • Stop:         ssh ${REMOTE_USER}@${REMOTE_HOST} 'sudo systemctl stop ${SERVICE_NAME}'"
echo ""
echo "Configure nginx reverse proxy with:"
echo "  • Deploy nginx: ./deploy/deploy-nginx.sh"
echo ""
echo "Access the application:"
echo "  • Health check:     http://${REMOTE_HOST}:${SERVICE_PORT}/health"
echo "  • GraphQL:          http://${REMOTE_HOST}:${SERVICE_PORT}/graphql"
echo "  • API:              http://${REMOTE_HOST}:${SERVICE_PORT}/api/*"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
