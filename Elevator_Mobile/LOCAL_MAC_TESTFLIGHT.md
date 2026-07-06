# Deploy to TestFlight Using Your Mac

## Prerequisites on Your Mac
1. Xcode (latest version from App Store)
2. Apple Developer Account ($99/year) - sign up at developer.apple.com
3. Node.js and npm installed

## Step-by-Step Deployment

### 1. Initial Setup (One Time)
```bash
# On your Mac, install Expo CLI and EAS CLI
npm install -g expo-cli eas-cli

# Clone or copy your project to the Mac
# Then navigate to the mobile directory
cd /path/to/elevator-system/mobile

# Install dependencies
npm install

# Login to Expo
expo login

# Login to your Apple account
eas login
```

### 2. Configure iOS Build
```bash
# Generate native iOS project
npx expo prebuild --platform ios

# This creates an 'ios' folder with the Xcode project
```

### 3. Open in Xcode
```bash
# Open the project in Xcode
open ios/*.xcworkspace
```

### 4. Configure Signing in Xcode
1. Select your project in the navigator
2. Select your app target
3. Go to "Signing & Capabilities" tab
4. Check "Automatically manage signing"
5. Select your Apple Developer Team (ajdrake@gmail.com)
6. Bundle Identifier should be: com.adaptllc.elevatorsystem

### 5. Build for TestFlight
In Xcode:
1. Select "Any iOS Device" as the build target (not a simulator)
2. Menu: Product → Archive
3. Wait for build to complete (5-10 minutes)
4. Organizer window opens automatically

### 6. Upload to TestFlight
In the Organizer window:
1. Select your archive
2. Click "Distribute App"
3. Choose "App Store Connect"
4. Choose "Upload"
5. Follow the prompts (keep defaults)
6. Wait for upload (2-5 minutes)

### 7. Configure TestFlight in App Store Connect
1. Go to https://appstoreconnect.apple.com
2. Select your app
3. Go to TestFlight tab
4. Your build will appear after processing (10-30 minutes)
5. Add test information:
   - What to Test: "Elevator control system interface"
   - Test Email: ajdrake@gmail.com
6. Add Internal Testers (yourself)
7. Submit for Beta Review (optional for external testers)

## Alternative: Command Line Build & Upload

If you prefer command line over Xcode GUI:

```bash
# Build the app
cd ios
xcodebuild -workspace *.xcworkspace -scheme mobile -configuration Release -archivePath ../build/mobile.xcarchive archive

# Export for App Store
xcodebuild -exportArchive -archivePath ../build/mobile.xcarchive -exportPath ../build -exportOptionsPlist ExportOptions.plist

# Upload using Transporter or altool
xcrun altool --upload-app -f ../build/*.ipa -u ajdrake@gmail.com -p "app-specific-password"
```

## Creating App-Specific Password
1. Go to https://appleid.apple.com
2. Sign in with ajdrake@gmail.com
3. Security → App-Specific Passwords
4. Generate one for "Xcode Upload"
5. Save it securely

## Local Development & Testing

For development builds on your Mac:
```bash
# Run on iOS Simulator
npx expo run:ios

# Run on connected iPhone (must be in Developer Mode)
npx expo run:ios --device
```

## Network Access from WSL

If you want to trigger builds from your WSL environment to the Mac:

1. On Mac, enable Remote Login:
   - System Preferences → Sharing → Remote Login

2. From WSL, you can SSH to your Mac:
   ```bash
   ssh username@mac-ip-address
   cd /path/to/project
   # Run build commands
   ```

## Troubleshooting

### "Team not found" error
- Ensure you're logged into Xcode with ajdrake@gmail.com
- Xcode → Preferences → Accounts → Add Apple ID

### "No provisioning profile" error
- Let Xcode manage it automatically
- Or create one at developer.apple.com → Certificates

### Build fails with "Command PhaseScriptExecution failed"
```bash
cd ios
pod install
```

## Quick Command Reference

```bash
# Check everything is set up
npx expo doctor

# Prebuild iOS project
npx expo prebuild --platform ios --clean

# Open in Xcode
open ios/*.xcworkspace

# Run on simulator
npx expo run:ios

# Build release
npx expo run:ios --configuration Release
```

## Time Estimate
- First time setup: 30-45 minutes
- Subsequent builds: 10-15 minutes
- Upload to TestFlight: 5 minutes
- Processing on Apple's side: 10-30 minutes

Your app will be available in TestFlight within 1 hour!