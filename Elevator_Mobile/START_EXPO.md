# Start Expo - Instructions

## The Issue
Expo needs to run in an interactive terminal to show the QR code properly.

## Solution: Run Expo in Your Terminal

### Step 1: Open a new terminal in the mobile directory

```bash
cd /home/aaron/elevator-system/mobile
```

### Step 2: Start Expo

**Option A: Same WiFi (Fastest)**
```bash
npx expo start
```

**Option B: Different Networks (More Reliable)**
```bash
npx expo start --tunnel
```

### Step 3: Look for the QR Code

You should see output like:
```
› Metro waiting on exp://172.27.65.193:8081
› Scan the QR code above with Expo Go (Android) or the Camera app (iOS)

[QR CODE APPEARS HERE AS ASCII ART]

› Press s │ switch to development build
› Press a │ open Android
› Press i │ open iOS simulator
› Press w │ open web

› Press j │ open debugger
› Press r │ reload app
› Press m │ toggle menu
› Press o │ open project code in your editor

› Press ? │ show all commands
```

### Step 4: Scan with iPhone

1. Open **Expo Go** app on iPhone
2. Tap **"Scan QR Code"**
3. Point camera at the QR code in terminal
4. App will load!

## Alternative: Manual URL Entry

If QR code doesn't work:

1. Open Expo Go on iPhone
2. Tap "Enter URL manually"
3. Type: `exp://172.27.65.193:8081`
   - Replace IP with what Expo shows in terminal
4. Tap "Connect"

## Troubleshooting

### "Connection timed out"
- **Check**: Are iPhone and computer on same WiFi?
- **Fix**: Use `npx expo start --tunnel` instead

### "Network request failed"
- **Check**: Is backend running?
- **Test**: `curl http://172.27.65.193:8000/health`
- **Fix**: Restart SSH tunnel (see below)

### Can't see QR code
- Make sure terminal window is big enough
- QR code is made of █ characters
- Try pressing `Shift + ?` in Expo to show options

## Backend Connection

The app connects to: `http://172.27.65.193:8000`

To verify backend is accessible:
```bash
curl http://172.27.65.193:8000/health
```

Should return: `{"status":"healthy","version":"2.0.0"}`

### If backend not responding:

```bash
# Restart SSH tunnel
pkill -f "ssh.*8000"
ssh -f -N -L 0.0.0.0:8000:localhost:8000 dell-cloudflare

# Check it worked
curl http://172.27.65.193:8000/health
```

## Next Steps

Once app loads on iPhone:
1. You should see "Elevator System" title
2. Current floor should show (starts at 1)
3. Try tapping a floor number
4. Request should appear in list below

## Need Help?

If you see any errors on iPhone, tell me:
1. Exact error message
2. What screen you see
3. Any red text in Expo terminal

I'll fix it immediately!
