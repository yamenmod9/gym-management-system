# Registration Failure Troubleshooting Guide

## Issue: Registration Fails Every Time

Based on the logs you provided, the app is running but registration is failing. Here's how to diagnose and fix it.

## Common Causes

### 1. Network/API Connection Issues
**Symptoms:**
- App launches successfully
- Can see the registration form
- Registration fails with no clear error

**Check:**
```dart
// Verify API base URL is correct in:
// lib/core/api/api_service.dart

baseUrl: 'https://yamenmod91.pythonanywhere.com'
```

**Test API Manually:**
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
    "weight": 75,
    "height": 1.75,
    "bmi": 24.5,
    "bmi_category": "Normal",
    "bmr": 1700,
    "daily_calories": 2500,
    "branch_id": 1
  }'
```

### 2. Authentication Token Issues
**Symptoms:**
- Login works fine
- Registration fails immediately

**Debug Steps:**
1. Check if token is being sent with request
2. Verify token hasn't expired
3. Check token format in headers

**Add Debug Logging:**
```dart
// In lib/core/api/api_service.dart
Future<Response> post(String endpoint, {dynamic data}) async {
  print('POST $endpoint');
  print('Data: $data');
  print('Headers: ${_dio.options.headers}');
  
  final response = await _dio.post(endpoint, data: data);
  print('Response: ${response.statusCode} - ${response.data}');
  return response;
}
```

### 3. Data Validation Issues
**Symptoms:**
- Form validates on client
- Server rejects the data

**Common Issues:**
- Height sent in wrong format (cm vs meters)
- BMI calculation incorrect
- Required fields missing
- Phone format invalid

**Fix Applied:**
```dart
// In register_customer_dialog.dart
// Height is converted from cm to meters:
final heightInMeters = double.parse(_heightController.text) / 100;

// BMI and other metrics are calculated:
final customer = provider.calculateHealthMetrics(...);
```

### 4. Branch ID Issues
**Symptoms:**
- Registration fails for all customers
- Error mentions branch_id

**Check:**
```dart
// Verify branchId is set correctly
// In lib/features/reception/providers/reception_provider.dart

ReceptionProvider(this._apiService, this.branchId);

// Make sure branchId is passed from auth:
final branchId = int.tryParse(auth.branchId ?? '1') ?? 1;
```

## Debugging Steps

### Step 1: Enable Detailed Logging

Add this to `lib/features/reception/widgets/register_customer_dialog.dart`:

```dart
Future<void> _handleSubmit() async {
  if (!_formKey.currentState!.validate()) return;

  setState(() => _isLoading = true);

  try {
    final provider = context.read<ReceptionProvider>();

    // Calculate health metrics
    final heightInMeters = double.parse(_heightController.text) / 100;
    
    print('=== REGISTRATION DEBUG ===');
    print('Name: ${_nameController.text}');
    print('Age: ${_ageController.text}');
    print('Weight: ${_weightController.text}');
    print('Height (cm): ${_heightController.text}');
    print('Height (m): $heightInMeters');
    print('Branch ID: ${provider.branchId}');
    print('========================');
    
    final customer = provider.calculateHealthMetrics(
      fullName: _nameController.text.trim(),
      weight: double.parse(_weightController.text),
      height: heightInMeters,
      age: int.parse(_ageController.text),
      gender: _gender,
      phone: _phoneController.text.trim().isEmpty ? null : _phoneController.text.trim(),
      email: _emailController.text.trim().isEmpty ? null : _emailController.text.trim(),
      qrCode: null,
    );

    print('Customer Data: ${customer.toJson()}');
    
    final result = await provider.registerCustomer(customer);
    
    print('Registration Result: $result');
    print('========================');
    
    // ... rest of code
  } catch (e) {
    print('ERROR: $e');
    // ... error handling
  }
}
```

### Step 2: Check Network Logs

Run the app with verbose logging:
```cmd
flutter run -v
```

Look for:
- HTTP request being made
- Response status code
- Response body
- Any Dio errors

### Step 3: Test API Directly

Before using the app, test the API endpoint directly:

**Using Postman or curl:**
1. Login first to get token
2. Use token in registration request
3. Verify data format matches API expectations

### Step 4: Check Backend Status

Verify backend is running:
```bash
curl https://yamenmod91.pythonanywhere.com/api/health
```

If no response, backend might be down.

## Expected API Request Format

```json
{
  "full_name": "John Doe",
  "phone": "01234567890",
  "email": "john@example.com",
  "gender": "male",
  "age": 30,
  "weight": 75.5,
  "height": 1.75,
  "bmi": 24.65,
  "bmi_category": "Normal",
  "bmr": 1750.5,
  "daily_calories": 2712.5,
  "branch_id": 1
}
```

## Expected API Response Format

### Success:
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "customer": {
      "id": 123,
      "full_name": "John Doe",
      "qr_code": "GYM-123",
      ...
    }
  }
}
```

### Error:
```json
{
  "success": false,
  "message": "Validation error",
  "error": "Phone number already exists"
}
```

## Quick Test

Run this test to verify registration flow:

```dart
// Add to reception_provider.dart for testing
Future<void> testRegistration() async {
  try {
    print('Testing registration...');
    
    final testCustomer = CustomerModel(
      fullName: 'Test Customer',
      gender: 'male',
      age: 25,
      weight: 75.0,
      height: 1.75,
      bmi: 24.5,
      bmiCategory: 'Normal',
      bmr: 1700.0,
      dailyCalories: 2500.0,
      branchId: branchId,
      phone: '01234567890',
      email: 'test@test.com',
    );
    
    print('Test Customer: ${testCustomer.toJson()}');
    
    final result = await registerCustomer(testCustomer);
    
    print('Test Result: $result');
  } catch (e) {
    print('Test Error: $e');
  }
}
```

## Solutions Applied

### 1. ✅ Enhanced Error Messages
Now shows:
- Network errors with specific details
- Validation errors from server
- Connection timeout messages
- Server response errors

### 2. ✅ Height Conversion Fix
Converts height from cm to meters before sending to API

### 3. ✅ Dialog Overflow Fix
Fixed pixel overflow in Gender/Age row

### 4. ✅ QR Code Generation
Generates QR code automatically from customer ID

## If Registration Still Fails

### Check These Files:

1. **API Configuration**
   - File: `lib/core/api/api_service.dart`
   - Verify base URL
   - Check token handling

2. **Customer Model**
   - File: `lib/shared/models/customer_model.dart`
   - Verify toJson() method
   - Check field names match API

3. **Reception Provider**
   - File: `lib/features/reception/providers/reception_provider.dart`
   - Check registerCustomer method
   - Verify error handling

4. **Auth Provider**
   - File: `lib/core/auth/auth_provider.dart`
   - Verify token is stored correctly
   - Check token is included in requests

## Getting Help

If issue persists:

1. **Collect Logs:**
   - Run: `flutter run -v > logs.txt 2>&1`
   - Attempt registration
   - Save the logs.txt file

2. **Check API Response:**
   - Look for actual error message from server
   - Note the HTTP status code

3. **Test Backend:**
   - Verify backend is accessible
   - Test API endpoints directly
   - Check if other endpoints work

## Current Status

- ✅ UI overflow issues fixed
- ✅ Error handling improved
- ✅ Height conversion fixed
- ✅ QR code generation implemented
- ⏳ Need to test actual registration with backend
- ⏳ Need to verify API connectivity

## Next Steps

1. **Run app with debug logging enabled**
2. **Attempt registration and capture logs**
3. **Verify backend connectivity**
4. **Test API endpoints directly**
5. **Check token validity**
6. **Verify data format matches API expectations**
