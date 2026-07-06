# Quick Start: Mock Elevator System

## 🚀 Instant Setup (30 seconds)

The app is already configured to use the mock backend! Just run:

```bash
cd mobile
npm start
```

Then scan the QR code with Expo Go on your phone, or press `w` to open in web browser.

## ✅ What's Working

- **Full elevator simulation** without any backend
- **Automatic floor movement** every 2 seconds
- **User interactions** - Call elevator to any floor
- **Priority system** - NORMAL, HIGH, EMERGENCY
- **Visual feedback** - Current floor, direction, active requests
- **Finite loop** - 40-state cycle that repeats

## 📁 Files Created

```
mobile/
├── mockData/
│   ├── elevatorStates.json    # 40-state simulation cycle
│   └── scenarios.json          # Additional scenarios (rush hour, etc.)
├── services/
│   ├── mockService.js          # Core mock elevator logic
│   └── mockApolloClient.js    # GraphQL mock implementation
├── AppMocked.js                # Main mock app (Apollo)
├── AppMockedPolling.js         # Alternative (HTTP polling)
└── index.js                    # Updated to use AppMocked by default
```

## 🎮 How It Works

1. **Elevator Movement**: The elevator automatically moves through a predefined 40-state cycle:
   - States 1-18: Going UP (floor 1 → 18)
   - States 19-36: Going DOWN (floor 18 → 2)
   - States 37-40: IDLE at floor 2
   - Then repeats from state 1

2. **User Requests**: When you tap a floor button:
   - Request is added to the queue
   - Sorted by priority (EMERGENCY > HIGH > NORMAL)
   - Served based on SCAN algorithm (current direction first)
   - Removed when elevator reaches that floor

3. **Update Frequency**: Every 2 seconds the elevator:
   - Advances to the next state
   - Updates the UI automatically
   - Processes any pending requests

## 🔄 Switching Modes

Edit `mobile/index.js` to switch between modes:

```javascript
// For mock mode (current):
import App from './AppMocked';

// For production mode:
import App from './App';

// For polling mock:
import App from './AppMockedPolling';
```

## 🧪 Testing the Mock

Run the test script to verify everything works:

```bash
cd mobile
node testMockService.js
```

## 📱 What You'll See

1. **Status Card**: Shows current floor (big blue number), direction, and next floor
2. **Priority Buttons**: Select NORMAL, HIGH, or EMERGENCY
3. **Floor Grid**:
   - Blue = Current floor
   - Green = Has active request
   - White = Available
4. **Active Requests**: List of pending calls with priority
5. **Mock Badge**: Orange/Purple indicator showing mock mode

## 🎯 Try This

1. Tap floor 15 with NORMAL priority
2. Watch elevator move up (takes ~14 seconds to arrive)
3. Tap floor 5 with EMERGENCY priority
4. See it get prioritized over other requests
5. Watch the finite loop repeat after ~80 seconds

## 🛠️ Customization

### Change Speed
In `mockData/elevatorStates.json`, modify:
```json
"updateInterval": 1000  // 1 second instead of 2
```

### Add More Floors
The mock supports floors 1-20 by default. Modify validation in `mockService.js` to change range.

### Different Scenarios
Check `mockData/scenarios.json` for rush hour, maintenance, and night mode variations.

## ⚠️ Important Notes

- **No persistence** - Requests are lost on app reload
- **Single user** - No multi-user synchronization
- **Predictable** - Same sequence every time (good for testing!)
- **Offline only** - No actual backend connection

## 🚫 Troubleshooting

**App won't start?**
- Check that `index.js` imports `AppMocked`
- Run `npm install` in the mobile directory

**Elevator not moving?**
- Verify mock service is running (check console)
- Ensure no JavaScript errors in Expo

**Can't call elevator?**
- Floor must be 1-20
- Priority must be NORMAL, HIGH, or EMERGENCY

## ✨ Success!

You now have a fully functional mock elevator system that:
- Works completely offline
- Simulates realistic elevator behavior
- Allows full testing without backend dependencies
- Prevents app crashes when backend is unavailable

The elevator is moving through its cycle right now - open the app and watch it go!