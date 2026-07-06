#!/bin/bash

# Kill any existing Expo process on port 8081
echo "Stopping any existing Expo processes..."
lsof -ti:8081 | xargs -r kill -9

# Create logs directory if it doesn't exist
mkdir -p /home/aaron/elevator-system/mobile/logs

# Set log file with timestamp
LOG_FILE="/home/aaron/elevator-system/mobile/logs/expo-$(date +%Y%m%d-%H%M%S).log"
LATEST_LOG="/home/aaron/elevator-system/mobile/logs/expo-latest.log"

echo "Starting Expo with tunnel mode..."
echo "Logs will be written to: $LOG_FILE"
echo "Latest log symlink: $LATEST_LOG"
echo ""

# Start Expo with tunnel and log output
cd /home/aaron/elevator-system/mobile

# Use unbuffer to preserve colors and real-time output, tee to show and save logs
npx expo start --tunnel 2>&1 | tee "$LOG_FILE"

# Create symlink to latest log for easy access
ln -sf "$LOG_FILE" "$LATEST_LOG"