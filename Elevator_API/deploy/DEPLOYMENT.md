# Deployment Guide - Dell Cloudflare Dev Server

Complete guide for deploying the Python backend to the dell-cloudflare dev server via SSH.

## Prerequisites

### Local Machine
- SSH access to dell-cloudflare server
- rsync installed
- SSH key configured for passwordless login (recommended)

### Remote Server (dell-cloudflare)
- Ubuntu/Debian Linux
- Python 3.11 or higher
- sudo access
- Ports 80 and 8000 available

## Quick Start

### Step 1: Configure SSH

Test your SSH connection:
```bash
ssh dell-cloudflare
```

If the connection fails, configure SSH:
```bash
# Edit SSH config
nano ~/.ssh/config

# Add this configuration:
Host dell-cloudflare
    HostName <server-ip-or-hostname>
    User <your-username>
    Port 22
    IdentityFile ~/.ssh/id_rsa
```

### Step 2: Deploy the Backend

From the `backend/` directory:

```bash
cd backend

# Deploy with default settings
./deploy/deploy.sh

# Or with custom settings
REMOTE_HOST=dell-cloudflare \
REMOTE_USER=aaron \
REMOTE_PATH=/opt/elevator-system \
SERVICE_PORT=8000 \
./deploy/deploy.sh
```

The deployment script will:
1. ✅ Test SSH connection
2. ✅ Create remote directory structure
3. ✅ Sync files to remote server
4. ✅ Install Python dependencies (with UV if available)
5. ✅ Create .env file if needed
6. ✅ Deploy systemd service
7. ✅ Start the service

### Step 3: Configure Environment

On first deployment, edit the environment file:

```bash
ssh dell-cloudflare
nano /opt/elevator-system/.env
```

Required configuration:
```env
PORT=8000
ACCESS_CODE=suffolkproto2025
PASSWORD_EXPIRY=2025-08-31T23:59:59

# IMPORTANT: Set your Resend API key
RESEND_API_KEY=re_your_actual_key_here
ADMIN_EMAIL=aaronjdrake@adapt-llc.com

CORS_ORIGINS=["*"]
```

After editing, restart the service:
```bash
./deploy/restart.sh
```

### Step 4: Deploy Nginx (Optional but Recommended)

Set up nginx as a reverse proxy:

```bash
./deploy/deploy-nginx.sh
```

This provides:
- Standard HTTP port (80) access
- WebSocket support for GraphQL subscriptions
- Better logging and monitoring
- SSL/TLS termination (if configured)

## Deployment Scripts

### Main Deployment

**deploy.sh** - Full deployment (sync + install + restart)
```bash
./deploy/deploy.sh
```

Environment variables:
- `REMOTE_HOST` - SSH hostname (default: dell-cloudflare)
- `REMOTE_USER` - SSH username (default: $USER)
- `REMOTE_PATH` - Installation path (default: /opt/elevator-system)
- `SERVICE_PORT` - Port number (default: 8000)

### Nginx Deployment

**deploy-nginx.sh** - Deploy nginx reverse proxy
```bash
./deploy/deploy-nginx.sh
```

### Management Scripts

**status.sh** - Check service status and health
```bash
./deploy/status.sh
```

**logs.sh** - View live logs (follow mode)
```bash
./deploy/logs.sh
```

**restart.sh** - Restart the service
```bash
./deploy/restart.sh
```

## Manual Operations

### SSH into Server

```bash
ssh dell-cloudflare
```

### Service Management

```bash
# Check status
sudo systemctl status elevator-system

# Start service
sudo systemctl start elevator-system

# Stop service
sudo systemctl stop elevator-system

# Restart service
sudo systemctl restart elevator-system

# Enable on boot
sudo systemctl enable elevator-system

# Disable on boot
sudo systemctl disable elevator-system
```

### View Logs

```bash
# Live logs (follow)
sudo journalctl -u elevator-system -f

# Last 100 lines
sudo journalctl -u elevator-system -n 100

# Logs from today
sudo journalctl -u elevator-system --since today

# Logs with timestamps
sudo journalctl -u elevator-system -o short-iso
```

### Update Code

```bash
# From local machine
cd backend
./deploy/deploy.sh

# Or manually on server
ssh dell-cloudflare
cd /opt/elevator-system
git pull  # if using git
source venv/bin/activate
pip install -e .
sudo systemctl restart elevator-system
```

### Edit Configuration

```bash
ssh dell-cloudflare
nano /opt/elevator-system/.env

# After changes, restart
sudo systemctl restart elevator-system
```

## Directory Structure on Server

```
/opt/elevator-system/
├── app/                    # Python application code
│   ├── main.py
│   ├── schema.py
│   ├── models.py
│   ├── state.py
│   ├── algorithm.py
│   ├── config.py
│   └── notifications.py
├── venv/                   # Virtual environment
├── deploy/                 # Deployment scripts
├── .env                    # Environment configuration (SECRET)
├── pyproject.toml
├── requirements.txt
└── README.md
```

## Systemd Service

The service is installed at `/etc/systemd/system/elevator-system.service`

Configuration:
- **User**: Your SSH user (e.g., aaron)
- **Working Directory**: /opt/elevator-system
- **Port**: 8000 (configurable)
- **Auto-restart**: Yes, with 10s delay
- **Logs**: journald (use `journalctl`)

## Nginx Configuration

Nginx config at `/etc/nginx/sites-available/elevator-system`

Features:
- Port 80 reverse proxy to port 8000
- WebSocket support for GraphQL subscriptions
- Request buffering optimization
- Access and error logging

Nginx logs:
- Access: `/var/log/nginx/elevator-system-access.log`
- Error: `/var/log/nginx/elevator-system-error.log`

View nginx logs:
```bash
ssh dell-cloudflare 'sudo tail -f /var/log/nginx/elevator-system-access.log'
```

## Accessing the Application

### Direct Access (Port 8000)

```
http://dell-cloudflare:8000/health         # Health check
http://dell-cloudflare:8000/graphql        # GraphQL playground
http://dell-cloudflare:8000/api/           # REST API
http://dell-cloudflare:8000/               # Frontend
```

### Through Nginx (Port 80)

```
http://dell-cloudflare/health              # Health check
http://dell-cloudflare/graphql             # GraphQL playground
http://dell-cloudflare/api/                # REST API
http://dell-cloudflare/                    # Frontend
```

## Health Checks

### From Local Machine

```bash
# Check if service is responding
curl http://dell-cloudflare:8000/health

# Expected response:
# {"status":"healthy","version":"2.0.0"}
```

### From Server

```bash
ssh dell-cloudflare 'curl -s http://localhost:8000/health | python3 -m json.tool'
```

### Automated Monitoring

Set up a cron job for health checks:

```bash
ssh dell-cloudflare

# Edit crontab
crontab -e

# Add health check every 5 minutes
*/5 * * * * curl -sf http://localhost:8000/health > /dev/null || systemctl restart elevator-system
```

## Troubleshooting

### Service Won't Start

Check logs:
```bash
./deploy/status.sh
# Or manually:
ssh dell-cloudflare 'sudo journalctl -u elevator-system -n 50'
```

Common issues:
1. **Port already in use**: Change `SERVICE_PORT` in .env
2. **Missing dependencies**: Re-run deployment
3. **Python version**: Ensure Python 3.11+
4. **Permissions**: Check file ownership

### Can't Connect via SSH

```bash
# Test SSH connection
ssh -v dell-cloudflare

# Check SSH config
cat ~/.ssh/config

# Test with explicit parameters
ssh -p 22 user@hostname
```

### Service Running But Not Responding

```bash
# Check if port is listening
ssh dell-cloudflare 'sudo netstat -tlnp | grep 8000'

# Check firewall
ssh dell-cloudflare 'sudo ufw status'

# Check nginx logs if using proxy
ssh dell-cloudflare 'sudo tail -f /var/log/nginx/elevator-system-error.log'
```

### Environment Variables Not Working

```bash
# Check .env file exists
ssh dell-cloudflare 'cat /opt/elevator-system/.env'

# Verify service is loading it
ssh dell-cloudflare 'sudo systemctl cat elevator-system'

# Check for syntax errors
ssh dell-cloudflare 'source /opt/elevator-system/venv/bin/activate && python3 -c "from app.config import settings; print(settings.dict())"'
```

### Out of Memory

```bash
# Check memory usage
ssh dell-cloudflare 'free -h'

# Check service memory
ssh dell-cloudflare 'sudo systemctl status elevator-system'

# Add memory limit to service
ssh dell-cloudflare 'sudo systemctl edit elevator-system'
# Add:
# [Service]
# MemoryMax=512M
```

### Nginx Issues

```bash
# Test nginx config
ssh dell-cloudflare 'sudo nginx -t'

# Reload nginx
ssh dell-cloudflare 'sudo systemctl reload nginx'

# Check nginx status
ssh dell-cloudflare 'sudo systemctl status nginx'

# View nginx error logs
ssh dell-cloudflare 'sudo tail -f /var/log/nginx/error.log'
```

## Security Considerations

### Firewall Configuration

```bash
ssh dell-cloudflare

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP
sudo ufw allow 80/tcp

# Allow HTTPS (if using SSL)
sudo ufw allow 443/tcp

# Allow direct backend access (optional)
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
```

### Environment Variables

Never commit `.env` files to git. The deployment script handles this automatically.

Sensitive variables:
- `RESEND_API_KEY` - Keep secret
- `ACCESS_CODE` - Change from default in production

### File Permissions

```bash
ssh dell-cloudflare

# Check permissions
ls -la /opt/elevator-system/.env

# Should be: -rw------- (600)
# If not:
chmod 600 /opt/elevator-system/.env
```

### SSL/TLS (HTTPS)

To enable HTTPS, edit nginx config and add certificates:

```bash
ssh dell-cloudflare

# Install certbot (Let's Encrypt)
sudo apt-get install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal is configured by certbot
```

## Rollback

If deployment fails, rollback to previous version:

```bash
ssh dell-cloudflare

# Stop service
sudo systemctl stop elevator-system

# Restore previous code (if using git)
cd /opt/elevator-system
git checkout <previous-commit>

# Or manually restore from backup
# cp -r /opt/elevator-system.backup/* /opt/elevator-system/

# Reinstall dependencies
source venv/bin/activate
pip install -e .

# Start service
sudo systemctl start elevator-system
```

## Monitoring

### Log Rotation

Logs are managed by systemd/journald. Configure retention:

```bash
ssh dell-cloudflare

# Edit journald config
sudo nano /etc/systemd/journald.conf

# Set max size (e.g., 100M)
SystemMaxUse=100M
MaxRetentionSec=2week

# Restart journald
sudo systemctl restart systemd-journald
```

### Performance Monitoring

```bash
# CPU and memory usage
ssh dell-cloudflare 'top -b -n 1 | head -20'

# Process info
ssh dell-cloudflare 'ps aux | grep uvicorn'

# Network connections
ssh dell-cloudflare 'sudo netstat -an | grep 8000'
```

## Backup

Create automated backups:

```bash
ssh dell-cloudflare

# Create backup script
cat > /opt/backup-elevator.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/backups/elevator-system"
DATE=$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR
tar czf $BACKUP_DIR/elevator-$DATE.tar.gz \
    --exclude='venv' \
    --exclude='__pycache__' \
    /opt/elevator-system
# Keep only last 7 backups
ls -t $BACKUP_DIR/elevator-*.tar.gz | tail -n +8 | xargs rm -f
EOF

chmod +x /opt/backup-elevator.sh

# Add to crontab (daily at 2 AM)
echo "0 2 * * * /opt/backup-elevator.sh" | crontab -
```

## Support

For deployment issues:
1. Check this deployment guide
2. View logs: `./deploy/logs.sh`
3. Check status: `./deploy/status.sh`
4. Review backend/README.md
5. Check MIGRATION_SUMMARY.md

Common commands reference:
```bash
# Deploy
./deploy/deploy.sh

# Check status
./deploy/status.sh

# View logs
./deploy/logs.sh

# Restart service
./deploy/restart.sh

# Deploy nginx
./deploy/deploy-nginx.sh
```
