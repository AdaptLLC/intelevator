# TestFlight Deployment Guide for Elevator System

## Overview

This guide walks you through deploying the Elevator System mobile app to TestFlight using Expo Application Services (EAS).

**App Details:**
- App Name: Elevator System
- Bundle Identifier: com.adaptllc.elevatorsystem
- Version: 1.0.0
- Build Number: 1
- Apple ID: ajdrake@gmail.com

---

## Prerequisites Checklist

Before starting the build process, ensure you have:

### Apple Developer Account
- [ ] Active Apple Developer Program membership ($99/year)
- [ ] Account email: ajdrake@gmail.com
- [ ] Access to App Store Connect (https://appstoreconnect.apple.com)
- [ ] Two-factor authentication enabled on Apple ID

### Development Environment
- [ ] Node.js installed (current version verified)
- [ ] Expo CLI installed (version 54.0.22 confirmed)
- [ ] EAS CLI will be installed during setup
- [ ] Logged into Expo account (or create one at https://expo.dev)

### App Assets
- [ ] App icon (1024x1024px PNG) at `./assets/icon.png`
- [ ] Splash screen image at `./assets/splash-icon.png`
- [ ] Adaptive icon for Android at `./assets/adaptive-icon.png`

---

## Step 1: Install and Configure EAS CLI

### 1.1 Install EAS CLI globally

```bash
npm install -g eas-cli
```

### 1.2 Login to Expo account

```bash
eas login
```

**Options:**
- If you have an Expo account: Enter your credentials
- If you don't have an Expo account: Create one at https://expo.dev/signup

### 1.3 Configure the project with EAS

```bash
cd /home/aaron/elevator-system/mobile
eas build:configure
```

**What this does:**
- Validates your eas.json configuration
- Generates a unique project ID
- Updates app.json with the project ID
- Links your local project to Expo's build servers

**Expected output:**
```
✔ EAS project created!
Project ID: [unique-id-will-be-shown]
```

---

## Step 2: Verify iOS Configuration

### 2.1 Check app.json settings

The following has been configured for you:

```json
{
  "expo": {
    "name": "Elevator System",
    "slug": "elevator-system",
    "version": "1.0.0",
    "ios": {
      "bundleIdentifier": "com.adaptllc.elevatorsystem",
      "buildNumber": "1"
    }
  }
}
```

### 2.2 Review eas.json build profiles

Three build profiles are configured:

**Development** - For testing with Expo Go or development builds
```json
{
  "developmentClient": true,
  "distribution": "internal",
  "ios": {
    "simulator": true
  }
}
```

**Preview** - For internal testing on real devices
```json
{
  "distribution": "internal",
  "ios": {
    "simulator": false,
    "bundleIdentifier": "com.adaptllc.elevatorsystem"
  }
}
```

**Production** - For TestFlight and App Store submission
```json
{
  "distribution": "store",
  "ios": {
    "bundleIdentifier": "com.adaptllc.elevatorsystem"
  }
}
```

---

## Step 3: Configure iOS Credentials

### 3.1 Generate iOS credentials automatically

EAS can automatically manage your iOS certificates and provisioning profiles:

```bash
eas credentials
```

**Follow the prompts:**
1. Select platform: **iOS**
2. Choose profile: **production**
3. Select: **Set up credentials**
4. When prompted for Apple ID: **ajdrake@gmail.com**
5. Enter your Apple ID password
6. Complete two-factor authentication
7. Select your team (if you have multiple)

**What EAS does automatically:**
- Creates a distribution certificate
- Generates a provisioning profile
- Registers the app bundle ID with Apple
- Stores credentials securely in Expo's infrastructure

### 3.2 Alternative: Manual credential management

If you prefer to manage credentials manually:

```bash
eas credentials --platform ios
```

Then follow prompts to upload existing certificates and provisioning profiles.

---

## Step 4: Build for TestFlight

### 4.1 Create production build

```bash
eas build --platform ios --profile production
```

**What happens:**
1. EAS uploads your code to Expo's build servers
2. Validates your configuration
3. Authenticates with Apple Developer Portal
4. Builds the iOS binary (.ipa file)
5. Generates download link

**Build time:** Typically 10-20 minutes

**Build output:**
```
✔ Build finished
Build ID: [unique-build-id]
Build link: https://expo.dev/accounts/[your-account]/projects/elevator-system/builds/[build-id]
```

### 4.2 Monitor build progress

**Option 1 - Web dashboard:**
Visit: https://expo.dev/accounts/ajdrake/projects/elevator-system/builds

**Option 2 - CLI:**
```bash
eas build:list --platform ios
```

### 4.3 Download the .ipa file (optional)

Once build completes:

```bash
eas build:download --platform ios --latest
```

---

## Step 5: Submit to TestFlight

### 5.1 Automatic submission via EAS

```bash
eas submit --platform ios --latest
```

**What this does:**
- Downloads your latest iOS build
- Uploads to App Store Connect
- Submits for TestFlight review

**Follow the prompts:**
1. Confirm Apple ID: **ajdrake@gmail.com**
2. Authenticate with Apple (2FA required)
3. Select the correct build
4. Confirm submission

### 5.2 Monitor submission status

**Via EAS CLI:**
```bash
eas submit:list --platform ios
```

**Via App Store Connect:**
1. Visit: https://appstoreconnect.apple.com
2. Navigate to: My Apps > Elevator System
3. Click: TestFlight tab
4. Check: Build processing status

**Processing time:** 5-15 minutes for Apple to process the build

---

## Step 6: Set Up TestFlight

### 6.1 Add app information in App Store Connect

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" > "Elevator System"
3. Go to "TestFlight" tab
4. Fill in required fields:
   - **Test Information**
   - **Beta App Description**: See `APP_STORE_CONTENT.md` for copy
   - **Feedback Email**: ajdrake@gmail.com
   - **Marketing URL**: (optional)
   - **Privacy Policy URL**: (required for TestFlight)

### 6.2 Create internal testing group

1. In TestFlight tab, click "App Store Connect Users"
2. Add testers by email
3. Enable "Automatic Distribution" for new builds

### 6.3 Export Compliance

For TestFlight, you must answer export compliance questions:

**Does your app use encryption?**
- **Answer**: Probably NO (unless you added custom encryption beyond standard HTTPS)
- GraphQL over HTTPS uses standard transport encryption (doesn't require declaration)

**If YES:** You may need to provide an Export Compliance Document

---

## Step 7: Distribute to Testers

### 7.1 Add internal testers (App Store Connect users)

1. TestFlight > App Store Connect Users
2. Click the "+" button
3. Select users from your team
4. Click "Add"

**Testers will receive:**
- Email invitation to test
- Link to install TestFlight app
- Access to install your app

### 7.2 Add external testers (public beta)

1. TestFlight > External Testing
2. Create a new group
3. Add testers by email
4. Submit build for Beta App Review (1-2 days)

**Note:** External testing requires Beta App Review by Apple

---

## Step 8: Install TestFlight Build

### 8.1 For testers

1. Install TestFlight app from App Store
2. Open invitation email from TestFlight
3. Tap "View in TestFlight"
4. Tap "Install" in TestFlight app
5. Launch "Elevator System"

### 8.2 Verify app functionality

Test checklist:
- [ ] App launches successfully
- [ ] Connects to backend (backend.adapt-llc.com)
- [ ] GraphQL subscription receives real-time updates
- [ ] Can call elevator to different floors
- [ ] Priority selection works (Normal, High, Emergency)
- [ ] Current floor display updates correctly
- [ ] Active requests list displays properly

---

## Troubleshooting

### Build fails with "Invalid bundle identifier"

**Solution:**
1. Verify bundle ID in app.json matches eas.json
2. Ensure bundle ID is registered in Apple Developer Portal
3. Run `eas build:configure` again

### "No valid code signing identity found"

**Solution:**
1. Run `eas credentials` to regenerate certificates
2. Select "Remove all credentials" then "Set up credentials"
3. Re-authenticate with Apple ID

### Build succeeds but submission fails

**Solution:**
1. Check App Store Connect for error messages
2. Verify Apple ID has necessary permissions
3. Ensure 2FA is enabled on Apple account
4. Try manual submission via Transporter app

### TestFlight build shows "Missing Compliance"

**Solution:**
1. In App Store Connect, select the build
2. Answer export compliance questions
3. If standard HTTPS only: Select "No" for encryption

### Backend connection fails in TestFlight build

**Solution:**
1. Verify backend URL in config.js uses production domain
2. Ensure backend.adapt-llc.com is accessible publicly
3. Check SSL certificate is valid for the domain
4. Verify GraphQL and WebSocket endpoints are working

---

## Updating the App

### For new builds (version updates)

1. Update version in app.json:
   ```json
   {
     "expo": {
       "version": "1.0.1",
       "ios": {
         "buildNumber": "2"
       }
     }
   }
   ```

2. Build new version:
   ```bash
   eas build --platform ios --profile production
   ```

3. Submit to TestFlight:
   ```bash
   eas submit --platform ios --latest
   ```

### For minor changes (same version)

- Increment only the buildNumber
- Apple requires unique build numbers for each submission

---

## Next Steps After TestFlight

Once TestFlight testing is complete, you can submit to the App Store:

1. Complete App Store listing in App Store Connect
2. Add screenshots (see `SCREENSHOTS.md` for requirements)
3. Add app description and metadata
4. Submit for App Store Review
5. Review typically takes 1-3 days

**See:** `APP_STORE_SUBMISSION.md` for full App Store submission guide

---

## Cost Breakdown

- **Apple Developer Program**: $99/year (required)
- **Expo EAS Build**: Free tier includes 30 builds/month for iOS
- **Paid plans**: If you need more builds, see https://expo.dev/pricing

---

## Useful Commands Reference

```bash
# Check EAS build status
eas build:list --platform ios

# View build logs
eas build:view [build-id]

# Cancel a build
eas build:cancel [build-id]

# Manage credentials
eas credentials

# View project configuration
eas config

# Check account status
eas whoami

# Update EAS CLI
npm install -g eas-cli@latest
```

---

## Support Resources

- **Expo EAS Documentation**: https://docs.expo.dev/build/introduction/
- **Expo EAS Submit Guide**: https://docs.expo.dev/submit/introduction/
- **Apple Developer Portal**: https://developer.apple.com
- **App Store Connect**: https://appstoreconnect.apple.com
- **TestFlight Help**: https://developer.apple.com/testflight/

---

## Configuration Files Summary

The following files have been configured for TestFlight deployment:

1. **eas.json** - EAS Build configuration with three profiles (development, preview, production)
2. **app.json** - Updated with iOS bundle identifier, build number, and metadata
3. **package.json** - Contains all required dependencies

All files are ready for the build process.
