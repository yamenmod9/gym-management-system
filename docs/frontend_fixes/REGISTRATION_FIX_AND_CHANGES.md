# Registration Fix and Application Changes

## Summary of Changes Made

### 1. ✅ Theme Already Configured
The app already has a **dark mode theme with dark grey and red colors**:
- **Primary Color**: Red (#DC2626)
- **Background**: Dark Grey (#1F1F1F)
- **Surface**: Medium Dark Grey (#2D2D2D)
- **Cards**: Card Grey (#3A3A3A)

Location: `lib/core/theme/app_theme.dart`

### 2. ✅ QR Code Generation System
The QR code system is already implemented correctly:
- QR codes are generated **after** customer registration using the customer's unique ID
- The registration form sets `qrCode: null` initially
- The backend is expected to generate the QR code after creating the customer
- QR codes are displayed in the Health Report screen
- Format: `CUSTOMER-{id}`

Location: `lib/features/reception/screens/health_report_screen.dart`

### 3. ✅ Improved Error Handling for Registration
**Changes Made:**
- Enhanced error handling in `register_customer_dialog.dart` to show detailed error messages in a dialog
- Improved error capture in `reception_provider.dart` to include:
  - Detailed server error messages
  - Network error descriptions
  - Connection timeout handling
  - Response data for debugging

**Files Modified:**
- `lib/features/reception/widgets/register_customer_dialog.dart`
- `lib/features/reception/providers/reception_provider.dart`

### 4. 🔧 App Icon Location Identified
App icons are located in:
```
android/app/src/main/res/
├── mipmap-hdpi/ic_launcher.png
├── mipmap-mdpi/ic_launcher.png
├── mipmap-xhdpi/ic_launcher.png
├── mipmap-xxhdpi/ic_launcher.png
└── mipmap-xxxhdpi/ic_launcher.png
```

## What Needs To Be Done

### 1. ⚠️ Backend API Issue
The registration is failing because of a backend API issue. When you test again, the app will now show:
- **Detailed error messages** in a dialog
- **Server response data** for debugging
- **Network error details** if connection fails

**Action Required:**
1. Try registering a customer again
2. Note the exact error message shown
3. Share the error details so we can fix the backend API endpoint

### 2. 🎨 Change App Icon
To change the app icon to your custom design:

**Option A: Manual Replacement**
1. Create your icon in these sizes:
   - hdpi: 72x72 px
   - mdpi: 48x48 px
   - xhdpi: 96x96 px
   - xxhdpi: 144x144 px
   - xxxhdpi: 192x192 px

2. Replace these files with your new icon:
   ```
   android/app/src/main/res/mipmap-hdpi/ic_launcher.png
   android/app/src/main/res/mipmap-mdpi/ic_launcher.png
   android/app/src/main/res/mipmap-xhdpi/ic_launcher.png
   android/app/src/main/res/mipmap-xxhdpi/ic_launcher.png
   android/app/src/main/res/mipmap-xxxhdpi/ic_launcher.png
   ```

**Option B: Using flutter_launcher_icons (Recommended)**
1. Add to `pubspec.yaml`:
   ```yaml
   dev_dependencies:
     flutter_launcher_icons: ^0.13.1

   flutter_launcher_icons:
     android: true
     ios: true
     image_path: "assets/icon/app_icon.png"  # Your icon (1024x1024)
     adaptive_icon_background: "#DC2626"     # Red background
     adaptive_icon_foreground: "assets/icon/app_icon_foreground.png"
   ```

2. Run:
   ```bash
   flutter pub get
   flutter pub run flutter_launcher_icons
   ```

## Current Registration Flow

1. User fills in customer details in `RegisterCustomerDialog`
2. Form validates required fields (name, age, weight, height, gender)
3. Health metrics are calculated (BMI, BMR, daily calories)
4. Customer data is sent to `/api/customers/register` endpoint
5. Backend creates customer and generates QR code from customer ID
6. Customer is added to recent customers list
7. Customer can view their QR code in Health Report

## Expected Backend Response

### Success Response (200/201):
```json
{
  "message": "Customer registered successfully",
  "customer": {
    "id": 123,
    "full_name": "John Doe",
    "qr_code": "CUSTOMER-123",
    // ... other fields
  }
}
```

### Error Response (4xx/5xx):
```json
{
  "message": "Error description",
  "error": "Detailed error information"
}
```

## Testing Steps

1. **Test Registration with Detailed Errors:**
   - Run the app: `flutter run`
   - Try to register a new customer
   - If it fails, a dialog will show the exact error
   - Share the error message for debugging

2. **Verify QR Code Display:**
   - Successfully register a customer
   - Navigate to their Health Report
   - Verify QR code displays with format: `CUSTOMER-{id}`
   - Test QR code copying functionality

3. **Test Dark Theme:**
   - Verify all screens use dark grey backgrounds
   - Verify red accent colors throughout
   - Test on different user roles (owner, branch_manager, reception, accountant)

## Notes

- ✅ No face recognition needed (removed as requested)
- ✅ QR code generation based on customer ID (already implemented)
- ✅ Dark mode with dark grey and red theme (already implemented)
- ⚠️ Backend API endpoint needs to be fixed/verified
- 🎨 App icon needs to be replaced with custom design

## Next Steps

1. Test registration and share error details
2. Prepare app icon in required sizes (or single 1024x1024 for automatic generation)
3. Fix any backend API issues identified
4. Test QR code scanning functionality with gym equipment/entry system
