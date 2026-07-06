# Privacy Policy Template for Elevator System

## About This Template

This is a template privacy policy for the Elevator System mobile app. You must:
1. Fill in the placeholders marked with [BRACKETS]
2. Review all content for accuracy
3. Host the final policy at a publicly accessible URL
4. Add the URL to App Store Connect

**Required for:** TestFlight and App Store submission

---

# Privacy Policy for Elevator System

**Last Updated:** [INSERT DATE - e.g., January 30, 2026]

## Introduction

This privacy policy describes how Elevator System ("the App", "we", "us", or "our") handles information when you use our mobile application.

**Developer:** [Your Name or Company Name - e.g., Adapt LLC]
**Contact Email:** [Your Email - e.g., ajdrake@gmail.com]
**App Version:** 1.0.0

## Information We Collect

### Personal Information
**The App does NOT collect, store, or transmit any personal information about users.**

We do not collect:
- Names or contact information
- Email addresses or phone numbers
- Location data
- Device identifiers
- User credentials or passwords
- Photos or media files
- Contacts or calendar data

### Technical Information
The App connects to a backend server to provide elevator control functionality. During operation, the following technical data is transmitted:

- Elevator floor requests (floor numbers only)
- Priority levels (Normal, High, Emergency)
- Real-time elevator status updates (current floor, direction, next destination)

**This data relates solely to elevator system operations and contains no personal or identifying information about users.**

## How We Use Information

The technical data transmitted to the backend server is used exclusively to:
- Display real-time elevator status
- Process elevator call requests
- Manage elevator priority queuing
- Enable real-time updates via WebSocket connections

## Network Connections

The App connects to:
- **Backend Server:** backend.adapt-llc.com (or your configured server)
- **Protocol:** HTTPS for API requests, WSS (WebSocket Secure) for real-time updates
- **Purpose:** Elevator system monitoring and control

All network connections use industry-standard encryption (TLS/SSL).

## Data Storage

**No data is stored on your device** beyond standard app configuration and temporary session data required for operation.

**No data is persistently stored on backend servers** related to individual users or app usage patterns.

## Third-Party Services

The App does NOT integrate with or share data with:
- Analytics services
- Advertising networks
- Social media platforms
- Crash reporting services
- Any other third-party services

## Children's Privacy

The App does not knowingly collect information from children under the age of 13. The App is designed for facility management and building operations, typically used by adult professionals.

## Data Security

We implement appropriate technical measures to protect data transmitted between the App and backend server:
- HTTPS/TLS encryption for all API requests
- WSS (WebSocket Secure) encryption for real-time updates
- No persistent storage of user data
- No user authentication required (no passwords to protect)

## Your Rights

Since we do not collect or store personal information, there is no personal data to:
- Access
- Modify
- Delete
- Export
- Restrict processing of

## Changes to This Policy

We may update this privacy policy from time to time. Changes will be reflected by updating the "Last Updated" date at the top of this policy. Continued use of the App after changes constitutes acceptance of the updated policy.

## International Users

The App and backend server are operated in [INSERT COUNTRY - e.g., United States]. If you use the App from outside this country, your data may be transmitted to and processed in [INSERT COUNTRY].

## California Privacy Rights (CCPA)

California residents: Since we do not collect personal information, CCPA data rights do not apply to this App.

## European Privacy Rights (GDPR)

European Union residents: Since we do not collect or process personal data, GDPR requirements do not apply to this App.

## Contact Us

If you have questions about this privacy policy or the App's data practices, please contact:

**Email:** [INSERT EMAIL - e.g., ajdrake@gmail.com]
**Website:** [INSERT WEBSITE - e.g., https://adapt-llc.com]
**Address:** [INSERT MAILING ADDRESS - Optional]

## Consent

By using the Elevator System app, you consent to this privacy policy.

---

## For App Store Submission

**Privacy Policy URL:** [INSERT URL after hosting this policy]

---

## Hosting Options

You must host this privacy policy at a publicly accessible URL. Options:

### Option 1: GitHub Pages (Free, Recommended)
1. Create a repository: `elevator-system-privacy`
2. Add this file as `index.md` or `privacy.html`
3. Enable GitHub Pages in repository settings
4. URL will be: `https://[username].github.io/elevator-system-privacy/`

### Option 2: Company Website
Host at: `https://adapt-llc.com/elevator-system/privacy`

### Option 3: Simple Hosting Services
- Netlify (free)
- Vercel (free)
- GitLab Pages (free)

---

## Verification Checklist

Before submitting to TestFlight:
- [ ] All [BRACKETS] filled in with actual information
- [ ] Date updated to current date
- [ ] Contact email is correct and monitored
- [ ] Policy hosted at public URL
- [ ] URL tested and loads correctly
- [ ] URL is HTTPS (secure)
- [ ] Policy accurately describes app data practices
- [ ] No false or misleading statements
