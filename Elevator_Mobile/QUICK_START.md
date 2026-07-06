# Quick Start: TestFlight Deployment

## Overview

This guide gets you from current state to TestFlight in the fastest way possible.

**Estimated Time:** 2-3 hours
**Apple ID:** ajdrake@gmail.com

---

## Step 1: Install EAS CLI (5 minutes)

```bash
npm install -g eas-cli
eas login
```

Create Expo account if you don't have one: https://expo.dev/signup

---

## Step 2: Configure Project (5 minutes)

```bash
cd /home/aaron/elevator-system/mobile
eas build:configure
```

This generates a project ID and links your app to Expo.

---

## Step 3: Set Up Apple Credentials (10 minutes)

```bash
eas credentials
```

**Steps:**
1. Select: iOS
2. Select: production
3. Enter Apple ID: ajdrake@gmail.com
4. Enter password
5. Complete 2FA
6. Select your team

EAS will automatically create certificates and provisioning profiles.

---

## Step 4: Build for iOS (15-20 minutes)

```bash
eas build --platform ios --profile production
```

Wait for build to complete. You'll get a URL to monitor progress.

---

## Step 5: Submit to TestFlight (5 minutes)

```bash
eas submit --platform ios --latest
```

**Steps:**
1. Confirm Apple ID: ajdrake@gmail.com
2. Authenticate with 2FA
3. Confirm submission

---

## Step 6: Configure TestFlight (15 minutes)

1. Go to https://appstoreconnect.apple.com
2. Click "My Apps" > "Elevator System"
3. Go to "TestFlight" tab
4. Fill in:
   - Beta App Description (see APP_STORE_CONTENT.md)
   - Feedback Email: ajdrake@gmail.com
   - Privacy Policy URL (see step 7)
5. Answer Export Compliance: "No" (if using standard HTTPS only)

---

## Step 7: Create Privacy Policy (20 minutes)

**REQUIRED before TestFlight can be used**

1. Edit `PRIVACY_POLICY_TEMPLATE.md`
2. Fill in all [BRACKETS] with your information
3. Host at a public URL (GitHub Pages recommended)
4. Add URL to App Store Connect

**Quick hosting with GitHub Pages:**
```bash
# Create a new GitHub repo called "elevator-privacy"
# Add the privacy policy as index.html
# Enable GitHub Pages in repo settings
# URL: https://ajdrake.github.io/elevator-privacy/
```

---

## Step 8: Add Testers (5 minutes)

In App Store Connect > TestFlight:
1. Click "App Store Connect Users"
2. Add internal testers
3. Enable "Automatic Distribution"
4. Testers receive email invitations

---

## Step 9: Install and Test (10 minutes)

1. Install TestFlight app from App Store
2. Open invitation email
3. Tap "View in TestFlight"
4. Install "Elevator System"
5. Test core functionality

---

## Troubleshooting

### Build fails
```bash
# Reset credentials and try again
eas credentials --platform ios
# Select "Remove all credentials"
# Then "Set up credentials"
eas build --platform ios --profile production
```

### Can't submit to TestFlight
- Verify Apple ID has App Manager or Admin role
- Check 2FA is enabled
- Try logging out and back in

### App crashes in TestFlight
- Check backend URL is production (backend.adapt-llc.com)
- Verify backend is publicly accessible
- Check crash logs in App Store Connect

---

## What's Been Configured

All configuration files are ready:
- **app.json** - Updated with bundle ID and iOS settings
- **eas.json** - Build profiles configured
- **config.js** - Backend URL set to production

---

## Next Steps After TestFlight

1. Complete testing with internal testers
2. Capture full screenshot set (see SCREENSHOTS_GUIDE.md)
3. Finalize App Store marketing content
4. Submit for App Store Review

See `TESTFLIGHT_SETUP.md` for detailed documentation.

---

## Cost Summary

- Apple Developer: $99/year (required)
- EAS Build: Free (30 builds/month)
- Total: $99/year
