#!/bin/bash

# Deploy to TestFlight Script for Mac
# Run this on your Mac to build and deploy to TestFlight

set -e

echo "🚀 Elevator System - Deploy to TestFlight"
echo "=========================================="

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo "❌ This script must be run on macOS"
    exit 1
fi

# Check for Xcode
if ! command -v xcodebuild &> /dev/null; then
    echo "❌ Xcode is not installed. Please install from the App Store."
    exit 1
fi

# Check for Node
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install from nodejs.org"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Navigate to mobile directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "📦 Installing dependencies..."
npm install

echo ""
echo "🔨 Prebuilding iOS project..."
npx expo prebuild --platform ios --clean

echo ""
echo "📱 Building for release..."
cd ios

# Clean build folder
xcodebuild clean -workspace *.xcworkspace -scheme ElevatorSystem -configuration Release -destination "generic/platform=iOS"

# Archive the app
echo "📚 Creating archive..."
ARCHIVE_PATH="../build/ElevatorSystem-$(date +%Y%m%d-%H%M%S).xcarchive"
xcodebuild archive \
    -workspace *.xcworkspace \
    -scheme ElevatorSystem \
    -configuration Release \
    -destination "generic/platform=iOS" \
    -archivePath "$ARCHIVE_PATH" \
    -allowProvisioningUpdates

echo ""
echo "📤 Exporting for App Store..."

# Create export options if not exists
if [ ! -f "../ios-export/ExportOptions.plist" ]; then
    echo "Creating ExportOptions.plist..."
    mkdir -p ../ios-export
    cat > ../ios-export/ExportOptions.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>uploadBitcode</key>
    <true/>
    <key>compileBitcode</key>
    <true/>
    <key>uploadSymbols</key>
    <true/>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>destination</key>
    <string>upload</string>
</dict>
</plist>
EOF
fi

# Export the archive
EXPORT_PATH="../build/export-$(date +%Y%m%d-%H%M%S)"
xcodebuild -exportArchive \
    -archivePath "$ARCHIVE_PATH" \
    -exportPath "$EXPORT_PATH" \
    -exportOptionsPlist ../ios-export/ExportOptions.plist \
    -allowProvisioningUpdates

echo ""
echo "🚀 Uploading to App Store Connect..."

# Find the IPA file
IPA_FILE=$(find "$EXPORT_PATH" -name "*.ipa" | head -1)

if [ -z "$IPA_FILE" ]; then
    echo "❌ IPA file not found in $EXPORT_PATH"
    exit 1
fi

echo "Found IPA: $IPA_FILE"
echo ""
echo "Please enter your App-Specific Password for ajdrake@gmail.com"
echo "(Generate at https://appleid.apple.com → Security → App-Specific Passwords)"
read -s -p "Password: " APP_PASSWORD
echo ""

# Upload using altool
xcrun altool --upload-app \
    -f "$IPA_FILE" \
    -t ios \
    -u ajdrake@gmail.com \
    -p "$APP_PASSWORD" \
    --verbose

echo ""
echo "✅ Upload complete!"
echo ""
echo "Next steps:"
echo "1. Go to https://appstoreconnect.apple.com"
echo "2. Wait 10-30 minutes for processing"
echo "3. Your build will appear in TestFlight"
echo "4. Add testers and start testing!"
echo ""
echo "Build artifacts saved in: $EXPORT_PATH"