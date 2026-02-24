# Running Both Apps Simultaneously

This project is now configured to run both the **Client App** and **Staff App** simultaneously on the same device.

## How It Works

The project uses Android product flavors to create two separate app variants:
- **Client App**: `com.example.gym_frontend.client`
- **Staff App**: `com.example.gym_frontend.staff`

Each app has:
- Different application ID (allows installation side-by-side)
- Different app name on device
- Different debug ports (allows simultaneous debugging)

## Run Configurations

### Option 1: Using IntelliJ/Android Studio Run Configurations

1. **To run the Client App:**
   - Select "Client App" from the run configuration dropdown
   - Click the Run button
   - The app will install as "Gym Client"

2. **To run the Staff App:**
   - Select "Staff app" from the run configuration dropdown  
   - Click the Run button
   - The app will install as "Gym Staff"

Both apps can run at the same time!

### Option 2: Using Command Line

**For Client App:**
```bash
flutter run --flavor client -t lib/client_main.dart --observatory-port=50001 --device-vmservice-port=50002
```

**For Staff App:**
```bash
flutter run --flavor staff -t lib/main.dart --observatory-port=50003 --device-vmservice-port=50004
```

## Debug Ports

- **Client App:** 
  - Observatory: 50001
  - Device VM Service: 50002
  
- **Staff App:**
  - Observatory: 50003
  - Device VM Service: 50004

## Building Release APKs

**Client App:**
```bash
flutter build apk --flavor client -t lib/client_main.dart
```

**Staff App:**
```bash
flutter build apk --flavor staff -t lib/main.dart
```

## Troubleshooting

### Apps won't install side-by-side
- Make sure you're using the correct flavor for each app
- Uninstall any previous versions of the app that had the same package name

### Debug session conflicts
- Ensure each app is using different ports (configured in run configurations)
- If ports are in use, try closing other Flutter debugging sessions

### Gradle sync issues
- Run: `cd android && ./gradlew clean`
- Then rebuild the project

## App Identifiers

- **Client App ID**: com.example.gym_frontend.client
- **Staff App ID**: com.example.gym_frontend.staff
- **Display Names**: "Gym Client" and "Gym Staff"

