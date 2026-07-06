# TestFlight Submission Checklist

## Pre-Submission Requirements

### Apple Developer Account
- [ ] Active Apple Developer Program membership ($99/year)
- [ ] Apple ID: ajdrake@gmail.com verified and accessible
- [ ] Two-factor authentication enabled
- [ ] Payment method on file (for annual renewal)
- [ ] Access to App Store Connect confirmed

### Expo Account Setup
- [ ] Expo account created (or existing account verified)
- [ ] Logged into Expo CLI: `eas login`
- [ ] EAS CLI installed: `npm install -g eas-cli`

---

## Configuration Files

### app.json
- [ ] App name set: "Elevator System"
- [ ] Slug set: "elevator-system"
- [ ] Version set: "1.0.0"
- [ ] iOS bundle identifier: "com.adaptllc.elevatorsystem"
- [ ] iOS build number: "1"
- [ ] Owner field set: "ajdrake"
- [ ] Orientation set to "portrait"
- [ ] Icon path configured: "./assets/icon.png"
- [ ] Splash screen configured: "./assets/splash-icon.png"
- [ ] iPad support enabled: "supportsTablet": true
- [ ] Info.plist descriptions added (camera, microphone, photo library)

### eas.json
- [ ] File created at project root
- [ ] Three build profiles configured (development, preview, production)
- [ ] Production profile uses "store" distribution
- [ ] iOS bundle identifier matches app.json
- [ ] Submit configuration includes Apple ID: ajdrake@gmail.com

### package.json
- [ ] App name: "mobile"
- [ ] Version: "1.0.0"
- [ ] All dependencies installed
- [ ] Required packages present:
  - [ ] expo ~54.0.32
  - [ ] @apollo/client ^4.1.3
  - [ ] graphql ^16.12.0
  - [ ] graphql-ws ^6.0.6
  - [ ] react-native 0.81.5

---

## App Assets

### App Icon
- [ ] File exists: `/home/aaron/elevator-system/mobile/assets/icon.png`
- [ ] Dimensions: 1024x1024 pixels
- [ ] Format: PNG (no transparency)
- [ ] Color space: RGB
- [ ] Design follows iOS icon guidelines (no rounded corners, system adds them)

### Splash Screen
- [ ] File exists: `/home/aaron/elevator-system/mobile/assets/splash-icon.png`
- [ ] Aspect ratio appropriate for splash screen
- [ ] Background color set in app.json: "#ffffff"
- [ ] Resize mode set: "contain"

### Adaptive Icon (Android)
- [ ] File exists: `/home/aaron/elevator-system/mobile/assets/adaptive-icon.png`
- [ ] Configured in app.json

---

## Legal and Policy Documents

### Privacy Policy (REQUIRED)
- [ ] Privacy policy drafted (see PRIVACY_POLICY_TEMPLATE.md)
- [ ] Policy hosted at accessible URL
- [ ] URL tested and opens correctly
- [ ] Policy covers:
  - [ ] Data collection (or lack thereof)
  - [ ] Network connections
  - [ ] Third-party services
  - [ ] User rights
  - [ ] Contact information
- [ ] URL ready to add to App Store Connect

### Support URL (REQUIRED)
- [ ] Support URL decided (GitHub, website, or email)
- [ ] URL publicly accessible
- [ ] URL tested and loads correctly
- [ ] Contact information available

### Terms of Service (Optional)
- [ ] Terms of Service drafted (if applicable)
- [ ] Hosted at accessible URL

---

## App Store Content

### Marketing Text
- [ ] App name finalized: "Elevator System" (15/30 chars)
- [ ] Subtitle written: "Real-time elevator control" (28/30 chars)
- [ ] Description written and proofread (891/4000 chars)
- [ ] Keywords optimized (89/100 chars)
- [ ] Promotional text written (167/170 chars)
- [ ] "What's New" text prepared (234/560 chars)
- [ ] Beta app description ready for TestFlight (312 chars)

### App Metadata
- [ ] Primary category selected: Productivity
- [ ] Secondary category selected: Business (optional)
- [ ] Age rating determined: 4+
- [ ] Copyright info ready: "© 2026 Adapt LLC"

### App Review Notes
- [ ] Test credentials prepared (if needed)
- [ ] Demo backend URL provided: backend.adapt-llc.com
- [ ] Instructions for reviewers written
- [ ] Special testing notes documented

---

## Screenshots

### iPhone 6.7" (REQUIRED)
- [ ] Resolution verified: 1290 x 2796 pixels
- [ ] Format: PNG
- [ ] Minimum 3 screenshots captured
- [ ] Maximum 10 screenshots (if using more than 3)
- [ ] Screenshots show key features:
  - [ ] Main elevator status screen
  - [ ] Floor selection interface
  - [ ] Priority selection
  - [ ] Active requests
  - [ ] Emergency mode (optional)
- [ ] Files organized in: `screenshots/6.7-inch/`

### iPhone 6.5" (REQUIRED)
- [ ] Resolution verified: 1242 x 2688 pixels
- [ ] Format: PNG
- [ ] 3-10 screenshots captured
- [ ] Files organized in: `screenshots/6.5-inch/`

### iPhone 5.5" (Optional but recommended)
- [ ] Resolution verified: 1242 x 2208 pixels
- [ ] Format: PNG
- [ ] 3-10 screenshots captured
- [ ] Files organized in: `screenshots/5.5-inch/`

### iPad Pro 12.9" (REQUIRED - app supports iPad)
- [ ] Resolution verified: 2048 x 2732 pixels
- [ ] Format: PNG
- [ ] 3-10 screenshots captured
- [ ] Files organized in: `screenshots/ipad-12.9/`

---

## Backend Configuration

### Production Backend
- [ ] Backend deployed at: backend.adapt-llc.com
- [ ] Backend publicly accessible
- [ ] SSL certificate valid (HTTPS)
- [ ] GraphQL endpoint working: https://backend.adapt-llc.com/graphql
- [ ] WebSocket endpoint working: wss://backend.adapt-llc.com/graphql
- [ ] Health check endpoint responding: https://backend.adapt-llc.com/health

### App Configuration
- [ ] config.js uses production backend URL
- [ ] BACKEND_HOST set to: "backend.adapt-llc.com"
- [ ] Protocol detection working (https/wss for production)
- [ ] No hardcoded localhost or development URLs
- [ ] No debug logs in production build

---

## Build Process

### EAS Build Configuration
- [ ] Run: `eas build:configure`
- [ ] Project ID generated and added to app.json
- [ ] Project linked to Expo account

### iOS Credentials
- [ ] Run: `eas credentials`
- [ ] Apple ID authenticated: ajdrake@gmail.com
- [ ] Two-factor authentication completed
- [ ] Distribution certificate created
- [ ] Provisioning profile created
- [ ] Bundle ID registered: com.adaptllc.elevatorsystem
- [ ] Credentials stored in Expo infrastructure

### Production Build
- [ ] Run: `eas build --platform ios --profile production`
- [ ] Build started successfully
- [ ] Build ID noted: _______________
- [ ] Build completed without errors
- [ ] .ipa file available for download

---

## TestFlight Submission

### App Store Connect Setup
- [ ] Logged into App Store Connect
- [ ] App created: "Elevator System"
- [ ] Bundle ID selected: com.adaptllc.elevatorsystem
- [ ] App Store Connect App ID noted: _______________

### Build Submission
- [ ] Run: `eas submit --platform ios --latest`
- [ ] Apple ID authenticated: ajdrake@gmail.com
- [ ] Build uploaded to App Store Connect
- [ ] Processing started (5-15 minutes)
- [ ] Build available in TestFlight tab

### TestFlight Information
- [ ] Beta App Description added
- [ ] Feedback email set: ajdrake@gmail.com
- [ ] Support URL added
- [ ] Privacy Policy URL added
- [ ] Marketing URL added (optional)
- [ ] Export Compliance answered

### Export Compliance
- [ ] Question answered: "Does your app use encryption?"
  - [ ] Answer: NO (if only using standard HTTPS)
  - [ ] OR Answer: YES and provide documentation
- [ ] Build approved for testing

---

## Tester Setup

### Internal Testing (App Store Connect Users)
- [ ] Internal testing group created
- [ ] Team members added as testers
- [ ] Automatic distribution enabled
- [ ] Testers received email invitations

### External Testing (Optional - requires Beta Review)
- [ ] External testing group created (if needed)
- [ ] Public beta testers added
- [ ] Build submitted for Beta App Review
- [ ] Beta App Review approved (1-2 days)

---

## Testing Phase

### App Installation
- [ ] TestFlight app installed on test device
- [ ] Invitation email received and opened
- [ ] App installed via TestFlight
- [ ] App launches successfully

### Functionality Testing
- [ ] App connects to backend
- [ ] Real-time updates working
- [ ] GraphQL subscription active
- [ ] WebSocket connection stable
- [ ] Floor selection responsive
- [ ] Priority selection working
- [ ] All three priorities function: Normal, High, Emergency
- [ ] Active requests display correctly
- [ ] Current floor updates in real-time
- [ ] Direction indicator accurate
- [ ] No crashes or freezes
- [ ] Network reconnection works
- [ ] Error handling appropriate

### UI/UX Testing
- [ ] Layout correct on iPhone
- [ ] Layout correct on iPad (if supported)
- [ ] Text readable at all sizes
- [ ] Colors and contrast appropriate
- [ ] Buttons responsive to touch
- [ ] Scrolling smooth
- [ ] Status bar appearance correct
- [ ] Splash screen displays properly

### Performance Testing
- [ ] App loads quickly
- [ ] Real-time updates arrive without delay
- [ ] No memory leaks during extended use
- [ ] Reconnection after network loss works
- [ ] Multiple rapid requests handled gracefully

---

## Issue Resolution

### If Build Fails
- [ ] Review build logs in Expo dashboard
- [ ] Check for credential issues
- [ ] Verify bundle ID configuration
- [ ] Run: `eas credentials` to reset if needed
- [ ] Try build again after fixes

### If Submission Fails
- [ ] Check App Store Connect for error messages
- [ ] Verify Apple ID has correct permissions
- [ ] Ensure bundle ID matches across all configs
- [ ] Check for missing compliance information
- [ ] Resubmit after addressing issues

### If App Crashes in TestFlight
- [ ] Check crash logs in App Store Connect
- [ ] Review different from development build
- [ ] Test on multiple devices
- [ ] Check for missing API keys or configuration
- [ ] Verify backend URL is production (not localhost)
- [ ] Fix issues and create new build

---

## Post-TestFlight Next Steps

### When Ready for App Store
- [ ] TestFlight testing complete
- [ ] All critical bugs fixed
- [ ] Feedback incorporated
- [ ] Full screenshot set prepared (all required sizes)
- [ ] App Store listing complete
- [ ] Preview video created (optional)
- [ ] Pricing and availability set
- [ ] Age rating confirmed
- [ ] Submit for App Store Review

### App Store Review Timeline
- [ ] Submission confirmed
- [ ] "Waiting for Review" status
- [ ] Review in progress (typically 1-3 days)
- [ ] Approved OR Rejected with feedback
- [ ] If rejected: Address issues and resubmit
- [ ] If approved: App goes live or scheduled release

---

## Emergency Rollback Plan

### If Critical Issue Found After Release
- [ ] Remove app from TestFlight (stops new downloads)
- [ ] Notify active testers of issue
- [ ] Fix bug in codebase
- [ ] Increment build number
- [ ] Create new build: `eas build --platform ios --profile production`
- [ ] Submit updated build: `eas submit --platform ios --latest`
- [ ] Test thoroughly before re-enabling

---

## Documentation Checklist

### Project Documentation
- [ ] TESTFLIGHT_SETUP.md reviewed
- [ ] APP_STORE_CONTENT.md reviewed
- [ ] SCREENSHOTS_GUIDE.md reviewed
- [ ] TESTFLIGHT_CHECKLIST.md (this file) reviewed
- [ ] PRIVACY_POLICY_TEMPLATE.md reviewed

### Build Information
- [ ] Build ID documented: _______________
- [ ] Build date: _______________
- [ ] App Store Connect App ID: _______________
- [ ] Bundle ID: com.adaptllc.elevatorsystem
- [ ] Version: 1.0.0
- [ ] Build number: 1

---

## Key Contacts and URLs

### Apple Resources
- Apple Developer Portal: https://developer.apple.com
- App Store Connect: https://appstoreconnect.apple.com
- TestFlight: https://developer.apple.com/testflight/

### Expo Resources
- Expo Dashboard: https://expo.dev
- EAS Build Dashboard: https://expo.dev/accounts/ajdrake/projects/elevator-system/builds
- Expo Documentation: https://docs.expo.dev

### Project Resources
- Backend URL: https://backend.adapt-llc.com
- Health check: https://backend.adapt-llc.com/health
- GraphQL playground: https://backend.adapt-llc.com/graphql

### Account Information
- Apple ID: ajdrake@gmail.com
- Expo username: ajdrake
- Bundle ID: com.adaptllc.elevatorsystem

---

## Timeline Estimate

### Day 1: Setup and Configuration (1-2 hours)
- Install EAS CLI
- Configure project
- Set up credentials
- Create privacy policy

### Day 2: Build and Submit (2-3 hours)
- Capture screenshots
- Create build
- Upload to App Store Connect
- Configure TestFlight

### Day 3: Testing (1-2 days)
- Internal testing
- Bug fixes if needed
- Gather feedback

### Day 4+: App Store Preparation (2-4 hours)
- Complete all screenshots
- Finalize marketing content
- Submit for App Store Review

### App Store Review: 1-3 days
- Apple reviews submission
- Approval or feedback

**Total time to TestFlight: 1-3 days**
**Total time to App Store: 4-7 days**

---

## Success Criteria

### TestFlight Success
- [ ] App available in TestFlight
- [ ] At least one tester successfully installs
- [ ] App launches and connects to backend
- [ ] Core functionality verified working
- [ ] No critical crashes

### Ready for App Store
- [ ] All TestFlight testing complete
- [ ] All checklist items completed
- [ ] All required screenshots uploaded
- [ ] Marketing content finalized
- [ ] Privacy policy accessible
- [ ] Support URL functional
- [ ] Export compliance completed

---

## Notes Section

Use this space to track important information during your submission:

**Build IDs:**
- First build: _______________
- Current build: _______________

**App Store Connect App ID:**
_______________

**Important Dates:**
- Project started: _______________
- First TestFlight build: _______________
- App Store submission: _______________
- App Store approval: _______________

**Tester Emails:**
1. _______________
2. _______________
3. _______________

**Issues Encountered:**
- Issue 1: _______________
- Resolution: _______________

**Feedback Received:**
- Feedback 1: _______________
- Action taken: _______________

---

## Final Pre-Submission Verification

Before running `eas build`:
- [ ] All checklist items above marked complete
- [ ] Code committed to version control
- [ ] Backend accessible and tested
- [ ] Assets verified and in place
- [ ] Configuration files reviewed one final time
- [ ] Ready to begin build process

**You're ready to submit to TestFlight!**

Follow the step-by-step instructions in `TESTFLIGHT_SETUP.md` to proceed with the build and submission process.
