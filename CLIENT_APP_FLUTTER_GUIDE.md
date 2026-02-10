# 📱 CLIENT APP DEVELOPMENT GUIDE - Flutter Frontend

## 🎯 Overview

Your gym backend now supports a **separate client/customer mobile app** where gym members can:
- Login with their credentials (phone + password)
- View their profile and subscription details
- Access their QR code for gym entry
- View entry history
- Change their password

## 🔐 Authentication Flow

### 1. Customer Registration (Reception Staff)

When reception registers a new customer, the backend returns:

```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "qr_code": "GYM-151",
    "client_credentials": {
      "client_id": "GYM-151",
      "phone": "01234567890",
      "temporary_password": "AB12CD34",
      "note": "Give these credentials to the client for their mobile app login"
    }
  }
}
```

**Reception should:**
1. Print or write down the credentials
2. Give them to the client
3. Tell client to download the gym member app
4. Client logs in with phone + temporary password

---

### 2. Client Login Endpoint

**Endpoint:** `POST /api/client/auth/login`

**Request:**
```json
{
  "phone": "01234567890",
  "password": "AB12CD34"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "Bearer",
    "password_changed": false,
    "customer": {
      "id": 151,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-151",
      "branch_id": 1,
      "branch_name": "Dragon Club",
      "has_active_subscription": true
    }
  },
  "message": "Login successful"
}
```

**Important:** Check `password_changed` field:
- `false` → Force user to change password (first login)
- `true` → Normal login flow

---

## 📱 Flutter Implementation

### 1. Login Screen (lib/screens/client_login_screen.dart)

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ClientLoginScreen extends StatefulWidget {
  @override
  _ClientLoginScreenState createState() => _ClientLoginScreenState();
}

class _ClientLoginScreenState extends State<ClientLoginScreen> {
  final _phoneController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  Future<void> _login() async {
    if (_phoneController.text.isEmpty || _passwordController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Please enter phone and password')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      final response = await http.post(
        Uri.parse('https://yamenmod91.pythonanywhere.com/api/client/auth/login'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'phone': _phoneController.text.trim(),
          'password': _passwordController.text.trim(),
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success'] == true) {
        final token = data['data']['access_token'];
        final passwordChanged = data['data']['password_changed'];
        final customer = data['data']['customer'];

        // Save token to secure storage
        await _saveToken(token);
        await _saveCustomer(customer);

        if (!passwordChanged) {
          // Force password change on first login
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(
              builder: (context) => ChangePasswordScreen(isFirstLogin: true),
            ),
          );
        } else {
          // Go to home screen
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ClientHomeScreen()),
          );
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Login failed')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _saveToken(String token) async {
    // Use flutter_secure_storage
    final storage = FlutterSecureStorage();
    await storage.write(key: 'access_token', value: token);
  }

  Future<void> _saveCustomer(Map<String, dynamic> customer) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('customer_data', jsonEncode(customer));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Client Login')),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            TextField(
              controller: _phoneController,
              decoration: InputDecoration(
                labelText: 'Phone Number',
                prefixIcon: Icon(Icons.phone),
              ),
              keyboardType: TextInputType.phone,
            ),
            SizedBox(height: 16),
            TextField(
              controller: _passwordController,
              decoration: InputDecoration(
                labelText: 'Password',
                prefixIcon: Icon(Icons.lock),
              ),
              obscureText: true,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isLoading ? null : _login,
              child: _isLoading
                  ? CircularProgressIndicator()
                  : Text('Login'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

### 2. Change Password Screen

**Endpoint:** `POST /api/client/change-password`

**Request:**
```json
{
  "current_password": "AB12CD34",
  "new_password": "mynewpass123"
}
```

**Flutter Implementation:**

```dart
class ChangePasswordScreen extends StatefulWidget {
  final bool isFirstLogin;
  
  ChangePasswordScreen({this.isFirstLogin = false});
  
  @override
  _ChangePasswordScreenState createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends State<ChangePasswordScreen> {
  final _currentPasswordController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  Future<void> _changePassword() async {
    if (_newPasswordController.text != _confirmPasswordController.text) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Passwords do not match')),
      );
      return;
    }

    if (_newPasswordController.text.length < 6) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Password must be at least 6 characters')),
      );
      return;
    }

    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');

    try {
      final response = await http.post(
        Uri.parse('https://yamenmod91.pythonanywhere.com/api/client/change-password'),
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer $token',
        },
        body: jsonEncode({
          'current_password': _currentPasswordController.text,
          'new_password': _newPasswordController.text,
        }),
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Password changed successfully')),
        );

        if (widget.isFirstLogin) {
          // After first login password change, go to home
          Navigator.pushReplacement(
            context,
            MaterialPageRoute(builder: (context) => ClientHomeScreen()),
          );
        } else {
          Navigator.pop(context);
        }
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(data['message'] ?? 'Failed to change password')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.isFirstLogin ? 'Set New Password' : 'Change Password'),
        automaticallyImplyLeading: !widget.isFirstLogin,
      ),
      body: Padding(
        padding: EdgeInsets.all(16.0),
        child: Column(
          children: [
            if (widget.isFirstLogin)
              Text(
                'Please change your temporary password',
                style: TextStyle(fontSize: 16, color: Colors.orange),
              ),
            SizedBox(height: 16),
            TextField(
              controller: _currentPasswordController,
              decoration: InputDecoration(labelText: 'Current Password'),
              obscureText: true,
            ),
            TextField(
              controller: _newPasswordController,
              decoration: InputDecoration(labelText: 'New Password (min 6 chars)'),
              obscureText: true,
            ),
            TextField(
              controller: _confirmPasswordController,
              decoration: InputDecoration(labelText: 'Confirm New Password'),
              obscureText: true,
            ),
            SizedBox(height: 24),
            ElevatedButton(
              onPressed: _changePassword,
              child: Text('Change Password'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

### 3. Client Profile Screen

**Endpoint:** `GET /api/client/me`

**Response:**
```json
{
  "success": true,
  "data": {
    "id": 151,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-151",
    "branch_name": "Dragon Club",
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "active_subscription": {
      "id": 124,
      "service_name": "Monthly Gym",
      "start_date": "2026-02-10",
      "end_date": "2026-03-10",
      "status": "active"
    },
    "password_changed": true,
    "qr_image_url": "/api/client/qr-image"
  }
}
```

**Flutter Implementation:**

```dart
class ClientProfileScreen extends StatefulWidget {
  @override
  _ClientProfileScreenState createState() => _ClientProfileScreenState();
}

class _ClientProfileScreenState extends State<ClientProfileScreen> {
  Map<String, dynamic>? _profile;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');

    try {
      final response = await http.get(
        Uri.parse('https://yamenmod91.pythonanywhere.com/api/client/me'),
        headers: {'Authorization': 'Bearer $token'},
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success']) {
        setState(() {
          _profile = data['data'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading profile: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(
        appBar: AppBar(title: Text('Profile')),
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (_profile == null) {
      return Scaffold(
        appBar: AppBar(title: Text('Profile')),
        body: Center(child: Text('Failed to load profile')),
      );
    }

    final subscription = _profile!['active_subscription'];

    return Scaffold(
      appBar: AppBar(title: Text('My Profile')),
      body: SingleChildScrollView(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: ListTile(
                leading: Icon(Icons.person, size: 40),
                title: Text(_profile!['full_name']),
                subtitle: Text(_profile!['phone']),
              ),
            ),
            SizedBox(height: 16),
            Text('Subscription', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Card(
              child: subscription != null
                  ? ListTile(
                      title: Text(subscription['service_name']),
                      subtitle: Text(
                        'Valid until: ${subscription['end_date']}\nStatus: ${subscription['status']}',
                      ),
                      trailing: Icon(
                        Icons.check_circle,
                        color: Colors.green,
                      ),
                    )
                  : ListTile(
                      title: Text('No active subscription'),
                      subtitle: Text('Please contact reception'),
                      trailing: Icon(Icons.warning, color: Colors.orange),
                    ),
            ),
            SizedBox(height: 16),
            Text('Health Info', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
            Card(
              child: Column(
                children: [
                  ListTile(
                    title: Text('Weight'),
                    trailing: Text('${_profile!['weight']} kg'),
                  ),
                  ListTile(
                    title: Text('Height'),
                    trailing: Text('${_profile!['height']} cm'),
                  ),
                  ListTile(
                    title: Text('BMI'),
                    trailing: Text('${_profile!['bmi']} (${_profile!['bmi_category']})'),
                  ),
                ],
              ),
            ),
            SizedBox(height: 16),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => QRCodeScreen()),
                );
              },
              icon: Icon(Icons.qr_code),
              label: Text('View QR Code'),
            ),
            SizedBox(height: 8),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => ChangePasswordScreen()),
                );
              },
              icon: Icon(Icons.lock),
              label: Text('Change Password'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

### 4. QR Code Screen

**Endpoint:** `GET /api/client/qr`

```dart
class QRCodeScreen extends StatefulWidget {
  @override
  _QRCodeScreenState createState() => _QRCodeScreenState();
}

class _QRCodeScreenState extends State<QRCodeScreen> {
  String? _qrData;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadQRCode();
  }

  Future<void> _loadQRCode() async {
    final storage = FlutterSecureStorage();
    final token = await storage.read(key: 'access_token');

    try {
      final response = await http.get(
        Uri.parse('https://yamenmod91.pythonanywhere.com/api/client/qr'),
        headers: {'Authorization': 'Bearer $token'},
      );

      final data = jsonDecode(response.body);

      if (response.statusCode == 200 && data['success']) {
        setState(() {
          _qrData = data['data']['qr_token'];
          _isLoading = false;
        });
      }
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading QR code: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Gym Access QR Code')),
      body: Center(
        child: _isLoading
            ? CircularProgressIndicator()
            : _qrData != null
                ? Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      QrImageView(
                        data: _qrData!,
                        version: QrVersions.auto,
                        size: 250.0,
                      ),
                      SizedBox(height: 16),
                      Text('Show this QR code at gym entry'),
                      SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _loadQRCode,
                        icon: Icon(Icons.refresh),
                        label: Text('Refresh'),
                      ),
                    ],
                  )
                : Text('Failed to load QR code'),
      ),
    );
  }
}
```

---

## 📊 Available Endpoints for Client App

### Authentication
- `POST /api/client/auth/login` - Login with phone + password
- `POST /api/client/change-password` - Change password

### Profile & Info
- `GET /api/client/me` - Get profile with subscription
- `GET /api/client/subscription` - Get active subscription details
- `GET /api/client/subscriptions/history` - Get past subscriptions

### Gym Access
- `GET /api/client/qr` - Get time-limited QR token for entry
- `POST /api/client/qr/refresh` - Refresh QR code

### Entry History
- `GET /api/client/entry-history` - View gym entry logs

---

## 🔒 Security Notes

1. **Always use HTTPS** in production
2. **Store token securely** using `flutter_secure_storage`
3. **Check token expiry** and refresh when needed
4. **Validate all user inputs** before sending to backend
5. **Handle errors gracefully**

---

## 📦 Required Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  flutter_secure_storage: ^9.0.0
  shared_preferences: ^2.2.2
  qr_flutter: ^4.1.0
  provider: ^6.1.1  # For state management
```

---

## 🎨 App Structure

```
lib/
├── main.dart
├── screens/
│   ├── client_login_screen.dart
│   ├── client_home_screen.dart
│   ├── client_profile_screen.dart
│   ├── change_password_screen.dart
│   ├── qr_code_screen.dart
│   └── entry_history_screen.dart
├── services/
│   ├── auth_service.dart
│   └── api_service.dart
├── models/
│   ├── customer.dart
│   └── subscription.dart
└── utils/
    ├── constants.dart
    └── secure_storage.dart
```

---

## ✅ Testing Checklist

- [ ] Customer registration shows credentials to reception
- [ ] Client can login with phone + temporary password
- [ ] First login forces password change
- [ ] Client can view profile and subscription
- [ ] QR code displays correctly
- [ ] Password change works
- [ ] Token stays valid for app usage
- [ ] Logout clears token

---

## 🚀 Deployment

1. **Test with existing customers:**
   - Run migration script on server
   - Get temporary passwords for test customers
   - Test login flow

2. **Build production app:**
   ```bash
   flutter build apk --release
   # or
   flutter build ios --release
   ```

3. **Update API URL** in production:
   - Replace `https://yamenmod91.pythonanywhere.com` with your domain
   - Use environment variables for different environments

---

**Your client app is now ready to build!** 🎉
