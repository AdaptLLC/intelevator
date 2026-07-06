/**
 * Main entry point for the Elevator System Mobile App
 *
 * Toggle between production and mock modes by changing the import below
 */

import { registerRootComponent } from 'expo';

// ==================================================
// CONFIGURATION: Choose which app version to run
// ==================================================

// PRODUCTION MODE - Requires backend server running
// import App from './App';

// PRODUCTION MODE ALTERNATIVE - Polling-based (no WebSocket)
// import App from './AppWorking';

// MOCK MODE - Fully offline with simulated backend (Apollo + WebSocket simulation)
// import App from './AppMocked';

// MOCK MODE SIMPLE - Direct mock service without Apollo (recommended for now)
import App from './AppMockedSimple';

// MOCK MODE ALTERNATIVE - Polling-based simulation (no WebSocket)
// import App from './AppMockedPolling';

// SIMPLE UI TEST - No backend calls at all
// import App from './AppSimple';

// ==================================================

// registerRootComponent calls AppRegistry.registerComponent('main', () => App);
// It also ensures that whether you load the app in Expo Go or in a native build,
// the environment is set up appropriately
registerRootComponent(App);

/**
 * Quick Reference:
 *
 * App.js              - Production app with real backend (WebSocket subscriptions)
 * AppWorking.js       - Production app with polling fallback (no WebSocket)
 * AppMocked.js        - Mock backend with Apollo subscriptions (recommended for development)
 * AppMockedPolling.js - Mock backend with HTTP polling (simpler, no WebSocket)
 * AppSimple.js        - Static UI only, no backend integration
 *
 * To switch modes, simply comment out the current import and uncomment the desired one.
 */
