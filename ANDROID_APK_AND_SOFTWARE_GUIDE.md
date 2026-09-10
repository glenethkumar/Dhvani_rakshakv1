# 📱 Dhvani Rakshak - Android App (.apk) & Desktop Software (.exe) Build Guide

This guide explains how to convert **Dhvani Rakshak** into a standalone **Android Application (.apk)** and **Windows Desktop Software (.exe)**.

---

## 🛠️ Method 1: Android App (.apk) using Capacitor & Android Studio

We have pre-configured **Capacitor** ([`frontend/capacitor.config.json`](file:///c:/Users/golag/New%20folder/Dhvani%20Rakshak/frontend/capacitor.config.json)) in the project.

### Step 1: Build the Web App & Add Android Platform
In your terminal, run:
```bash
cd frontend
npm run build
npx cap add android
npx cap sync
```

### Step 2: Open in Android Studio & Export APK
Run:
```bash
npx cap open android
```
1. Android Studio will open the generated native Android project.
2. In Android Studio top menu, click **Build ➡️ Build Bundle(s) / APK(s) ➡️ Build APK(s)**.
3. Once completed, Android Studio will generate the `.apk` file:
   `frontend/android/app/build/outputs/apk/debug/app-debug.apk`
4. Transfer `app-debug.apk` to any Android phone and tap **Install**!

---

## ⚡ Method 2: Instant 1-Click APK Generator (No Android Studio required)

If you don't have Android Studio installed:

1. Deploy your frontend to Vercel (e.g. `https://dhvani-rakshak.vercel.app`).
2. Open [WebIntoApp.com](https://www.webintoapp.com) or [PWABuilder.com](https://www.pwabuilder.com).
3. Paste your Vercel URL (`https://dhvani-rakshak.vercel.app`).
4. Enter App Name: **Dhvani Rakshak**.
5. Click **Generate APK**. Download and install the `.apk` directly on your Android phone!

---

## 💻 Method 3: Windows Desktop Software (.exe)

To run Dhvani Rakshak as a native Windows `.exe` application:

### Step 1: Install Nativeifier / Electron
In your terminal, run:
```bash
npm install -g nativefier
```

### Step 2: Generate Windows Executable (.exe)
Run:
```bash
nativefier --name "Dhvani Rakshak" "http://localhost:5173" --platform windows
```

This creates a standalone `Dhvani Rakshak.exe` file inside your project directory that launches as desktop software!
