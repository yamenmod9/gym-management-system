# BACKEND ENDPOINTS REQUIRED FOR GYM MANAGEMENT SYSTEM

## STAFF APP ENDPOINTS

### Authentication
- `POST /api/staff/auth/login` - Staff login (all roles)
- `POST /api/staff/auth/logout` - Staff logout
- `POST /api/staff/auth/change-password` - Change password
- `GET /api/staff/auth/me` - Get current staff profile

### Owner Endpoints
- `GET /api/owner/dashboard/statistics` - Overall statistics (all branches)
- `GET /api/owner/dashboard/revenue` - Revenue analytics
- `GET /api/owner/dashboard/alerts` - Smart alerts
- `GET /api/branches` - List all branches
- `GET /api/branches/{id}` - Get branch details
- `POST /api/branches` - Create new branch
- `PUT /api/branches/{id}` - Update branch
- `DELETE /api/branches/{id}` - Delete branch
- `GET /api/staff` - List all staff (all roles)
- `GET /api/staff/{id}` - Get staff details
- `POST /api/staff` - Create new staff member
- `PUT /api/staff/{id}` - Update staff
- `DELETE /api/staff/{id}` - Delete staff
- `GET /api/reports/branch-comparison` - Compare branches
- `GET /api/reports/revenue` - Revenue report
- `GET /api/reports/employee-performance` - Staff performance

### Manager Endpoints
- `GET /api/manager/dashboard/statistics` - Branch statistics (manager's branch only)
- `GET /api/manager/branch` - Get assigned branch details
- `GET /api/manager/staff` - List staff in manager's branch
- `GET /api/customers` - List customers with branch filter
- `GET /api/subscriptions` - List subscriptions with branch filter
- `GET /api/reports/branch-revenue` - Branch revenue report
- `GET /api/complaints` - List complaints

### Accountant Endpoints
- `GET /api/accountant/dashboard/statistics` - Financial statistics (branch-specific)
- `GET /api/payments` - List all payments with filters
- `GET /api/payments/{id}` - Get payment details
- `POST /api/payments` - Record new payment
- `PUT /api/payments/{id}` - Update payment
- `GET /api/reports/revenue` - Revenue reports
- `GET /api/reports/payments` - Payment reports
- `GET /api/subscriptions` - List subscriptions (for revenue tracking)
- `POST /api/reports/export` - Export financial reports

### Reception Endpoints
- `GET /api/reception/dashboard/statistics` - Reception statistics (branch-specific)
- `GET /api/customers` - List customers with branch filter
- `GET /api/customers/{id}` - Get customer details
- `POST /api/customers` - Register new customer
- `PUT /api/customers/{id}` - Update customer
- `DELETE /api/customers/{id}` - Delete customer (soft delete)
- `POST /api/customers/{id}/regenerate-qr` - Regenerate customer QR code
- `GET /api/customers/{id}/temp-password` - Get customer temporary password
- `POST /api/subscriptions` - Create/activate subscription
- `POST /api/subscriptions/activate` - Activate subscription for customer
- `POST /api/subscriptions/{id}/freeze` - Freeze subscription
- `POST /api/subscriptions/{id}/renew` - Renew subscription
- `POST /api/subscriptions/{id}/stop` - Stop subscription
- `POST /api/subscriptions/{id}/use-coins` - Deduct coins from subscription
- `POST /api/subscriptions/{id}/deduct-session` - Deduct session from subscription
- `GET /api/services` - List available services
- `POST /api/checkins` - Record customer check-in
- `GET /api/checkins` - List check-ins
- `POST /api/complaints` - Submit complaint
- `GET /api/complaints` - List complaints

### Common Staff Endpoints
- `GET /api/customers/search` - Search customers
- `GET /api/subscriptions/active` - Get active subscriptions count
- `GET /api/complaints/{id}` - Get complaint details
- `PUT /api/complaints/{id}` - Update complaint status

---

## CLIENT APP ENDPOINTS

### Authentication
- `POST /api/client/auth/login` - Customer login (phone + temp password)
- `POST /api/client/auth/change-password` - Change password (forced on first login)
- `POST /api/client/auth/logout` - Customer logout
- `GET /api/client/auth/me` - Get current customer profile

### Customer Profile
- `GET /api/client/profile` - Get customer profile
- `PUT /api/client/profile` - Update profile
- `GET /api/client/profile/qr-code` - Get QR code for gym entry
- `GET /api/client/profile/health-metrics` - Get health metrics (BMI, BMR, calories)

### Subscriptions
- `GET /api/client/subscriptions` - Get customer's subscriptions
- `GET /api/client/subscriptions/active` - Get active subscription
- `GET /api/client/subscriptions/{id}` - Get subscription details

### Check-ins
- `GET /api/client/checkins` - Get check-in history
- `GET /api/client/checkins/stats` - Get check-in statistics
- `POST /api/client/checkins/verify` - Verify QR code for check-in (scanned by reception)

### Complaints
- `GET /api/client/complaints` - Get customer's complaints
- `POST /api/client/complaints` - Submit new complaint
- `GET /api/client/complaints/{id}` - Get complaint details

### Branch Info
- `GET /api/client/branch` - Get customer's branch information
- `GET /api/client/branch/services` - Get available services at branch

---

## SHARED/PUBLIC ENDPOINTS
- `GET /api/branches/public` - List public branch information
- `GET /api/services/public` - List available services
- `GET /api/health` - Health check endpoint

---

## REQUEST/RESPONSE FORMATS

### Authentication Responses
```json
{
  "success": true,
  "token": "jwt_token_here",
  "user": {
    "id": 1,
    "full_name": "John Doe",
    "role": "reception",
    "branch_id": 1,
    "branch_name": "Dragon Club",
    "password_changed": true
  }
}
```

### Customer Response (for Staff)
```json
{
  "id": 1,
  "full_name": "Ahmed Hassan",
  "phone": "01012345678",
  "email": "ahmed@example.com",
  "branch_id": 1,
  "branch_name": "Dragon Club",
  "qr_code": "GYM-1-1",
  "temp_password": "AB12CD",
  "password_changed": false,
  "is_active": true,
  "gender": "male",
  "date_of_birth": "1990-01-15",
  "height": 1.75,
  "weight": 80.0,
  "bmi": 26.1,
  "bmi_category": "Overweight",
  "bmr": 1850.5,
  "daily_calories": 2868,
  "created_at": "2026-01-01T10:00:00",
  "updated_at": "2026-02-15T10:00:00"
}
```

### Subscription Response
```json
{
  "id": 1,
  "customer_id": 1,
  "service_id": 1,
  "service_name": "Monthly Membership",
  "branch_id": 1,
  "type": "coins",
  "coins": 20,
  "remaining_sessions": 15,
  "status": "active",
  "start_date": "2026-02-01",
  "end_date": "2026-03-01",
  "amount": 500.0,
  "payment_method": "cash",
  "created_at": "2026-02-01T10:00:00"
}
```

### Check-in Request
```json
{
  "customer_id": 1,
  "subscription_id": 1,
  "deduct_session": true,
  "notes": "Regular check-in"
}
```

### Check-in Response
```json
{
  "success": true,
  "message": "Check-in successful",
  "remaining_sessions": 14,
  "checkin": {
    "id": 1,
    "customer_id": 1,
    "subscription_id": 1,
    "checked_in_at": "2026-02-15T14:30:00",
    "sessions_deducted": 1
  }
}
```

---

## ERROR RESPONSES

All endpoints should return consistent error responses:

```json
{
  "success": false,
  "error": "Error message here",
  "details": "Optional detailed error information"
}
```

HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

---

## IMPORTANT NOTES

1. **Branch Filtering**: 
   - Owner sees ALL data across all branches
   - Manager/Accountant/Reception see only their branch data
   - Backend must enforce this at API level, not just frontend

2. **Authentication**:
   - All staff endpoints require JWT authentication
   - Client endpoints require customer JWT authentication
   - Tokens should include user role and branch_id

3. **QR Code Format**:
   - Format: `GYM-{branch_id}-{customer_id}` (e.g., "GYM-1-123")
   - Must be unique per customer
   - Should be regenerable if lost/compromised

4. **Temporary Password**:
   - Generated on customer creation
   - Format: 6 characters (e.g., "AB12CD")
   - Must be shown to reception after creation
   - Stored in `temp_password` field until first login
   - Set `password_changed = false` initially

5. **Subscriptions**:
   - Can only be created for customers in same branch as staff
   - Check-ins should deduct from remaining_sessions/coins
   - Status should auto-update based on expiry/session count

6. **Pagination**:
   - All list endpoints should support pagination
   - Query params: `page`, `limit`, `offset`
   - Response should include: `items`, `total`, `page`, `limit`

