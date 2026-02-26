# 🚀 QUICK RUN GUIDE - Both Apps

## 📱 Running on Android/iOS Device

### Client App (Customer App)
```bash
flutter run -t lib/client_main.dart -d <device-id>
```

### Staff App (Receptionist/Admin App)
```bash
flutter run -t lib/main.dart -d <device-id> --flavor staff
```

**Get device ID:**
```bash
flutter devices
```

---

## 🖥️ Running on Web (Alternative)

### Method 1: Web Server (Recommended)
```bash
# Client App
flutter run -d web-server -t lib/client_main.dart

# Staff App
flutter run -d web-server -t lib/main.dart
```

### Method 2: Build and Serve
```bash
# Build
flutter build web -t lib/main.dart

# Serve (choose one):
# Python
cd build/web && python -m http.server 8000

# Or Node.js
cd build/web && npx serve

# Or PHP
cd build/web && php -S localhost:8000
```

---

## ⚠️ Why Edge/Chrome Direct Launch Fails

**Error you see:**
```
Failed to launch browser after 3 tries
```

**Reasons:**
1. `--flavor` not supported on web platform
2. Web apps need a web server (can't open `file://` directly)
3. CORS and security restrictions
4. Different build configuration needed

**Solution:** Use web-server method or focus on mobile!

---

## 📲 Recommended Setup

### For Development:
1. **Use Android/iOS emulator or physical device**
   - Better testing experience
   - All features work (QR scanner, camera, etc.)
   - Faster hot reload
   
2. **Use Run Configurations in IDE**
   - Already set up for you
   - Just click "Run" button
   - Easier than terminal commands

---

## 🎯 IDE Run Configurations

### IntelliJ/Android Studio/VS Code:

**Client App Configuration:**
```json
{
  "name": "Client App",
  "type": "dart",
  "request": "launch",
  "program": "lib/client_main.dart"
}
```

**Staff App Configuration:**
```json
{
  "name": "Staff App",  
  "type": "dart",
  "request": "launch",
  "program": "lib/main.dart",
  "args": ["--flavor", "staff"]
}
```

Just select the configuration from dropdown and click Run! ▶️

---

## ✅ Quick Commands Cheat Sheet

```bash
# See available devices
flutter devices

# Run client app
flutter run -t lib/client_main.dart

# Run staff app  
flutter run -t lib/main.dart --flavor staff

# Run on specific device
flutter run -t lib/client_main.dart -d SM-A566B

# Hot reload
# Press 'r' in terminal

# Hot restart
# Press 'R' in terminal

# Clean build
flutter clean && flutter pub get

# Check for issues
flutter analyze
```

---

## 🔧 Troubleshooting

### "No devices found"
```bash
# Check devices
flutter devices

# Check Android
adb devices

# Restart ADB
adb kill-server && adb start-server
```

### "Flavor not supported"
- **On Web:** Remove `--flavor staff` or use web-server
- **On Mobile:** Keep the flavor flag

### "Build failed"
```bash
# Clean and rebuild
flutter clean
flutter pub get
flutter run
```

---

## 📚 More Info

- See `ALL_FIXES_APPLIED_FEB14.md` for recent fixes
- See `QUICK_START_FEB14.md` for testing guide
- Check `CLIENT_APP_RUNNING_GUIDE.md` for client app details

---

**TL;DR:**
- ✅ **Mobile:** Use the run configurations, works perfectly
- ❌ **Web Direct:** Won't work (needs web-server)
- ✅ **Web Server:** Use `flutter run -d web-server`

Focus on mobile - it's what the app is designed for! 📱

