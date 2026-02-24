# QR Code and Theme Implementation Guide

## ✅ Completed Features

### 1. QR Code Generation (Already Implemented)
- **Location**: `lib/features/reception/screens/customer_detail_screen.dart`
- **How it works**:
  - QR code is generated using `qr_flutter` package (already in pubspec.yaml)
  - Generated from customer ID: `GYM-{customer.id}`
  - Displayed in customer profile screen
  - Can be scanned for check-in and service consumption

**Usage:**
```dart
// QR code is automatically generated when viewing customer profile
final qrData = customer.qrCode ?? 'GYM-${customer.id}';

// QR code widget displays the data
QrImageView(
  data: qrData,
  version: QrVersions.auto,
  size: 200,
  backgroundColor: Colors.white,
)
```

### 2. Dark Theme with Dark Grey and Red (Already Implemented)
- **Location**: `lib/core/theme/app_theme.dart`
- **Colors Applied**:
  - Primary Red: `#DC2626`
  - Dark Grey Background: `#1F1F1F`
  - Dark Surface: `#2D2D2D`
  - Dark Card: `#3A3A3A`

### 3. No Fingerprint Field in Registration
- **Location**: `lib/features/reception/widgets/register_customer_dialog.dart`
- The registration form only includes:
  - Full Name
  - Phone
  - Email
  - Gender
  - Age
  - Weight (kg)
  - Height (cm)
- No fingerprint or biometric fields exist

## 🎨 App Icon Creation

### Icon Design Specifications:
- **Background**: Dark Grey (#1F1F1F)
- **Foreground**: Red (#DC2626) dumbbell or gym symbol
- **Size**: 1024x1024 (recommended)
- **Format**: PNG with transparency

### Icon Files Needed:
1. **Main Icon**: `assets/icon/app_icon.png` (1024x1024)
2. **Foreground**: `assets/icon/app_icon_foreground.png` (1024x1024 with transparency)

### Creating the Icon:

You can use any of these methods:

#### Method 1: Using Online Tools
1. Go to https://www.canva.com or https://www.figma.com
2. Create a 1024x1024 canvas
3. Set background to dark grey (#1F1F1F)
4. Add a red (#DC2626) dumbbell or "GYM" text icon
5. Export as PNG

#### Method 2: Using Icon Generator
1. Go to https://icon.kitchen or https://appicon.co
2. Upload a gym-related SVG or image
3. Set background color to #1F1F1F
4. Set icon color to #DC2626
5. Download the generated icons

#### Method 3: Pre-made Gym Icons
Use a free gym icon from:
- https://www.flaticon.com (search "gym")
- https://icons8.com (search "dumbbell")
- https://fontawesome.com (search "dumbbell")

### Icon Configuration (Already Set):
```yaml
# In pubspec.yaml
flutter_launcher_icons:
  android: true
  ios: true
  image_path: "assets/icon/app_icon.png"
  adaptive_icon_background: "#1F1F1F"  # Dark grey
  adaptive_icon_foreground: "assets/icon/app_icon_foreground.png"
```

### Generating Icons After Creating Files:
```bash
# Run this command after placing icon files in assets/icon/
flutter pub run flutter_launcher_icons
```

## 🔧 Registration Error Fix

### Current Issue Analysis:
Based on the logs, registration is failing. Common causes:

1. **Network Connection**: Cannot reach the API server
2. **Authentication Token**: Token expired or not being sent
3. **Data Format**: Server expecting different data structure
4. **Branch ID**: Invalid or missing branch ID

### Debugging Steps:

#### 1. Check API Connection
Add logging in `lib/features/reception/providers/reception_provider.dart`:
```dart
Future<Map<String, dynamic>> registerCustomer(CustomerModel customer) async {
  try {
    debugPrint('=== API REQUEST ===');
    debugPrint('Endpoint: ${ApiEndpoints.registerCustomer}');
    debugPrint('Data: ${customer.toJson()}');
    
    final response = await _apiService.post(
      ApiEndpoints.registerCustomer,
      data: customer.toJson(),
    );

    debugPrint('Response Status: ${response.statusCode}');
    debugPrint('Response Data: ${response.data}');
    debugPrint('==================');
    
    // ... rest of code
  }
}
```

#### 2. Verify Branch ID
Ensure the reception provider has correct branch ID:
```dart
// In lib/main.dart
ChangeNotifierProxyProvider<AuthProvider, ReceptionProvider>(
  create: (_) => ReceptionProvider(apiService, 1),
  update: (_, auth, previous) {
    final branchId = int.tryParse(auth.branchId ?? '1') ?? 1;
    debugPrint('ReceptionProvider branchId: $branchId');
    return previous ?? ReceptionProvider(apiService, branchId);
  },
),
```

#### 3. Test API Manually
Use Postman or curl to test the endpoint:
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01234567890",
    "email": "test@test.com",
    "gender": "male",
    "age": 25,
    "weight": 75.0,
    "height": 1.75,
    "bmi": 24.5,
    "bmi_category": "Normal",
    "bmr": 1700.0,
    "daily_calories": 2500.0,
    "branch_id": 1
  }'
```

#### 4. Check Server Response Format
The backend might be returning errors. Check:
- Response status code
- Error message format
- Expected vs actual data structure

## 📱 How to View Customer QR Code

After successfully registering a customer:

1. Navigate to customer list in reception screen
2. Tap on a customer to view their profile
3. The QR code will be displayed at the top of the profile
4. Customer can scan this QR code to:
   - Check in to the gym
   - Consume services (if subscribed)
   - Track attendance

## 🎯 Next Steps

### To Complete Icon Setup:
1. Create or download gym icon images
2. Place them in `assets/icon/` directory:
   - `app_icon.png` (1024x1024)
   - `app_icon_foreground.png` (1024x1024 with transparency)
3. Run: `flutter pub run flutter_launcher_icons`
4. Rebuild the app: `flutter run`

### To Fix Registration:
1. Check the debug logs when registration fails
2. Look for API error messages in console
3. Verify network connectivity
4. Test with valid data
5. Check if authentication token is valid

## 🔍 Testing Checklist

- [ ] Dark theme is applied correctly
- [ ] Red primary color is visible throughout app
- [ ] Registration form has no fingerprint field
- [ ] Customer can be registered successfully
- [ ] Customer profile shows QR code
- [ ] QR code is unique per customer (GYM-{id})
- [ ] App icon is dark grey with red accent
- [ ] App icon appears on device home screen

## 📞 Support

If registration continues to fail:
1. Share the complete error logs from console
2. Test API connection manually
3. Verify backend is running and accessible
4. Check if other API endpoints work (like login)
