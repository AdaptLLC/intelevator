# Mock Backend Setup for Elevator System Mobile App

## Overview

The mobile app now includes a complete mock backend system that simulates all elevator operations locally without requiring any backend connection. This allows the app to run fully offline and prevents crashes when the backend is unavailable.

## Features

- **Complete offline operation** - No backend required
- **Realistic elevator simulation** - Moves between floors with proper timing
- **Finite loop cycle** - 40 predefined states that repeat
- **Dynamic request handling** - User requests are integrated into the simulation
- **Multiple implementations** - Works with Apollo subscriptions and HTTP polling

## Files Structure

```
mobile/
├── mockData/
│   └── elevatorStates.json       # Predefined elevator states (40-state cycle)
├── services/
│   ├── mockService.js            # Core mock service with elevator logic
│   └── mockApolloClient.js       # Mock Apollo client for GraphQL operations
├── AppMocked.js                  # Main app using Apollo + WebSocket simulation
└── AppMockedPolling.js           # Alternative using HTTP polling simulation
```

## Available Mock Apps

### 1. AppMocked.js (Recommended)
- Uses Apollo Client with mock GraphQL subscriptions
- Real-time updates via simulated WebSocket
- Most similar to production app behavior

### 2. AppMockedPolling.js
- Uses HTTP polling (every 2 seconds)
- No WebSocket dependencies
- Good for simpler testing scenarios

## How to Use

### Running the Mock App

1. **Using Expo Go:**
```bash
cd mobile
npm start
```

2. **In your main App.js or index.js, import the mock version:**
```javascript
// Replace this:
import App from './App';

// With this:
import App from './AppMocked';
// or
import App from './AppMockedPolling';
```

### Mock Data Structure

The elevator simulation uses a 40-state cycle defined in `mockData/elevatorStates.json`:

- **States 1-18**: Elevator moves UP from floor 1 to 18
- **State 18**: Idle at top floor
- **States 19-36**: Elevator moves DOWN from floor 18 to 2
- **States 37-40**: Idle at floor 2

Each state includes:
```json
{
  "currentFloor": 5,
  "nextFloor": 7,
  "direction": "UP",
  "requests": [...]
}
```

### Simulation Behavior

1. **Automatic Movement**: Elevator advances to next state every 2 seconds
2. **Request Integration**: User-submitted requests are merged with predefined requests
3. **Priority Handling**:
   - EMERGENCY > HIGH > NORMAL
   - Higher priority requests are served first
4. **SCAN Algorithm**: Elevator serves requests in current direction before reversing

### Customization

#### Modify Cycle Speed
In `mockService.js`, change the update interval:
```javascript
this.updateInterval = 3000; // 3 seconds instead of 2
```

#### Add More States
Edit `mockData/elevatorStates.json` to add more states and update `cycleLength`.

#### Change Floor Range
Modify the floor validation in `mockService.js`:
```javascript
if (floor < 1 || floor > 30) { // Support 30 floors instead of 20
```

## API Compatibility

The mock service implements all GraphQL operations used by the production app:

### Queries
- `elevatorStatus` - Get current elevator status

### Mutations
- `callElevator(floor, priority)` - Request elevator to a floor

### Subscriptions
- `elevatorUpdates` - Real-time status updates

## Testing Features

### Reset Simulation
The polling version includes a reset button to restart the simulation from the beginning.

### Dynamic Requests
Click any floor button to add a request. The elevator will:
1. Add your request to the queue
2. Serve it based on priority and direction
3. Remove it when the floor is reached

## Differences from Production

| Feature | Production | Mock |
|---------|------------|------|
| Data Source | Backend server | Local JSON |
| Updates | Real elevator events | 2-second intervals |
| Persistence | Database | Memory only |
| Multi-user | Yes | No |
| Request Processing | SCAN algorithm | Simulated SCAN |

## Troubleshooting

### App Crashes on Start
- Ensure you're importing the mock version, not the production App.js
- Check that all mock files are present in the correct directories

### Elevator Not Moving
- Verify `mockService.js` is starting the simulation
- Check browser console for errors
- Ensure interval is not cleared accidentally

### Requests Not Working
- Verify floor number is between 1-20
- Check priority is NORMAL, HIGH, or EMERGENCY
- Look for errors in console

## Development Benefits

1. **No Backend Dependency** - Develop anywhere without server setup
2. **Predictable Behavior** - Same cycle every time for consistent testing
3. **Fast Iteration** - No network delays or server issues
4. **Offline Development** - Work without internet connection
5. **Easy Debugging** - All logic is client-side and observable

## Production Migration

To switch back to the production backend:

1. Import the original App:
```javascript
import App from './App'; // Production version
```

2. Ensure backend is running and accessible
3. Update `config.js` with correct backend URL