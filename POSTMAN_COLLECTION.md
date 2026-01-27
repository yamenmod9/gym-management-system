# Gym Management System API - Postman Collection

## Quick Import Instructions

1. Open Postman
2. Click "Import" button
3. Paste this URL or upload this file
4. Collection will be ready to use with all endpoints

## Base Configuration

- **Base URL**: `http://localhost:5000`
- **API Prefix**: `/api`

## Authentication Flow

1. Use `POST /api/auth/login` to get JWT token
2. Copy the `access_token` from response
3. Use it in Authorization header: `Bearer <token>`

## Test Accounts

### Owner
```json
{
  "username": "owner",
  "password": "owner123"
}
```

### Branch Manager
```json
{
  "username": "manager1",
  "password": "manager123"
}
```

### Receptionist
```json
{
  "username": "reception1",
  "password": "reception123"
}
```

### Accountant
```json
{
  "username": "accountant1",
  "password": "accountant123"
}
```

## Available Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/change-password` - Change password

### Users
- `GET /api/users` - List all users (paginated)
- `GET /api/users/{id}` - Get user details
- `POST /api/users` - Create new user (Owner/Manager only)
- `PUT /api/users/{id}` - Update user
- `DELETE /api/users/{id}` - Deactivate user

### Branches
- `GET /api/branches` - List all branches
- `GET /api/branches/{id}` - Get branch details
- `POST /api/branches` - Create branch (Owner only)
- `PUT /api/branches/{id}` - Update branch
- `DELETE /api/branches/{id}` - Deactivate branch

### Customers
- `GET /api/customers` - List customers (paginated, filtered by branch)
- `GET /api/customers/{id}` - Get customer details
- `GET /api/customers/phone/{phone}` - Get customer by phone
- `POST /api/customers` - Register new customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Deactivate customer

### Services
- `GET /api/services` - List all services
- `GET /api/services/{id}` - Get service details
- `POST /api/services` - Create service
- `PUT /api/services/{id}` - Update service
- `DELETE /api/services/{id}` - Deactivate service

### Subscriptions
- `GET /api/subscriptions` - List subscriptions
- `GET /api/subscriptions/{id}` - Get subscription details
- `POST /api/subscriptions` - Create subscription
- `POST /api/subscriptions/{id}/renew` - Renew subscription
- `POST /api/subscriptions/{id}/freeze` - Freeze subscription
- `POST /api/subscriptions/{id}/unfreeze` - Unfreeze subscription
- `POST /api/subscriptions/{id}/stop` - Stop subscription

### Transactions
- `GET /api/transactions` - List transactions
- `GET /api/transactions/{id}` - Get transaction details
- `POST /api/transactions` - Create transaction

### Expenses
- `GET /api/expenses` - List expenses
- `GET /api/expenses/{id}` - Get expense details
- `POST /api/expenses` - Create expense
- `POST /api/expenses/{id}/review` - Approve/reject expense
- `DELETE /api/expenses/{id}` - Delete expense

### Complaints
- `GET /api/complaints` - List complaints
- `GET /api/complaints/{id}` - Get complaint details
- `POST /api/complaints` - Create complaint
- `PUT /api/complaints/{id}` - Update complaint status
- `DELETE /api/complaints/{id}` - Delete complaint

### Fingerprints
- `GET /api/fingerprints` - List fingerprints
- `POST /api/fingerprints/register` - Register fingerprint
- `POST /api/fingerprints/validate` - Validate access (NO AUTH)
- `POST /api/fingerprints/{id}/deactivate` - Deactivate fingerprint
- `POST /api/fingerprints/{id}/reactivate` - Reactivate fingerprint

### Dashboards
- `GET /api/dashboards/owner` - Owner dashboard (Owner only)
- `GET /api/dashboards/accountant` - Accountant dashboard
- `GET /api/dashboards/branch-manager` - Branch manager dashboard
- `GET /api/dashboards/reports/revenue` - Revenue report
- `GET /api/dashboards/alerts/expiring-subscriptions` - Expiring subscriptions alert

## Example Requests

### Login
```http
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "username": "owner",
  "password": "owner123"
}
```

### Create Customer
```http
POST http://localhost:5000/api/customers
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "full_name": "John Doe",
  "phone": "01234567899",
  "email": "john@example.com",
  "date_of_birth": "1990-01-01",
  "gender": "male",
  "height": 180,
  "weight": 75,
  "branch_id": 1
}
```

### Create Subscription
```http
POST http://localhost:5000/api/subscriptions
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "customer_id": 1,
  "service_id": 1,
  "branch_id": 1,
  "payment_method": "cash"
}
```

### Freeze Subscription
```http
POST http://localhost:5000/api/subscriptions/1/freeze
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "days": 7,
  "reason": "Travel"
}
```

### Register Fingerprint
```http
POST http://localhost:5000/api/fingerprints/register
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "customer_id": 1,
  "unique_data": "simulated_fingerprint_12345"
}
```

### Validate Fingerprint (No Auth Required)
```http
POST http://localhost:5000/api/fingerprints/validate
Content-Type: application/json

{
  "fingerprint_hash": "hash_from_registration_response"
}
```

## Query Parameters

### Pagination
```
?page=1&per_page=20
```

### Filtering
```
?branch_id=1
?status=active
?start_date=2024-01-01&end_date=2024-01-31
```

### Search
```
?search=john
```

## Response Format

### Success
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional message"
}
```

### Error
```json
{
  "success": false,
  "error": "Error message",
  "errors": { ... }
}
```

### Paginated Response
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

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Amounts are in decimal format (e.g., "500.00")
- Date format: YYYY-MM-DD
- DateTime format: YYYY-MM-DDTHH:MM:SS
