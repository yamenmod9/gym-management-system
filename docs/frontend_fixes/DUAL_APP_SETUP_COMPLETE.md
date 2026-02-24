# Dual App Setup Complete! 🎉

Your Flutter project is now configured to run **both Client and Staff apps simultaneously** on the same device.

## ✅ What Was Configured

### 1. **Android Product Flavors**
   - Created two flavors: `client` and `staff`
   - Each has a unique application ID:
     - Client: `com.example.gym_frontend.client`
     - Staff: `com.example.gym_frontend.staff`
   - Different app names visible on device:
     - Client: "Gym Client"
     - Staff: "Gym Staff"

### 2. **Debug Port Configuration**
   - Client App uses ports 50001-50002
   - Staff App uses ports 50003-50004
   - This prevents debug session conflicts

### 3. **IDE Run Configurations**
   - **IntelliJ/Android Studio**: Updated `.idea/runConfigurations/`
   - **VS Code**: Created `.vscode/launch.json` with compound configuration

## 🚀 How to Use

### Method 1: IntelliJ IDEA / Android Studio (Recommended)

1. Open the run configuration dropdown (top toolbar)
2. You'll see two configurations:
   - **"Client App"** - Runs the client app
   - **"Staff app"** - Runs the staff app

3. To run both simultaneously:
   - Click on "Client App" and press Run (▶️)
   - Wait for it to install and start
   - Click on "Staff app" and press Run (▶️)
   - Both apps now run side-by-side!

### Method 2: VS Code

1. Open the Run and Debug panel (Ctrl+Shift+D)
2. Select from dropdown:
   - **"Client App"** - Runs client app only
   - **"Staff App"** - Runs staff app only  
   - **"Both Apps"** - Runs BOTH simultaneously! ⚡

### Method 3: Command Line

Run in separate terminals:

**Terminal 1 - Client:**
```bash
flutter run --flavor client -t lib/client_main.dart --observatory-port=50001 --device-vmservice-port=50002
```

**Terminal 2 - Staff:**
```bash
flutter run --flavor staff -t lib/main.dart --observatory-port=50003 --device-vmservice-port=50004
```

### Method 4: Batch Script (Windows)

Double-click `run_both_apps.bat` - it will launch both apps automatically!

## 📱 On Your Device

After running both apps, you'll see two separate icons:
- 📱 **Gym Client** - The customer-facing app
- 👨‍💼 **Gym Staff** - The staff/admin app

Both can run at the same time with no conflicts!

## 🔧 Building Release APKs

**Client App:**
```bash
flutter build apk --flavor client -t lib/client_main.dart --release
# Output: build/app/outputs/flutter-apk/app-client-release.apk
```

**Staff App:**
```bash
flutter build apk --flavor staff -t lib/main.dart --release
# Output: build/app/outputs/flutter-apk/app-staff-release.apk
```

## 🐛 Debugging Both Apps

With this setup, you can:
- ✅ Debug both apps simultaneously
- ✅ Hot reload works on both
- ✅ DevTools available for both
- ✅ No port conflicts
- ✅ No application ID conflicts

Each app has its own debug session and can be developed independently!

## ⚠️ Important Notes

1. **First Time Setup**: After pulling these changes, run:
   ```bash
   cd android
   ./gradlew clean
   cd ..
   flutter clean
   flutter pub get
   ```

2. **Uninstall Old Versions**: If you have the old app installed (without flavors), uninstall it first to avoid conflicts.

3. **iOS Support**: To enable similar functionality on iOS, you'll need to configure schemes in Xcode. Let me know if you need this!

## 🎯 Benefits

- ✅ Test real-time interactions between client and staff
- ✅ No need to constantly uninstall/reinstall
- ✅ Independent debugging sessions
- ✅ Faster development cycle
- ✅ Better testing workflow

## 📞 Need Help?

If you encounter any issues:
1. Run `flutter clean && cd android && ./gradlew clean`
2. Restart your IDE
3. Make sure you're using the latest Flutter SDK
4. Check that your device has enough storage for both apps

---

**Happy Coding! 🚀**

