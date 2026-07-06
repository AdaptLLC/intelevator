/**
 * Configuration for the elevator mobile app
 *
 * To change the backend URL, update BACKEND_HOST below
 */

// Backend configuration
const BACKEND_HOST = process.env.BACKEND_HOST || 'hoist.adapt-llc.com';

// Determine if we should use https/wss (for domains) or http/ws (for localhost with port)
const isSecure =
  !BACKEND_HOST.includes(':') || BACKEND_HOST.includes('adapt-llc.com');
const httpProtocol = isSecure ? 'https' : 'http';
const wsProtocol = isSecure ? 'wss' : 'ws';

export const config = {
  // Backend URLs
  backendUrl: BACKEND_HOST,
  graphqlUrl: `${httpProtocol}://${BACKEND_HOST}/graphql`,
  graphqlWsUrl: `${wsProtocol}://${BACKEND_HOST}/graphql`,

  // API endpoints
  healthUrl: `${httpProtocol}://${BACKEND_HOST}/health`,

  // App settings
  appName: 'Elevator System',
  version: '1.0.0',
};

export default config;
