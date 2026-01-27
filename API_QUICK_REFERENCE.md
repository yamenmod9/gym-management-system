# 🚀 API Quick Reference Card

## 🔗 Base URL
```
http://localhost:5000/api
```

## 🔐 Authentication

### Login
```http
POST /api/auth/login
{
  "username": "owner",
  "password": "owner123"
}
```

### Get Current User
```http
GET /api/auth/me
Authorization: Bearer {token}
```

## 👥 Quick Endpoints

### Customers
```http
GET    /api/customers              # List all
GET    /api/customers/{id}         # Get one
GET    /api/customers/phone/{phone} # Search by phone
POST   /api/customers              # Create
PUT    /api/customers/{id}         # Update
DELETE /api/customers/{id}         # Delete
```

### Subscriptions
```http
GET    /api/subscriptions          # List all
POST   /api/subscriptions          # Create
POST   /api/subscriptions/{id}/renew    # Renew
POST   /api/subscriptions/{id}/freeze   # Freeze
POST   /api/subscriptions/{id}/unfreeze # Unfreeze
POST   /api/subscriptions/{id}/stop     # Stop
```

### Fingerprints
```http
POST /api/fingerprints/register    # Register (Auth required)
POST /api/fingerprints/validate    # Validate (NO AUTH)
```

### Dashboards
```http
GET /api/dashboards/owner          # Owner dashboard
GET /api/dashboards/accountant     # Accountant dashboard
GET /api/dashboards/branch-manager # Branch manager dashboard
```

## 📋 Test Accounts

| Role | Username | Password |
|------|----------|----------|
| Owner | owner | owner123 |
| Manager | manager1 | manager123 |
| Reception | reception1 | reception123 |
| Accountant | accountant1 | accountant123 |

## 📊 Response Format

### Success
```json
{
  "success": true,
  "data": {...},
  "message": "Optional"
}
```

### Error
```json
{
  "success": false,
  "error": "Error message"
}
```

## 🔧 Query Parameters

```
?page=1&per_page=20           # Pagination
?branch_id=1                  # Filter by branch
?status=active                # Filter by status
?search=john                  # Search
?start_date=2024-01-01        # Date range
?end_date=2024-01-31
```

## 💡 Quick Tips

1. **Get Token**: Login first to get JWT token
2. **Use Token**: Add `Authorization: Bearer {token}` header
3. **Test Page**: Visit `/test` for full docs
4. **Pagination**: Most list endpoints support pagination
5. **Validation**: Errors return field-specific messages

## 🎯 Common Operations

### Register Customer & Create Subscription
```http
# 1. Create customer
POST /api/customers
{
  "full_name": "John Doe",
  "phone": "01234567890",
  "branch_id": 1,
  "height": 180,
  "weight": 75
}

# 2. Create subscription
POST /api/subscriptions
{
  "customer_id": 1,
  "service_id": 1,
  "branch_id": 1,
  "payment_method": "cash"
}

# 3. Register fingerprint
POST /api/fingerprints/register
{
  "customer_id": 1,
  "unique_data": "fingerprint_data_123"
}
```

### Validate Access (Kiosk)
```http
POST /api/fingerprints/validate
{
  "fingerprint_hash": "hash_from_registration"
}
```

## 📱 Flutter Example

```dart
// Login
final loginResponse = await http.post(
  Uri.parse('http://localhost:5000/api/auth/login'),
  headers: {'Content-Type': 'application/json'},
  body: jsonEncode({
    'username': 'owner',
    'password': 'owner123'
  })
);

final token = jsonDecode(loginResponse.body)['data']['access_token'];

// Get customers
final customersResponse = await http.get(
  Uri.parse('http://localhost:5000/api/customers'),
  headers: {
    'Authorization': 'Bearer $token',
    'Content-Type': 'application/json'
  }
);

final customers = jsonDecode(customersResponse.body)['data']['items'];
```

## 🛠 Setup Commands

```bash
# Windows Quick Start
quick_start.bat

# Manual Setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
flask init-db
python seed.py
python run.py
```

## 📖 Full Documentation

- README.md - Complete documentation
- /test endpoint - Interactive API docs
- PROJECT_STATUS.md - Implementation details
- POSTMAN_COLLECTION.md - Postman guide

---

**Need help?** Check http://localhost:5000/test
