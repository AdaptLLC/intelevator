# Elevator System - Mobile App

React Native mobile app with real-time GraphQL subscriptions for the elevator system.

## Quick Start

### 1. Configure Backend URL

Edit `config.js` and set the backend host:

```javascript
const BACKEND_HOST = '172.27.65.193:8000'; // Your backend URL
```

Or use environment variable:
```bash
export BACKEND_HOST='your-server.com'
```

### 2. Install Dependencies (if not already done)

```bash
npm install
```

### 3. Start Expo

```bash
npx expo start
```

Or for remote testing (different networks):
```bash
npx expo start --tunnel
```

### 4. Test on iPhone

1. Install **Expo Go** from App Store
2. Scan QR code from terminal
3. App will load on your iPhone

## Configuration

### Backend URL Options

**Local Development (Same WiFi):**
```javascript
const BACKEND_HOST = '192.168.1.100:8000';
```

**SSH Tunnel:**
```javascript
const BACKEND_HOST = '172.27.65.193:8000';
```

**Cloudflare Tunnel:**
```javascript
const BACKEND_HOST = 'elevator.adapt-llc.com';
```

**Production Domain:**
```javascript
const BACKEND_HOST = 'api.yourdomain.com';
```

## Features

### Real-time Updates
- GraphQL subscriptions via WebSocket
- Instant elevator status updates
- No polling needed

### Priority System
- Normal priority
- High priority
- Emergency priority (jumps to front of queue)

### Floor Selection
- Tap any floor (1-20) to call elevator
- Visual indicators:
  - **Blue** - Current floor
  - **Green** - Requested floor
  - **White** - Available

### Status Display
- Current floor
- Direction (up/down/idle)
- Next floor destination
- Active requests list

## Troubleshooting

### App won't connect to backend

1. **Check backend is running:**
```bash
curl http://YOUR_BACKEND_URL/health
```

2. **Verify config.js has correct URL:**
```bash
grep BACKEND_HOST config.js
```

3. **Check firewall/network:**
- iPhone and server must be reachable
- For local testing, use same WiFi
- For remote testing, use tunnel or public URL

### App crashes on launch

1. **Clear Metro cache:**
```bash
npx expo start --clear
```

2. **Reinstall dependencies:**
```bash
rm -rf node_modules package-lock.json
npm install
```

3. **Check for JavaScript errors in terminal**

### WebSocket connection fails

- Ensure backend supports WebSocket (it does via Strawberry GraphQL)
- Check that GraphQL subscriptions are enabled
- Verify no proxy/firewall blocking WebSocket connections

## Development

### Project Structure
```
mobile/
├── App.js           # Main app component
├── config.js        # Configuration (backend URL)
├── package.json     # Dependencies
├── .env.example     # Environment template
└── README.md        # This file
```

### Dependencies
- **expo** - React Native framework
- **@apollo/client** - GraphQL client
- **graphql-ws** - WebSocket transport for subscriptions
- **react-native** - Mobile framework

### GraphQL Operations

**Subscription (Real-time):**
```graphql
subscription {
  elevatorUpdates {
    currentFloor
    nextFloor
    direction
    requests {
      floor
      priority
    }
  }
}
```

**Mutation (Call Elevator):**
```graphql
mutation {
  callElevator(floor: 5, priority: NORMAL) {
    id
    floor
    priority
  }
}
```

## Backend Setup

The mobile app requires the Python FastAPI backend to be running.

**Check backend health:**
```bash
curl http://YOUR_BACKEND_URL/health
```

**Should return:**
```json
{"status":"healthy","version":"2.0.0"}
```

See `../backend/README.md` for backend deployment instructions.

## Testing

### Test Backend Connection

```bash
# From your machine
curl http://172.27.65.193:8000/health

# Should see: {"status":"healthy","version":"2.0.0"}
```

### Test GraphQL

Visit http://172.27.65.193:8000/graphql in a browser to use the GraphQL playground.

### Test on Device

1. Ensure device and backend are on same network (or use tunnel)
2. Start Expo: `npx expo start`
3. Scan QR code with Expo Go
4. App should connect and show elevator interface

## Production Deployment

For production, deploy backend to a public URL and update `config.js`:

```javascript
const BACKEND_HOST = 'elevator.yourdomain.com';
```

Consider:
- HTTPS/WSS for production
- Authentication/authorization
- Rate limiting
- Error tracking (Sentry)
- Analytics

## Support

For issues:
1. Check this README
2. Review `../CURRENT_STATUS.md`
3. Check backend logs: `ssh dell-cloudflare 'tail -f ~/elevator-system/server.log'`
