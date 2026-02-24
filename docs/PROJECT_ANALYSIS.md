# 🏋️ Gym Management System — Complete Project Analysis
*Last analyzed: February 24, 2026*

---

## 📁 Repository Layout

```
gym_frontend/                          ← Flutter monorepo (staff + client apps)
├── lib/
│   ├── main.dart                      ← Staff/Admin app entry point
│   ├── client_main.dart               ← Client (member) app entry point
│   ├── core/                          ← Shared API, auth, constants, theme, utils
│   │   ├── api/
│   │   │   ├── api_service.dart       ← Dio HTTP client for staff app
│   │   │   └── api_endpoints.dart     ← All staff API URL constants
│   │   ├── auth/
│   │   │   ├── auth_provider.dart     ← Staff auth state (ChangeNotifier)
│   │   │   └── auth_service.dart      ← JWT login/logout for staff
│   │   ├── constants/app_constants.dart
│   │   └── theme/                     ← Role-based theming
│   ├── features/                      ← Staff app screens by role
│   │   ├── auth/screens/              ← Staff login
│   │   ├── reception/
│   │   │   ├── screens/               ← Home, customers list, customer detail,
│   │   │   │                            QR scanner, subscription ops, operations
│   │   │   ├── providers/reception_provider.dart
│   │   │   └── widgets/
│   │   ├── owner/screens/             ← Dashboard, branch detail, alerts,
│   │   │                                leaderboard, operational monitor
│   │   ├── branch_manager/screens/    ← Manager dashboard + settings
│   │   ├── accountant/screens/        ← Accountant dashboard, ledger, settings
│   │   └── manager/screens/           ← Manager settings
│   ├── shared/
│   │   ├── models/                    ← Shared data models (customer, service,
│   │   │                                subscription, branch, payment, user…)
│   │   └── widgets/                   ← Reusable UI (stat_card, date_range_picker…)
│   ├── routes/app_router.dart         ← GoRouter for staff app
│   └── client/                        ← Client (member) app
│       ├── core/
│       │   ├── api/client_api_service.dart   ← Dio client for member app
│       │   ├── auth/
│       │   │   ├── client_auth_provider.dart
│       │   │   └── client_auth_service.dart
│       │   └── theme/client_theme.dart       ← Dark theme
│       ├── models/
│       │   ├── client_model.dart
│       │   ├── subscription_model.dart       ← Parses subscription JSON
│       │   └── entry_history_model.dart
│       ├── screens/
│       │   ├── welcome_screen.dart           ← Login / first screen
│       │   ├── activation_screen.dart        ← Code-based 2FA screen
│       │   ├── client_main_screen.dart       ← Bottom-tab shell
│       │   ├── client_overview_tab.dart      ← Dashboard tab
│       │   ├── home_screen.dart              ← Main tab (loads subscription)
│       │   ├── qr_screen.dart                ← Member QR code display
│       │   ├── subscription_screen.dart      ← Subscription detail
│       │   ├── entry_history_screen.dart
│       │   ├── change_password_screen.dart
│       │   └── settings_screen.dart
│       └── routes/client_router.dart         ← GoRouter for client app

Gym_backend/
└── backend/
    ├── app/
    │   ├── __init__.py               ← Flask app factory
    │   ├── config.py
    │   ├── extensions.py
    │   ├── models/                   ← SQLAlchemy ORM models
    │   │   ├── customer.py           ← Customer + auth fields (phone, QR, temp_password…)
    │   │   ├── subscription.py       ← Subscription + display logic (coins/time/sessions)
    │   │   ├── service.py            ← Service/Package (gym, swimming, karate, bundle)
    │   │   ├── user.py               ← Staff users with roles
    │   │   ├── branch.py
    │   │   ├── entry_log.py
    │   │   ├── freeze_history.py
    │   │   ├── transaction.py
    │   │   ├── daily_closing.py
    │   │   ├── activation_code.py
    │   │   ├── expense.py
    │   │   ├── fingerprint.py
    │   │   └── complaint.py
    │   ├── routes/                   ← Flask blueprints
    │   │   ├── client_auth_routes.py ← POST /api/client/auth/login
    │   │   ├── client_routes.py      ← GET /api/client/me, /api/client/subscription…
    │   │   ├── qr_routes.py          ← POST /api/qr/scan, /api/qr/deduct-coins
    │   │   ├── subscriptions_routes.py ← Full CRUD + freeze/stop/activate/renew
    │   │   ├── customers_routes.py
    │   │   ├── auth_routes.py        ← Staff JWT login
    │   │   ├── branches_routes.py
    │   │   ├── services_routes.py
    │   │   ├── payments_routes.py
    │   │   ├── reports_routes.py
    │   │   ├── dashboards_routes.py
    │   │   ├── attendance_routes.py
    │   │   ├── alerts_routes.py
    │   │   ├── finance_routes.py
    │   │   ├── expenses_routes.py
    │   │   ├── transactions_routes.py
    │   │   ├── entry_logs_routes.py
    │   │   ├── fingerprints_routes.py
    │   │   ├── complaints_routes.py
    │   │   ├── daily_closing_routes.py
    │   │   ├── validation_routes.py
    │   │   ├── debug_routes.py
    │   │   └── test_routes.py
    │   ├── services/
    │   │   ├── subscription_service.py  ← Create/renew/freeze subscriptions
    │   │   ├── auth_service.py
    │   │   ├── dashboard_service.py
    │   │   ├── notification_service.py
    │   │   └── qr_service.py
    │   └── utils/
    ├── run.py
    ├── seed.py
    └── requirements.txt
```

---

## 🏗️ Architecture Overview

### Two Flutter Entry Points
| Entry | File | Target Users |
|---|---|---|
| Staff/Admin App | `lib/main.dart` | Owner, Branch Manager, Reception, Accountant |
| Client App | `lib/client_main.dart` | Gym members / customers |

Both apps share the same Flutter project (`pubspec.yaml`) but use entirely separate providers, routers, API services, and screens.

### Backend
- **Framework**: Flask (Python) with SQLAlchemy ORM
- **Auth**: JWT (Flask-JWT-Extended) — separate tokens for staff (`/api/auth/login`) and clients (`/api/client/auth/login`)
- **Deployment**: PythonAnywhere at `https://yamenmod91.pythonanywhere.com`
- **Database**: SQLite (development) / configured via `.env`

---

## 🔐 Authentication Flow

### Staff App
1. POST `/api/auth/login` → returns `access_token`
2. Token stored in `FlutterSecureStorage` with key `jwt_token`
3. `ApiService` Dio interceptor attaches `Authorization: Bearer <token>` automatically

### Client App
1. POST `/api/client/auth/login` → returns `access_token` + `customer` object + `password_changed`
2. Token stored under `client_access_token`
3. `ClientAuthProvider` reads `password_changed` — if `false`, router forces `/change-password` screen first

---

## 📦 Subscription System (Critical)

### Subscription Types (Backend `subscription_type` field)
| Type | Display | Tracks |
|---|---|---|
| `coins` | `remaining_coins` | Deducted per visit/service |
| `time_based` | days remaining | `end_date - today` |
| `sessions` | `remaining_sessions` | Group classes, fixed count |
| `training` | `remaining_sessions` | Personal training, fixed count |

### Backend → Flutter Data Mapping
The `Subscription.to_dict()` method sends:
```json
{
  "subscription_type": "coins",
  "remaining_coins": 45,
  "remaining_sessions": null,
  "remaining_days": null,
  "display_metric": "coins",
  "display_value": 45,
  "display_label": "45 Coins",
  "start_date": "2026-01-01",
  "end_date": "2026-12-31",
  "status": "active",
  "freeze_history": [],
  "allowed_services": []
}
```

The Flutter `SubscriptionModel.fromJson()` in `lib/client/models/subscription_model.dart`:
- Has fallback logic to infer `displayMetric` from `subscription_type` name
- Handles `expiry_date` or `end_date` for the end date field
- Calculates `daysRemaining` from `expiryDate`

### QR Check-in Flow
1. Reception staff opens QR scanner → `QRScannerScreen`
2. Camera scans QR code (format: `GYM-{id}`, `CUST-{id}`, `customer_id:{id}`, or bare ID)
3. Staff app POSTs to `/api/qr/scan` with `{ qr_code, branch_id, action, coins_to_deduct }`
4. Backend finds customer → validates active subscription → deducts coin/logs entry
5. Response returns `remaining_coins`, `entry_id`, `customer_name`

### Client QR Display
- `QrScreen` reads `client.qrCode` from `ClientAuthProvider.currentClient`
- Displays QR as image using `qr_flutter` package
- Auto-refreshes countdown (1 hour default)
- Can refresh via `/api/client/qr-refresh` endpoint

---

## 👥 User Roles (Staff App)

| Role Enum | Access |
|---|---|
| `OWNER` | All branches, all data, financial reports |
| `BRANCH_MANAGER` | Own branch, staff management |
| `FRONT_DESK` (Reception) | Customer check-ins, subscriptions, QR scanning |
| `CENTRAL_ACCOUNTANT` | All branch financials |
| `ACCOUNTANT` | Own branch financials |

Role-based routing in `app_router.dart` directs each user to the appropriate feature set.

---

## 🌐 API Base URLs

| App | Base URL |
|---|---|
| Staff App | `https://yamenmod91.pythonanywhere.com` (set in `api_endpoints.dart`) |
| Client App | `https://yamenmod91.pythonanywhere.com/api` (set in `client_api_service.dart`) |

---

## 📱 Key Flutter Packages

| Package | Purpose |
|---|---|
| `provider ^6.1.1` | State management |
| `dio ^5.4.0` | HTTP client |
| `flutter_secure_storage ^9.0.0` | JWT token storage |
| `go_router ^13.0.0` | Declarative routing |
| `qr_flutter ^4.1.0` | QR code generation (client display) |
| `mobile_scanner ^3.5.7` | QR code scanning (reception) |
| `fl_chart ^0.66.0` | Charts/graphs |
| `intl ^0.19.0` | Date formatting |
| `jwt_decoder ^2.0.1` | JWT token inspection |

---

## 🗄️ Key Backend Models

### Customer
- `phone` — unique login identifier
- `qr_code` — unique gym access code (format `GYM-{id}`)
- `password_hash` — bcrypt hashed password
- `temp_password` — plain-text first-time password set by reception
- `password_changed` — boolean; forces client to change password on first login
- `branch_id` — home branch
- Health fields: `height`, `weight`, `bmi`, `bmr`, `ideal_weight`, `daily_calories`

### Subscription
- `subscription_type` — `coins`, `time_based`, `sessions`, `training`
- `remaining_coins` / `remaining_sessions` — usage counters
- `status` — `active`, `frozen`, `stopped`, `expired`
- `freeze_count` / `total_frozen_days` — freeze tracking
- `end_date` — expiry (for time-based)

### Service
- `service_type` — `gym`, `swimming_education`, `swimming_recreation`, `karate`, `bundle`
- `class_limit` — non-null for session/training types
- `freeze_count_limit` / `freeze_max_days` — freeze rules per service

---

## ⚠️ Known Integration Points & Notes

1. **QR Scan endpoint** (`/api/qr/scan`) currently only handles coin-based subscriptions — time-based subscriptions need separate logic
2. **Client API** uses `/api/client/` prefix while staff uses `/api/` prefix
3. **`password_changed` flag** — critical for first-login flow; if false, client is forced to `/change-password`
4. **Subscription `end_date` vs `expiry_date`** — backend sends `end_date`, Flutter model handles both via `json['expiry_date'] ?? json['end_date']`
5. **Branch filtering** — Owner/Central Accountant see all branches; other roles are scoped to `user.branch_id`
6. **CORS** — Backend must allow requests from Android/iOS clients; previously a known issue (see `docs/backend_fixes/`)

---

## 📂 Documentation Organization

All documentation is now organized into:

```
docs/
├── PROJECT_ANALYSIS.md         ← This file (full project overview)
├── backend_fixes/              ← All backend-related docs, API specs, deployment guides
│   ├── BACKEND_*.md            ← Backend fix prompts and requirements
│   ├── CLAUDE_BACKEND_*.md     ← AI prompts for backend fixes
│   ├── COMPLETE_BACKEND_*.md   ← Complete API specifications
│   ├── CORS_*.md               ← CORS fixes
│   ├── DEPLOYMENT_*.md         ← PythonAnywhere deployment
│   ├── API_ENDPOINTS.md        ← API endpoint reference
│   └── ...
└── frontend_fixes/             ← All Flutter/frontend-related docs
    ├── CLIENT_APP_*.md         ← Client app implementation docs
    ├── FLUTTER_*.md            ← Flutter fix summaries
    ├── QR_CODE_*.md            ← QR code implementation
    ├── REGISTRATION_*.md       ← Registration flow fixes
    ├── SUBSCRIPTION_*.md       ← Subscription UI fixes
    ├── STAFF_APP_*.md          ← Staff app UI/UX fixes
    └── ...
```

