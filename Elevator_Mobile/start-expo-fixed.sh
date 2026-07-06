#!/bin/bash

# Kill any existing Expo process on port 8081
echo "Stopping any existing Expo processes..."
lsof -ti:8081 | xargs -r kill -9 2>/dev/null || true

# Create logs directory if it doesn't exist
mkdir -p /home/aaron/elevator-system/mobile/logs

# Set log file
LOG_FILE="/home/aaron/elevator-system/mobile/logs/expo-running.log"

echo "Starting Expo with tunnel mode..."
echo "Logs will be written to: $LOG_FILE"
echo ""
echo "Access your app with:"
echo "1. Install Expo Go on your phone"
echo "2. Look for the exp:// URL in the logs"
echo "3. Scan the QR code that appears"
echo ""

# Start Expo with tunnel
cd /home/aaron/elevator-system/mobile

# Run Expo in the foreground with proper signal handling
exec npx expo start --tunnel 2>&1 | tee "$LOG_FILE"