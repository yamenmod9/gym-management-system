# 🏋️ Gym Management System - Backend API

A production-ready Flask REST API backend for managing gym/sports club operations with multi-branch support, role-based access control, financial tracking, and comprehensive subscription management.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Authentication & Authorization](#authentication--authorization)
- [User Roles](#user-roles)
- [Database Models](#database-models)
- [Testing](#testing)
- [Deployment](#deployment)

## ✨ Features

### Core Functionality
- ✅ **Multi-Branch Management** - Support for multiple gym locations
- ✅ **Role-Based Access Control (RBAC)** - 6 distinct user roles with granular permissions
- ✅ **Customer Management** - Complete customer profiles with health metrics (BMI, ideal weight, calories)
- ✅ **Subscription System** - Flexible subscriptions with freeze, renewal, and stop capabilities
- ✅ **Financial Tracking** - Complete transaction history with multiple payment methods
- ✅ **Expense Management** - Approval workflow for business expenses
- ✅ **Complaints System** - Track and resolve customer complaints
- ✅ **Fingerprint Access Control** - Simulated biometric entry system
- ✅ **Smart Dashboards** - Role-specific dashboards with analytics
- ✅ **Comprehensive Reporting** - Revenue reports, branch comparison, staff performance

### 📱 Client Features (NEW)
- ✅ **OTP Authentication** - 6-digit activation codes via SMS/Email
- ✅ **Client Mobile App API** - Separate JWT tokens for clients
- ✅ **QR Code Entry** - Time-limited QR codes (5-10 minutes)
- ✅ **Barcode Validation** - Static barcode scanning (GYM-XXX)
- ✅ **Entry Logging** - Complete audit trail of gym entries
- ✅ **Visit/Class Tracking** - Automatic coin deduction system
- ✅ **Entry Validation** - Staff endpoints for gate scanners
- ✅ **Client Statistics** - Visit history, streaks, and analytics
- 📖 **[Complete Client API Docs →](CLIENT_FEATURES_API.md)**

### Services Supported
- 🏋️ **Gym** - General fitness memberships
- 🏊 **Swimming** - Education and recreation programs
- 🥋 **Karate** - Martial arts training
- 📦 **Bundles** - Combined service packages

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| **Python 3.11+** | Backend runtime |
| **Flask** | Web framework |
| **Flask-RESTful** | REST API development |
| **Flask-JWT-Extended** | JWT authentication |
| **SQLAlchemy** | ORM |
| **Flask-Migrate** | Database migrations |
| **Marshmallow** | Serialization/validation |
| **Passlib** | Password hashing |
| **SQLite** | Development database |
| **PostgreSQL** | Production database (configurable) |

## 📁 Project Structure

```
backend/
│
├── app/
│   ├── __init__.py              # Application factory
│   ├── config.py                # Configuration classes
│   ├── extensions.py            # Flask extensions initialization
│   │
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User & authentication
│   │   ├── branch.py            # Branch management
│   │   ├── customer.py          # Customer profiles
│   │   ├── service.py           # Service definitions
│   │   ├── subscription.py      # Subscription logic
│   │   ├── transaction.py       # Financial transactions
│   │   ├── expense.py           # Business expenses
│   │   ├── complaint.py         # Customer complaints
│   │   ├── fingerprint.py       # Access control
│   │   ├── freeze_history.py    # Subscription freezes
│   │   ├── daily_closing.py     # Daily reconciliation
│   │   ├── activation_code.py   # 🆕 Client OTP codes
│   │   └── entry_log.py         # 🆕 Gym entry tracking
│   │
│   ├── routes/                  # API endpoints
│   │   ├── __init__.py
│   │   ├── auth_routes.py       # Authentication
│   │   ├── users_routes.py      # User management
│   │   ├── branches_routes.py   # Branch operations
│   │   ├── customers_routes.py  # Customer CRUD
│   │   ├── services_routes.py   # Service management
│   │   ├── subscriptions_routes.py  # Subscription operations
│   │   ├── transactions_routes.py   # Financial records
│   │   ├── expenses_routes.py   # Expense tracking
│   │   ├── complaints_routes.py # Complaint handling
│   │   ├── fingerprints_routes.py   # Access control
│   │   ├── dashboards_routes.py # Analytics & reports
│   │   ├── test_routes.py       # Test page
│   │   ├── client_auth_routes.py    # 🆕 Client OTP login
│   │   ├── client_routes.py     # 🆕 Client mobile API
│   │   └── validation_routes.py # 🆕 Entry validation
│   │
│   ├── services/                # Business logic layer
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication logic
│   │   ├── subscription_service.py  # Subscription business rules
│   │   ├── dashboard_service.py     # Analytics & reporting
│   │   ├── notification_service.py  # 🆕 SMS/Email abstraction
│   │   └── qr_service.py        # 🆕 QR/barcode validation
│   │
│   ├── schemas/                 # Marshmallow schemas
│   │   └── __init__.py          # Validation & serialization
│   │
│   └── utils/                   # Helper functions
│       ├── __init__.py
│       ├── decorators.py        # Custom decorators (RBAC)
│       ├── helpers.py           # Utility functions
│       └── client_auth.py       # 🆕 Client JWT helpers
│
├── tests/
│   └── test_accounts.json       # Test account credentials
│
├── migrations/                  # Database migration scripts
│
├── instance/                    # SQLite database (auto-created)
│
├── venv/                        # Python virtual environment
│
├── .env                         # Environment variables (create from .env.example)
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
├── requirements.txt             # Python dependencies
├── seed.py                      # Database seeding script
├── migrate_client_features.py   # 🆕 Client features migration
├── test_client_features.py      # 🆕 Client API test suite
├── run.py                       # Application entry point
├── quick_start.bat              # Windows quick start script
├── README.md                    # This file
├── CLIENT_FEATURES_API.md       # 🆕 Client API documentation
├── CLIENT_FEATURES_IMPLEMENTATION.md  # 🆕 Implementation guide
└── QUICK_START_CLIENT.md        # 🆕 Client features quick start
```

## 🚀 Quick Start

### Windows (Easiest Method)

1. **Clone the repository**
   ```bash
   cd backend
   ```

2. **Run the quick start script**
   ```bash
   quick_start.bat
   ```

   This script will:
   - ✅ Check Python installation
   - ✅ Create virtual environment
   - ✅ Install all dependencies
   - ✅ Initialize the database
   - ✅ Seed with test data
   - ✅ Start the Flask server

3. **Access the API**
   - API Base: `http://localhost:5000`
   - Test Page: `http://localhost:5000/test`

### Manual Setup

1. **Create virtual environment**
   ```bash
   python -m venv venv
   ```

2. **Activate virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate

   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   copy .env.example .env
   # Edit .env with your settings
   ```

5. **Initialize database**
   ```bash
   flask init-db
   ```

6. **Seed test data**
   ```bash
   python seed.py
   ```

7. **🆕 Add client features (optional)**
   ```bash
   python migrate_client_features.py
   ```
   This creates activation_codes and entry_logs tables with sample data.

8. **Run the server**
   ```bash
   python run.py
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```bash
FLASK_APP=run.py
FLASK_ENV=development  # or production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Database (SQLite for development)
DATABASE_URL=sqlite:///gym_management.db

# For production, use PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/gym_db
```

### Database Configuration

**Development (SQLite):**
- Automatically created in `instance/gym_management.db`
- Perfect for testing and development

**Production (PostgreSQL):**
```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://username:password@host:5432/database_name
```

## 📚 API Documentation

### Base URL
```
http://localhost:5000/api
```

### Test Page
Visit `http://localhost:5000/test` for interactive API documentation with example requests.

### 📱 Client Mobile API Documentation
**Complete Client Features Documentation:**
- **[Client Features API Reference](CLIENT_FEATURES_API.md)** - 11 endpoints for mobile apps
- **[Implementation Guide](CLIENT_FEATURES_IMPLEMENTATION.md)** - Architecture & flows
- **[Quick Start Guide](QUICK_START_CLIENT.md)** - Get started in 5 minutes

**Client Endpoints:**
- Client OTP authentication (request-code, verify-code)
- QR code generation for gym entry
- Client profile and subscription info
- Entry history and statistics
- Staff validation (QR, barcode, manual entry)

### Authentication

All endpoints (except `/test` and `/api/fingerprints/validate`) require JWT authentication.

**Login:**
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "owner",
  "password": "owner123"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "user": {
      "id": 1,
      "username": "owner",
      "role": "owner",
      ...
    }
  }
}
```

**Using the token:**
```http
GET /api/customers
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

## 🔐 Authentication & Authorization

### JWT Token Flow
1. User logs in with username/password
2. Server returns JWT access token (12 hours) and refresh token (30 days)
3. Client includes token in `Authorization: Bearer <token>` header
4. Server validates token and checks user permissions

### Role-Based Access Control (RBAC)

Routes are protected by role decorators:
```python
@jwt_required()
@role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER)
def some_protected_route():
    # Only Owner and Branch Manager can access
    pass
```

## 👥 User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| **Owner** | System administrator | Full access to all branches and features |
| **Branch Manager** | Branch administrator | Manage specific branch operations |
| **Front Desk** | Reception staff | Register customers, create subscriptions |
| **Accountant** | Financial officer | View transactions, approve expenses |
| **Branch Accountant** | Branch finance | Branch-specific financial access |
| **Central Accountant** | Central finance | System-wide financial access |

### Test Accounts

```json
{
  "owner": {
    "username": "owner",
    "password": "owner123"
  },
  "manager": {
    "username": "manager1",
    "password": "manager123"
  },
  "reception": {
    "username": "reception1",
    "password": "reception123"
  },
  "accountant": {
    "username": "accountant1",
    "password": "accountant123"
  }
}
```

## 🗄️ Database Models

### Core Models

1. **User** - Staff and administrators
2. **Branch** - Gym locations
3. **Customer** - Gym members with health metrics
4. **Service** - Available gym services
5. **Subscription** - Customer subscriptions
6. **Transaction** - Financial records
7. **Expense** - Business expenses
8. **Complaint** - Customer feedback
9. **Fingerprint** - Access control (simulated)
10. **FreezeHistory** - Subscription freeze records
11. **DailyClosing** - Daily cash reconciliation

### Key Features

- **Health Metrics Auto-Calculation** - BMI, ideal weight, daily calories
- **Subscription Status Management** - Active, Frozen, Stopped, Expired
- **Flexible Freeze Rules** - Configurable freeze limits and costs
- **Multi-Payment Support** - Cash, Network, Transfer
- **Expense Approval Workflow** - Pending → Approved/Rejected

## 🧪 Testing

### Test Data
The `seed.py` script creates:
- 3 Branches
- 8 Users (all roles)
- 10 Customers
- 6 Services
- 11 Subscriptions
- Multiple Transactions, Expenses, Complaints

### Testing with Flutter

**API Response Format:**
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

**Error Format:**
```json
{
  "success": false,
  "error": "Error message",
  "errors": { ... }  // Validation errors
}
```

**Pagination Format:**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "pagination": {
      "total": 100,
      "pages": 5,
      "current_page": 1,
      "per_page": 20
    }
  }
}
```

## 📱 Flutter Integration

### Authentication Example
```dart
// Login
final response = await http.post(
  Uri.parse('http://localhost:5000/api/auth/login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'owner',
    'password': 'owner123'
  })
);

final data = jsonDecode(response.body);
final token = data['data']['access_token'];

// Use token in subsequent requests
final customersResponse = await http.get(
  Uri.parse('http://localhost:5000/api/customers'),
  headers: {
    'Authorization': 'Bearer $token'
  }
);
```

## 🚀 Deployment

### Production Checklist

1. **Change secret keys** in `.env`
2. **Use PostgreSQL** instead of SQLite
3. **Set** `FLASK_ENV=production`
4. **Use a production WSGI server** (Gunicorn)
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 run:app
   ```
5. **Enable HTTPS**
6. **Set up proper logging**
7. **Configure CORS** for your Flutter app domain
8. **Use environment-specific configs**

### Production Database Migration
```bash
# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## 📊 Key Endpoints Summary

| Category | Endpoint | Method | Description |
|----------|----------|--------|-------------|
| Auth | `/api/auth/login` | POST | User login |
| Auth | `/api/auth/me` | GET | Current user info |
| Branches | `/api/branches` | GET/POST | List/Create branches |
| Customers | `/api/customers` | GET/POST | List/Create customers |
| Services | `/api/services` | GET/POST | List/Create services |
| Subscriptions | `/api/subscriptions` | GET/POST | List/Create subscriptions |
| Subscriptions | `/api/subscriptions/{id}/freeze` | POST | Freeze subscription |
| Subscriptions | `/api/subscriptions/{id}/renew` | POST | Renew subscription |
| Fingerprints | `/api/fingerprints/register` | POST | Register fingerprint |
| Fingerprints | `/api/fingerprints/validate` | POST | Validate access |
| Dashboards | `/api/dashboards/owner` | GET | Owner dashboard |
| Dashboards | `/api/dashboards/accountant` | GET | Accountant dashboard |

## 🤝 Contributing

This is a production-ready backend system. Key areas for enhancement:
- Advanced reporting features
- Email/SMS notifications
- Mobile app push notifications
- Advanced scheduling system
- Integration with payment gateways

## 📝 License

Proprietary - Gym Management System

## 🆘 Support

For issues or questions:
1. Check the test page at `http://localhost:5000/test`
2. Review test accounts in `tests/test_accounts.json`
3. Examine seed data in `seed.py`

## 🎯 Key Features for Flutter Integration

✅ **JSON-only responses** - No HTML rendering  
✅ **Consistent error handling** - Standard format across all endpoints  
✅ **JWT authentication** - Stateless and mobile-friendly  
✅ **Pagination support** - Efficient data loading  
✅ **Role-based access** - Secure permission system  
✅ **Comprehensive validation** - Marshmallow schemas  
✅ **CORS enabled** - Cross-origin requests supported  

### 📱 Client Mobile Features (NEW)
✅ **OTP Authentication** - Password-less login for clients  
✅ **Dual JWT System** - Separate tokens for staff vs clients  
✅ **QR Code Entry** - Time-limited codes with signature validation  
✅ **Entry Validation API** - QR, barcode, and manual entry  
✅ **Client Analytics** - Visit history, streaks, and statistics  
✅ **Pluggable Notifications** - SMS/Email abstraction layer  

**Complete Documentation:** [CLIENT_FEATURES_API.md](CLIENT_FEATURES_API.md) | [QUICK_START_CLIENT.md](QUICK_START_CLIENT.md)  

---

**Built with ❤️ for efficient gym management**
