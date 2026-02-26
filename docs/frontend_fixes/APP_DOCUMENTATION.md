# 📚 FLUTTER GYM APP DOCUMENTATION

**Date:** February 16, 2026  
**Project:** Gym Management System (Staff & Client Apps)

---

## 📱 APPS OVERVIEW

### Staff App (Receptionist/Manager/Accountant/Owner)
**Package:** `com.example.gym_frontend.staff`
- Customer registration
- Subscription activation
- QR code scanning for check-ins
- Customer management
- Dashboard analytics

### Client App (Gym Members)
**Package:** `com.example.gym_frontend.client`
- Login with phone + temporary password
- View QR code for gym entry
- View subscription status (coins/time remaining)
- View workout history
- Update profile

---

## 🔑 KEY FEATURES

### Staff App Features
1. **Dashboard** - Active subscriptions, recent customers, revenue
2. **Customers** - List, search, register, view details
3. **QR Scanner** - Scan member QR codes for check-in
4. **Subscriptions** - Activate different types (coins/monthly/personal training)
5. **Settings** - Profile, logout

### Client App Features
1. **Login** - Phone number + temporary password
2. **Dashboard** - Subscription status, remaining coins/time
3. **QR Code** - Personal QR code for gym entry
4. **Plan** - Subscription details and expiration
5. **Profile** - Personal information and health metrics
6. **Settings** - Change password, logout

---

## 📊 SUBSCRIPTION TYPES

### 1. Coins Subscription
- Buy bundle of coins (e.g., 20, 50, 100 coins)
- Each gym entry = -1 coin
- No expiration date
- Shows: "X coins remaining"

### 2. Time-Based Subscription
- Monthly (1, 2, 3, 6, 9, 12 months)
- Unlimited entries during period
- Shows: "X days remaining"

### 3. Personal Training
- Private training sessions
- Shows session count and schedule

---

## 🔐 AUTHENTICATION

### Staff Authentication
- Login with email + password
- Role-based access (Owner/Manager/Accountant/Receptionist)
- JWT token stored securely
- Branch-specific access (except Owner)

### Client Authentication
- First-time: Phone + temporary password (e.g., "RX04AF")
- Forced password change on first login
- JWT token stored securely
- Branch-specific membership

---

## 📡 API STRUCTURE

### Staff Endpoints
- `/api/staff/auth/login` - Staff login
- `/api/customers` - Customer management
- `/api/customers/register` - Register new customer
- `/api/subscriptions/activate` - Activate subscription
- `/api/checkins` - Create check-in

### Client Endpoints
- `/api/client/auth/login` - Client login
- `/api/client/auth/change-password` - Change password
- `/api/client/profile` - Get/update profile
- `/api/client/subscription` - Get subscription status
- `/api/client/checkins` - Get check-in history

---

## 🏗️ PROJECT STRUCTURE

```
lib/
├── main.dart                          # App entry point
├── core/
│   ├── constants/
│   │   ├── api_constants.dart        # API URLs
│   │   └── colors.dart               # App colors
│   ├── models/
│   │   ├── user_model.dart          # User data model
│   │   ├── customer_model.dart      # Customer model
│   │   └── subscription_model.dart  # Subscription model
│   └── services/
│       ├── api_service.dart         # HTTP client
│       └── auth_service.dart        # Authentication
├── features/
│   ├── auth/                        # Login screens
│   ├── dashboard/                   # Dashboard screens
│   ├── reception/                   # Customer management
│   ├── qr_scanner/                  # QR code scanning
│   └── settings/                    # Settings screens
└── shared/
    └── widgets/                     # Reusable widgets
```

---

## 🎨 UI/UX GUIDELINES

### Colors
- Primary: Blue (#2196F3)
- Secondary: Teal (#009688)
- Error: Red (#F44336)
- Success: Green (#4CAF50)

### Components
- Stat Cards: Dashboard metrics
- Customer Cards: Customer list items
- QR Scanner: Full-screen camera view
- Bottom Navigation: 5 tabs (Dashboard, Customers, Scan, Reports, Settings)

---

## 🔧 CURRENT ISSUES (Being Fixed)

### Backend Issues
1. ❌ Customer registration blocked
2. ❌ Check-in system not working
3. ❌ QR codes not generated
4. ❌ Coins not decreasing
5. ❌ Temp password not showing

### Flutter Issues (All Fixed)
1. ✅ Branch filtering working
2. ✅ QR scanner implemented
3. ✅ Subscription display correct
4. ✅ Navigation working
5. ✅ All UI issues resolved

---

## 🧪 TESTING CREDENTIALS

### Staff Accounts
| Role | Email | Password | Branch |
|------|-------|----------|--------|
| Owner | owner@example.com | password123 | All |
| Manager | manager.branch1@example.com | password123 | Branch 1 |
| Receptionist | receptionist.branch1@example.com | password123 | Branch 1 |
| Accountant | accountant.branch1@example.com | password123 | Branch 1 |

### Client Accounts (After Registration)
| Phone | Temp Password | Name |
|-------|---------------|------|
| 01077827638 | RX04AF | Mohamed Salem |
| 01022981052 | SI19IC | Layla Rashad |

---

## 🚀 RUNNING THE APPS

### Staff App
```bash
flutter run -d <device> --flavor staff -t lib/main.dart
```

### Client App
```bash
flutter run -d <device> --flavor client -t lib/main.dart
```

### Both Apps (Separate Terminals)
Terminal 1: `flutter run --flavor staff`
Terminal 2: `flutter run --flavor client`

---

## 📦 DEPENDENCIES

### Core Dependencies
- `flutter_riverpod` - State management
- `dio` - HTTP client
- `shared_preferences` - Local storage
- `flutter_secure_storage` - Secure token storage
- `mobile_scanner` - QR code scanning
- `qr_flutter` - QR code generation

### UI Dependencies
- `google_fonts` - Typography
- `shimmer` - Loading effects
- `cached_network_image` - Image caching

---

## 🔄 DATA FLOW

### Customer Registration Flow
1. Receptionist fills registration form
2. App sends data to `/api/customers/register`
3. Backend validates branch access
4. Backend generates temp password & QR code
5. Backend returns customer data
6. App displays success + temp password

### Check-in Flow
1. Receptionist scans customer QR code
2. App extracts customer_id from QR
3. App sends to `/api/checkins`
4. Backend validates subscription
5. Backend decrements coins (if coin subscription)
6. Backend saves check-in record
7. App displays success message

### Client Login Flow
1. Client enters phone + temp password
2. App sends to `/api/client/auth/login`
3. Backend validates credentials
4. Backend checks `password_changed` flag
5. If false: Force password change screen
6. If true: Navigate to dashboard
7. Token stored securely

---

## ✅ VERIFICATION CHECKLIST

### Staff App
- [ ] Login with different roles
- [ ] Register new customer
- [ ] View customer list (filtered by branch)
- [ ] Scan QR code
- [ ] Activate subscription
- [ ] View dashboard metrics

### Client App
- [ ] Login with temp password
- [ ] Force password change on first login
- [ ] View QR code
- [ ] See correct subscription type (coins/time)
- [ ] View remaining coins/days
- [ ] Check-in history

---

## 🐛 KNOWN LIMITATIONS

1. **Backend dependent** - All features require backend API
2. **Network required** - No offline mode
3. **QR codes** - Must be generated on backend
4. **Real-time updates** - Requires manual refresh

---

## 📞 SUPPORT

**For Backend Issues:** See `backend_fixes/ALL_BACKEND_FIXES_REQUIRED.md`

**For Flutter Issues:** All resolved (as of Feb 16, 2026)

---

**END OF DOCUMENTATION**

