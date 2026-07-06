module.exports = {
  preset: 'react-native',
  testEnvironment: 'node',
  transformIgnorePatterns: [
    'node_modules/(?!((jest-)?react-native|@react-native(-community)?)|expo(nent)?|@expo(nent)?/.*|@expo-google-fonts/.*|react-navigation|@react-navigation/.*|@unimodules/.*|unimodules|sentry-expo|native-base|react-native-svg|@apollo/client|graphql-ws)'
  ],
  setupFilesAfterEnv: [],
  collectCoverage: true,
  collectCoverageFrom: [
    'config.js',
    'services/**/*.js',
    '!**/coverage/**',
    '!**/node_modules/**',
    '!**/jest.setup.js',
    '!**/babel.config.js',
    '!**/jest.config.js',
    '!**/metro.config.js',
    '!**/.eslintrc.js',
    '!**/index.js',
    '!**/ios-export/**',
    '!**/logs/**',
    '!**/mockData/**',
    '!**/assets/**',
    '!App*.js',
    '!test*.js'
  ],
  coverageThreshold: {
    global: {
      branches: 0,
      functions: 0,
      lines: 0,
      statements: 0
    }
  },
  testMatch: [
    '**/__tests__/**/*.test.js',
    '**/__tests__/**/*.spec.js'
  ],
  moduleNameMapper: {
    '\\.(jpg|jpeg|png|gif|eot|otf|webp|svg|ttf|woff|woff2|mp4|webm|wav|mp3|m4a|aac|oga)$': '<rootDir>/__mocks__/fileMock.js',
    '\\.(css|less)$': '<rootDir>/__mocks__/styleMock.js'
  },
  testTimeout: 30000,
  verbose: true
};