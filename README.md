# Gym Management Frontend

A production-grade Flutter mobile application for gym management with role-based access control and comprehensive operational features.

> 🆕 **NEW!** [📘 Flutter App Updated for Production Dataset](FLUTTER_APP_UPDATED.md) - Complete guide with test credentials and expected data

## 🚀 Quick Start

- **Testing Guide:** [QUICK_START_TEST_GUIDE.md](QUICK_START_TEST_GUIDE.md)
- **Test Credentials:** [TEST_CREDENTIALS.md](TEST_CREDENTIALS.md) - 14 test accounts
- **Expected Data:** [EXPECTED_DATA_GUIDE.md](EXPECTED_DATA_GUIDE.md) - What should appear on screens
- **Documentation Index:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) - All 29+ guides

## 🎯 Overview

This Flutter application provides a complete frontend solution for gym management operations, connecting to an existing Flask backend API. The app supports four distinct user roles with tailored interfaces:

- **Owner** - Strategic oversight with multi-branch analytics
- **Branch Manager** - Single-branch operations and performance tracking
- **Reception** - Fast-paced customer registration and subscription management
- **Accountant** - Financial reporting and expense tracking

## 🏗️ Architecture

### Clean Architecture Pattern

```
lib/
├── core/                          # Core infrastructure
│   ├── api/                       # API client and endpoints
│   ├── auth/                      # Authentication
│   ├── theme/                     # Theming
│   ├── utils/                     # Utilities
│   └── constants/                 # App constants
├── features/                      # Feature modules (by role)
│   ├── auth/                      # Login
│   ├── owner/                     # Owner dashboard
│   ├── branch_manager/            # Branch manager dashboard
│   ├── reception/                 # Reception operations
│   └── accountant/                # Accountant dashboard
├── shared/                        # Shared resources
│   ├── models/                    # Data models
│   └── widgets/                   # Reusable UI components
├── routes/                        # Navigation
└── main.dart                      # App entry point
```

## 🚀 Features

### Owner Dashboard
- Smart Alerts & Notifications
- Multi-branch Revenue Analytics
- Branch Performance Comparison
- Employee Performance Tracking
- Financial Overview & Decision Support
- Organization-wide Complaints Management

### Branch Manager Dashboard
- Branch Performance Metrics
- Staff Attendance Tracking
- Revenue by Service Analysis
- Daily Operations Summary
- Branch-level Complaint Management

### Reception (Front Desk)
- **Quick Customer Registration** with auto health metrics (BMI, BMR, calories)
- **Subscription Management**: Activate, Renew, Freeze, Stop
- **Payment Recording** with multiple methods
- **Daily Closing** for cash reconciliation
- **Complaint Submission**

### Accountant Dashboard
- Daily Sales Tracking
- Expense Management
- Cash Reconciliation
- Branch Financial Comparison
- Weekly & Monthly Reports
- Advanced Filtering

## 🛠️ Technology Stack

- **Flutter** 3.10.7+ with **Dart** 3.10.7+
- **Material 3** Design System
- **Provider** - State Management
- **Dio** - HTTP Client
- **Flutter Secure Storage** - JWT Storage
- **Go Router** - Navigation
- **FL Chart** - Data Visualization
- **JWT Decoder** - Token Parsing
- **Intl** - Date Formatting

## 📡 Backend Integration

**Base URL:** `https://yamenmod91.pythonanywhere.com`

**Authentication:** JWT Bearer Token

**Key Features:**
- Auto JWT injection in all requests
- 401 → Auto logout
- 403 → Permission error
- 500 → Retry mechanism

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete API reference.

## 📱 Installation

```bash
# Install dependencies
flutter pub get

# Run app
flutter run

# Build release APK
flutter build apk --release

# Build iOS
flutter build ios --release
```

## 🔐 Security

- Secure JWT storage (platform-specific encryption)
- Token expiry validation
- Role-based route guards
- Input validation on all forms
- HTTPS-only communication

## 🎨 Design System

**Color Scheme by Role:**
- Owner: Purple (#9C27B0)
- Branch Manager: Blue (#2196F3)
- Reception: Green (#4CAF50)
- Accountant: Orange (#FF9800)

## 📊 Business Logic

**Health Calculations (Auto-computed):**
- **BMI:** `weight (kg) / height (m)²`
- **BMR:** Mifflin-St Jeor Equation
- **Daily Calories:** BMR × Activity Multiplier

**Subscription Rules:**
- Payment required before activation
- Freeze pauses expiration counter
- Stop = immediate deactivation
- Renewal extends from current end date

**Fingerprint Handling:**
- Text-based hash (NO device biometrics)
- Optional customer identifier
- Manual or backend-generated

## 🧪 Testing

**Production-Quality Test Dataset Available:**

- **14 Test Users** across all roles (Owner, 3 Managers, 6 Reception, 4 Accountants)
- **150 Customers** distributed across 3 branches
- **472 Transactions** totaling 164,521 EGP
- **123 Subscriptions** with realistic statuses

See **[TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)** for complete test account details and scenarios.

**Quick Test Login:**
```
Owner: owner / owner123
Manager: manager_dragon / manager123
Reception: reception_dragon_1 / reception123
Accountant: accountant_central_1 / accountant123
```

**Testing Guide:** See [QUICK_START_TEST_GUIDE.md](QUICK_START_TEST_GUIDE.md) for step-by-step testing instructions.

## 📝 Code Structure

```dart
// Example: Feature Provider Pattern
class ReceptionProvider extends ChangeNotifier {
  final ApiService _apiService;
  
  Future<Map<String, dynamic>> registerCustomer(...) async {
    // API call
    // Update state
    notifyListeners();
  }
}

// Example: Screen with Provider
class ReceptionHomeScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final provider = context.watch<ReceptionProvider>();
    // UI implementation
  }
}
```

## 🚦 Development Workflow

1. Feature in separate folder under `features/`
2. Provider for state management
3. API service calls with error handling
4. Shared widgets for reusability
5. Run `flutter analyze` before commit

## 📈 Future Enhancements

- [ ] Advanced charts for Owner dashboard
- [ ] Push notifications
- [ ] Offline mode with sync
- [ ] Multi-language support
- [ ] Dark mode
- [ ] PDF/Excel export
- [ ] QR code generation

## 🐛 Troubleshooting

**"Target of URI doesn't exist":**
```bash
flutter clean && flutter pub get
```

**JWT expired:** App auto-logs out, re-login required

**Cannot connect:** Check internet, verify backend URL

## 📄 License

Private project for internal use.

---

**Built with ❤️ using Flutter**
