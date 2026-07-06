# Deployment Scripts

Quick reference for deploying to dell-cloudflare dev server.

## Quick Start

```bash
cd backend

# 1. Deploy backend
./deploy/deploy.sh

# 2. Configure environment (first time only)
ssh dell-cloudflare
nano /opt/elevator-system/.env
# Add your RESEND_API_KEY
exit

# 3. Restart service
./deploy/restart.sh

# 4. Deploy nginx (optional)
./deploy/deploy-nginx.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `deploy.sh` | Full deployment (sync + install + start) |
| `deploy-nginx.sh` | Deploy nginx reverse proxy |
| `status.sh` | Check service status and health |
| `logs.sh` | View live logs |
| `restart.sh` | Restart the service |

## Configuration

Set environment variables before deploying:

```bash
export REMOTE_HOST=dell-cloudflare
export REMOTE_USER=aaron
export REMOTE_PATH=/opt/elevator-system
export SERVICE_PORT=8000

./deploy/deploy.sh
```

## Files

- `elevator-system.service` - Systemd service configuration
- `nginx-elevator-system.conf` - Nginx reverse proxy configuration
- `DEPLOYMENT.md` - Complete deployment documentation

## Common Tasks

### Deploy Updates
```bash
./deploy/deploy.sh
```

### View Logs
```bash
./deploy/logs.sh
```

### Check Status
```bash
./deploy/status.sh
```

### Restart Service
```bash
./deploy/restart.sh
```

### SSH to Server
```bash
ssh dell-cloudflare
```

## Access URLs

**Direct (port 8000):**
- Health: http://dell-cloudflare:8000/health
- GraphQL: http://dell-cloudflare:8000/graphql
- API: http://dell-cloudflare:8000/api/

**Via Nginx (port 80):**
- Health: http://dell-cloudflare/health
- GraphQL: http://dell-cloudflare/graphql
- API: http://dell-cloudflare/api/

## Troubleshooting

**Service won't start?**
```bash
./deploy/status.sh
ssh dell-cloudflare 'sudo journalctl -u elevator-system -n 50'
```

**Can't connect via SSH?**
```bash
ssh -v dell-cloudflare
cat ~/.ssh/config
```

**Need to change port?**
```bash
ssh dell-cloudflare
nano /opt/elevator-system/.env
# Change PORT=8000 to desired port
sudo systemctl restart elevator-system
```

See `DEPLOYMENT.md` for complete documentation.
