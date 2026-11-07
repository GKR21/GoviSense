# GoviSense Farmer Mobile App (Flutter APK)

**Package ID:** `lk.gov.govisense.farmer`  
**Target Platform:** Android (APK) & iOS  
**Backend:** GoviSense FastAPI Server (`http://<server-ip>:8000`)

---

## 1. Overview
GoviSense Farmer is a dedicated Flutter mobile application for Sri Lankan smallholder farmers. It connects directly with the GoviSense AI pipeline to:
1. Provide personalized **Top-3 Crop Recommendations** with suitability scores, water requirements, and P10–P90 farmgate price prediction intervals.
2. Ingest empirical **Ground Planting Declarations** (Closed-Loop Feedback) that feed directly into the national Supply Pressure Index (SPI) recalculation and policy dashboard.
3. Display daily wholesale and retail market prices from Dedicated Economic Centres (Dambulla, Keppetipola, Pettah).
4. Provide trilingual localization: English, Sinhala (සිංහල), and Tamil (தமிழ்).

---

## 2. Project Structure
```
farmer_app/
├── android/                        # Android native configurations & build files
│   ├── app/
│   │   ├── build.gradle            # APK build settings (minSdk 21, targetSdk 34)
│   │   └── src/main/
│   │       └── AndroidManifest.xml # Permissions (INTERNET, ACCESS_NETWORK_STATE)
│   ├── build.gradle
│   └── settings.gradle
├── lib/
│   ├── main.dart                   # Application entry point & theme
│   ├── config/
│   │   └── app_config.dart         # Backend API URLs & constants
│   ├── constants/
│   │   ├── colors.dart             # Emerald glassmorphic dark palette
│   │   └── strings.dart            # Trilingual localization (EN, SI, TA)
│   ├── models/
│   │   ├── crop_recommendation.dart # AI 1 / WP2 recommendation data model
│   │   ├── farmer_profile.dart     # Soil, land extent, and irrigation profile
│   │   └── planting_report.dart    # Ground truth submission schema
│   ├── providers/
│   │   └── app_state.dart          # Reactive state management
│   ├── screens/
│   │   ├── home_screen.dart        # Farm dashboard & quick action cards
│   │   ├── top3_advisor_screen.dart# ML-powered crop ranking & metrics
│   │   ├── report_planting_screen.dart # Closed-loop actual planting logger
│   │   ├── market_prices_screen.dart   # HARTI DEC wholesale & retail prices
│   │   └── profile_screen.dart     # Farm parcel configuration & language selector
│   └── services/
│       └── api_service.dart        # REST client connecting to FastAPI
└── pubspec.yaml                    # Flutter dependencies (http, provider, intl)
```

---

## 3. Local Environment & Running in Android Studio

### Configured Local Tools
- **Android Studio:** `C:\Program Files\Android\Android Studio\bin\studio64.exe`
- **Android SDK:** `C:\Users\User\AppData\Local\Android\Sdk`
- **Pre-configured Emulator:** `Medium_Phone_API_37.0`
- **JDK (JBR):** `C:\Program Files\Android\Android Studio\jbr`

### One-Click Launchers
From the project root (`D:\GoviSence`):
1. **Launch Emulator:** Double-click [`launch_mobile_emulator.bat`](file:///d:/GoviSence/launch_mobile_emulator.bat) to spin up `Medium_Phone_API_37.0`.
2. **Open in Android Studio:** Double-click [`open_farmer_app_studio.bat`](file:///d:/GoviSence/open_farmer_app_studio.bat) to open the project in Android Studio.

### Opening in Android Studio
1. Start Android Studio: `studio64.exe` or use `open_farmer_app_studio.bat`.
2. Open either:
   - Root project: `d:\GoviSence\farmer_app` (if Flutter & Dart plugins are installed).
   - Native Android module: `d:\GoviSence\farmer_app\android` (to inspect Gradle dependencies, manifests, and build variants).
3. If the Flutter plugin is not yet installed in Android Studio:
   - Go to **Plugins** -> search for **Flutter** (by flutter.dev) -> Click **Install** -> Restart IDE.
4. Select the device dropdown: choose **Medium Phone API 37.0** or your connected Android phone.
5. Click **Run** (`Shift + F10`) or debug.

---

## 4. How to Build the Standalone Android APK

### Prerequisites
1. Install [Flutter SDK](https://docs.flutter.dev/get-started/install/windows) (Version 3.0.0 or higher).
2. Install Android Studio with Android SDK Command-line Tools.

### Steps to Build
```powershell
# 1. Navigate to the Flutter app directory
cd d:\GoviSence\farmer_app

# 2. Get dependencies
flutter pub get

# 3. Build standalone Android release APK
flutter build apk --release
```

The output standalone APK will be located at:
```
farmer_app/build/app/outputs/flutter-apk/app-release.apk
```
This `.apk` file can be directly installed on any Android smartphone.

---

## 4. Connecting to the Backend Server
In `lib/config/app_config.dart`:
```dart
// For local Android Emulator:
static String baseUrl = 'http://10.0.2.2:8000';

// For physical Android device on the same local Wi-Fi:
static String baseUrl = 'http://192.168.x.x:8000';

// For deployed cloud/government server:
static String baseUrl = 'https://api.govisense.agr.gov.lk';
```

