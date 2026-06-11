# Nazar: Replit Migration and App Store Runbook

This document is written for a non-technical owner. It explains what has been prepared in this repository, what still requires account access, and the practical steps to launch Nazar outside Replit and package it for the Apple App Store.

## Current product shape

Nazar is currently a web app. The live product is mostly contained in:

- `artifacts/nazar/index.html`
- `artifacts/nazar/public/manifest.json`
- `artifacts/nazar/public/sw.js`

It stores journal entries in the user's own browser using `localStorage`. That means:

- no account is required
- no cloud database is currently needed for journal entries
- entries do not automatically sync between devices
- entries can be lost if a user clears browser data

## What this repository now supports

### 1. Static hosting outside Replit

The app can be built as a static website and hosted on Vercel, Netlify, Cloudflare Pages, or similar services.

Recommended first host: Vercel.

Vercel configuration has been added at:

- `vercel.json`

Recommended Vercel settings:

- Build command: `pnpm --filter @workspace/nazar run build`
- Output directory: `artifacts/nazar/dist/public`
- Install command: `pnpm install --frozen-lockfile`

### 2. PWA assets

The web app manifest expects PNG icons. These are required for mobile install prompts and are useful for iOS packaging.

Expected files:

- `artifacts/nazar/public/icon-192.png`
- `artifacts/nazar/public/icon-512.png`
- `artifacts/nazar/public/apple-touch-icon.png`

### 3. iOS wrapper path

The fastest App Store route is to use Capacitor. Capacitor packages the web app inside a native iOS shell.

Useful commands after dependencies are installed:

```bash
pnpm --filter @workspace/nazar run build
pnpm --filter @workspace/nazar run cap:sync
```

To open the iOS project on a Mac:

```bash
pnpm --filter @workspace/nazar run cap:open:ios
```

## What still requires owner action

These steps require access to accounts that should stay under founder/company control:

1. Create or use an Apple Developer account.
2. Create an App Store Connect app listing.
3. Choose the final bundle ID, for example `com.nazar.journal`.
4. Connect the production domain on the chosen web host.
5. Provide final App Store screenshots, support URL, marketing URL, and privacy policy URL.
6. Submit the app to Apple from Xcode on a Mac.

## Replit migration checklist

1. Deploy the app to Vercel using this repository.
2. Confirm the deployed site loads on desktop and mobile.
3. Confirm journal entries save after closing and reopening the browser.
4. Confirm the app can be added to the iPhone Home Screen.
5. Connect the real domain.
6. Leave Replit running until the new domain is verified.
7. After verification, point users to the new domain.

## App Store checklist

1. Build the Nazar web app.
2. Sync the web build into the Capacitor iOS wrapper.
3. Open the generated iOS project in Xcode.
4. Set the Apple Team and bundle identifier.
5. Add final app icons and launch screen.
6. Test on a real iPhone.
7. Archive the app in Xcode.
8. Upload to App Store Connect.
9. Complete privacy labels.
10. Submit for review.

## Product recommendation

Launch the web app first on a non-Replit host. Then submit the App Store version as a focused, local-first journaling app.

Do not add accounts, payments, or cloud sync before the first store submission unless they are absolutely required. They add privacy, security, support, and review complexity.
