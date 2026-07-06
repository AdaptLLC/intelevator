const { getDefaultConfig } = require('expo/metro-config');

const config = getDefaultConfig(__dirname);

// Fix for Apollo Client 4.x module resolution
config.resolver.resolveRequest = (context, moduleName, platform) => {
  // Fix Apollo Client imports
  if (moduleName.startsWith('@apollo/client')) {
    // Map the imports to the correct paths
    const mappings = {
      '@apollo/client': '@apollo/client/core',
      '@apollo/client/core': '@apollo/client/core',
      '@apollo/client/link/ws': '@apollo/client/link/ws',
      '@apollo/client/link/subscriptions': '@apollo/client/link/subscriptions',
    };

    const resolvedName = mappings[moduleName] || moduleName;

    try {
      return context.resolveRequest(context, resolvedName, platform);
    } catch (e) {
      // Fallback to default resolution
    }
  }

  // Default resolution for everything else
  return context.resolveRequest(context, moduleName, platform);
};

module.exports = config;
