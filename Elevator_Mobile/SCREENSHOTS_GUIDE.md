# App Store Screenshots Guide

## Overview

Apple requires screenshots for TestFlight and App Store submission. This guide covers requirements, how to capture them, and best practices.

---

## Required Screenshot Sizes

### iPhone Screenshots (Required)

**iPhone 6.7" Display** - REQUIRED
- Devices: iPhone 14 Pro Max, 15 Pro Max, 15 Plus, 16 Pro Max
- Resolution: **1290 x 2796 pixels** (portrait)
- Aspect ratio: 9:19.5

**iPhone 6.5" Display** - REQUIRED
- Devices: iPhone 11 Pro Max, XS Max
- Resolution: **1242 x 2688 pixels** (portrait)
- Aspect ratio: 9:19.5

**iPhone 5.5" Display** - Optional
- Devices: iPhone 8 Plus, 7 Plus, 6s Plus
- Resolution: **1242 x 2208 pixels** (portrait)
- Aspect ratio: 9:16

### iPad Screenshots (Required if app supports iPad)

**iPad Pro 12.9" Display** - REQUIRED (app supports iPad)
- Devices: iPad Pro 12.9" (all generations)
- Resolution: **2048 x 2732 pixels** (portrait)
- Aspect ratio: 3:4

---

## Screenshot Requirements

### Technical Requirements
- **Format**: PNG or JPEG (PNG recommended)
- **Color space**: RGB (sRGB or P3)
- **Quantity**: 3-10 screenshots per device size
- **Order**: Screenshots appear in App Store in the order uploaded
- **File size**: Max 500 MB per screenshot
- **Status bar**: Can show or hide device status bar

### Content Requirements
- Screenshots must be actual app screenshots (not mockups)
- Must accurately represent current app version
- Cannot include device frames (Apple adds them automatically)
- No transparency allowed
- No borders or edges around screenshots
- Must not contain pricing information
- Must not reference competing platforms

---

## Capturing Screenshots

### Method 1: iOS Simulator (Easiest for exact sizes)

#### Step 1: Install and run app in simulator

```bash
cd /home/aaron/elevator-system/mobile
npx expo start --ios
```

Press `i` to open in iOS Simulator

#### Step 2: Select correct device size

In iOS Simulator:
- Menu: **Device > iPhone 14 Pro Max** (for 6.7" screenshots)
- Menu: **Device > iPhone 11 Pro Max** (for 6.5" screenshots)
- Menu: **Device > iPad Pro (12.9-inch)** (for iPad screenshots)

#### Step 3: Take screenshots

**Option A - Simulator Built-in:**
- Menu: **File > New Screen Shot** (⌘+S)
- Saves to Desktop as PNG at exact required resolution

**Option B - Keyboard:**
- Press **⌘+S** while simulator is active
- Automatically saves at correct resolution

#### Step 4: Verify screenshot dimensions

```bash
# On macOS
sips -g pixelWidth -g pixelHeight ~/Desktop/Simulator*.png

# On Linux
identify ~/Desktop/Simulator*.png
```

### Method 2: Real Device (for authentic screenshots)

#### Step 1: Take screenshots on device

**On iPhone:**
- Press **Side button + Volume Up** simultaneously
- Screenshot saves to Photos app

**On iPad:**
- Press **Top button + Volume Up** simultaneously

#### Step 2: Transfer to computer

- AirDrop to Mac
- Or use Photos sync
- Or email to yourself

#### Step 3: Resize if needed

Real device screenshots may not match exact required dimensions. Use image editing software to resize:

**Using ImageMagick:**
```bash
# Resize iPhone 14 Pro Max screenshot to 6.7" requirement
convert original.png -resize 1290x2796 -background white -gravity center -extent 1290x2796 output.png

# Resize to 6.5" requirement
convert original.png -resize 1242x2688 -background white -gravity center -extent 1242x2688 output.png
```

---

## Screenshot Content Strategy

### Start Simple, Add Complexity Progressively

Following your principle of starting limited and building up:

### Set 1: Essential Screenshots (Minimum Viable)

**Screenshot 1: Main Status Screen**
- Shows elevator at a floor (e.g., Floor 8)
- Direction indicator (Up/Down/Idle)
- Clean, simple interface
- This is your "hero" screenshot

**Screenshot 2: Floor Selection**
- 20-floor grid visible
- One or two floors highlighted (current and requested)
- Shows the core interaction

**Screenshot 3: Priority Selection**
- Three priority buttons visible
- One selected (e.g., Normal)
- Shows a key feature

### Set 2: Enhanced Screenshots (Added Detail)

Build on Set 1 by adding:

**Screenshot 4: Active Requests**
- Multiple requests visible in the list
- Different priorities shown
- Demonstrates system activity

**Screenshot 5: Real-time Update**
- Elevator in motion
- Next floor indicator visible
- Shows the real-time capability

### Set 3: Complete Set (Full Context)

Add finishing touches:

**Screenshot 6: Emergency Priority**
- Emergency priority selected
- Red/orange visual indicator
- Shows critical feature

**Screenshot 7: Full System View**
- Scrolled view showing multiple active requests
- Elevator serving various floors
- Demonstrates scale

---

## Recommended Screenshot Scenarios

### Scenario 1: Idle State (Screenshot 1)
```
- Current Floor: 1
- Direction: IDLE
- Next Floor: None
- Requests: Empty
- Priority: NORMAL selected
```

### Scenario 2: Active Request (Screenshot 2)
```
- Current Floor: 5
- Direction: UP
- Next Floor: 8
- Requests: Floor 8 (NORMAL)
- Priority: NORMAL selected
- Floor 8 highlighted in green
```

### Scenario 3: Multiple Requests (Screenshot 3)
```
- Current Floor: 10
- Direction: DOWN
- Next Floor: 7
- Requests:
  - Floor 7 (HIGH)
  - Floor 3 (NORMAL)
  - Floor 15 (NORMAL)
- Priority: HIGH selected
```

### Scenario 4: Emergency Priority (Screenshot 4)
```
- Current Floor: 12
- Direction: UP
- Next Floor: 18
- Requests: Floor 18 (EMERGENCY)
- Priority: EMERGENCY selected
- Red/orange color scheme
```

---

## Step-by-Step Screenshot Capture Process

### Step 1: Prepare app state

Start the app and connect to backend:
```bash
cd /home/aaron/elevator-system/mobile
npx expo start --ios
```

### Step 2: Create first scenario (Idle)

1. Wait for app to load and connect
2. Ensure elevator is at floor 1
3. No requests active
4. Take screenshot (⌘+S in Simulator)
5. Name: `01-idle-state.png`

### Step 3: Create second scenario (Single Request)

1. Tap floor 8 to call elevator
2. Wait for request to appear
3. Take screenshot
4. Name: `02-single-request.png`

### Step 4: Create third scenario (Multiple Requests)

1. Call elevator to floor 3 (NORMAL)
2. Change priority to HIGH
3. Call elevator to floor 15
4. Change priority to HIGH
5. Call elevator to floor 7
6. Take screenshot showing all requests
7. Name: `03-multiple-requests.png`

### Step 5: Create fourth scenario (Emergency)

1. Change priority to EMERGENCY
2. Call elevator to floor 18
3. Take screenshot
4. Name: `04-emergency-priority.png`

### Step 6: Create priority selection screenshot

1. Tap priority selector area
2. Ensure all three priority buttons visible
3. Take screenshot
4. Name: `05-priority-selection.png`

---

## Organizing Screenshots

Create a directory structure:

```bash
cd /home/aaron/elevator-system/mobile
mkdir -p screenshots/{6.7-inch,6.5-inch,5.5-inch,ipad-12.9}
```

### Naming Convention

```
screenshots/
├── 6.7-inch/
│   ├── 01-main-status.png
│   ├── 02-floor-selection.png
│   ├── 03-priority-options.png
│   ├── 04-active-requests.png
│   └── 05-emergency-mode.png
├── 6.5-inch/
│   ├── 01-main-status.png
│   ├── 02-floor-selection.png
│   └── ...
└── ipad-12.9/
    ├── 01-main-status.png
    ├── 02-floor-selection.png
    └── ...
```

---

## Screenshot Enhancement (Optional)

### Basic Approach (Start Simple)

Use screenshots as-is from simulator:
- No editing required
- Clean, authentic look
- Fast to produce

### Enhanced Approach (Add Polish)

Add simple annotations:
- Circle key features
- Add brief text labels
- Highlight important buttons

**Tools:**
- macOS Preview (built-in)
- Sketch
- Figma
- Adobe Photoshop

### Advanced Approach (Professional Polish)

Create marketing screenshots:
- Background gradients
- Device frames
- Feature callouts
- Text overlays describing benefits

**Recommended tool:** Figma (free for personal use)

---

## Screenshot Checklist

### Before Capturing

- [ ] App running in simulator
- [ ] Correct device size selected
- [ ] Backend connected and responsive
- [ ] Status bar visible (or hidden consistently)
- [ ] No debug overlays visible

### During Capture

- [ ] Main status screen captured
- [ ] Floor selection interface captured
- [ ] Priority selection captured
- [ ] Active requests visible
- [ ] Emergency mode demonstrated
- [ ] All screenshots in portrait orientation
- [ ] Consistent app state/design across shots

### After Capture

- [ ] All screenshots at correct resolution
- [ ] File format is PNG (recommended) or JPEG
- [ ] Color space is RGB
- [ ] Files under 500 MB each
- [ ] No transparency in images
- [ ] Screenshots organized by device size
- [ ] Files renamed with clear descriptive names

### For Each Device Size

- [ ] iPhone 6.7" - 3-10 screenshots
- [ ] iPhone 6.5" - 3-10 screenshots
- [ ] iPad 12.9" - 3-10 screenshots (if supporting iPad)

---

## TestFlight Screenshot Requirements

**Good news:** TestFlight is more flexible than App Store

### TestFlight Requirements
- Minimum: 1 screenshot
- Maximum: 10 screenshots
- Can use screenshots from any iPhone size
- iPad screenshots optional even if app supports iPad

**Recommendation:** Capture 3-5 screenshots from 6.7" device for TestFlight, then complete full set before App Store submission.

---

## App Store Connect Upload Process

### Step 1: Log into App Store Connect
Visit: https://appstoreconnect.apple.com

### Step 2: Navigate to app
1. Click "My Apps"
2. Select "Elevator System"
3. Click version (e.g., "1.0.0")

### Step 3: Upload screenshots
1. Scroll to "App Preview and Screenshots"
2. Select device size (e.g., "6.7" Display")
3. Drag and drop screenshot files
4. Reorder by dragging if needed
5. Repeat for each device size

### Step 4: Verify
- Preview how screenshots appear in App Store
- Check ordering
- Ensure all required sizes uploaded

---

## Common Issues and Solutions

### Issue: Wrong resolution
**Solution:** Use iOS Simulator's "File > New Screen Shot" feature - it automatically saves at correct resolution

### Issue: Status bar looks messy
**Solution:**
- Hide status bar in app code temporarily for screenshots
- Or use simulator which has clean status bar

### Issue: Screenshots look blurry
**Solution:**
- Ensure using PNG format
- Capture at exact required resolution (don't resize up)
- Use simulator instead of real device for exact dimensions

### Issue: Need screenshots for multiple sizes
**Solution:**
- Capture once at largest size (6.7")
- Apple allows using larger screenshots for smaller device sizes
- They will auto-scale (not recommended but acceptable)

### Issue: App state keeps changing during capture
**Solution:**
- Pause WebSocket connection temporarily
- Or capture from a controlled demo backend
- Or use mock data during screenshot capture

---

## Time-Saving Tips

1. **Capture all scenarios in one simulator session**
   - Set up each scenario
   - Take screenshot
   - Don't close simulator between shots

2. **Use simulator at largest size first (6.7")**
   - Can reuse for smaller sizes if needed
   - Easier to downscale than upscale

3. **Create a screenshot script**
   ```bash
   # Automate device switching and capture
   for device in "iPhone 14 Pro Max" "iPhone 11 Pro Max"; do
     # Open simulator with specific device
     # Capture screenshots
   done
   ```

4. **Batch process with ImageMagick**
   ```bash
   # Resize all screenshots at once
   for img in *.png; do
     convert "$img" -resize 1290x2796 "resized/$img"
   done
   ```

---

## Example Screenshot Descriptions

When uploading to App Store Connect, you can add optional descriptions (not shown to users, just for your reference):

1. "Main elevator status screen showing current floor and direction"
2. "Floor selection grid with 20 floors and visual indicators"
3. "Priority selection interface with Normal, High, and Emergency options"
4. "Active requests list showing multiple pending elevator calls"
5. "Emergency priority mode with critical request highlighted"

---

## Next Steps

1. **Capture essential screenshots** (3-5 screenshots)
2. **Organize files** into proper directories
3. **Verify dimensions** using image properties
4. **Upload to TestFlight** (minimum set)
5. **Complete full set** for App Store submission
6. **Enhance if time permits** (annotations, marketing polish)

---

## Useful Commands

```bash
# Check image dimensions
identify screenshot.png

# Batch check all screenshots
identify screenshots/6.7-inch/*.png

# Resize image
convert input.png -resize 1290x2796 output.png

# Convert JPEG to PNG
convert screenshot.jpg screenshot.png

# Optimize PNG file size
pngcrush input.png output.png
```

---

## Resources

- **Apple Screenshot Specifications**: https://help.apple.com/app-store-connect/#/devd274dd925
- **iOS Simulator Guide**: https://developer.apple.com/documentation/xcode/running-your-app-in-simulator-or-on-a-device
- **ImageMagick Documentation**: https://imagemagick.org/
- **Expo Screenshot Guide**: https://docs.expo.dev/distribution/app-stores/
