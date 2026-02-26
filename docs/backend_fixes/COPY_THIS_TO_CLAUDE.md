═══════════════════════════════════════════════════════════════════════════
📋 COPY THIS ENTIRE PROMPT TO CLAUDE SONNET 4.5
═══════════════════════════════════════════════════════════════════════════

# Flutter Gym App - Registration & Login Issues

I have a Flutter gym management app with a Flask/Python backend. I'm experiencing two critical issues:

## 🔴 ISSUE 1: Registration Fails with "Resource Not Found"

### Current Behavior:
- Frontend sends POST request to: `https://yamenmod91.pythonanywhere.com/api/customers/register`
- Backend returns: `404 Not Found` or "Resource not found" error
- No customer is created in database

### Expected Request Body:
```json
{
  "full_name": "John Doe",
  "phone": "01234567890",
  "email": "john@example.com",
  "gender": "male",
  "age": 25,
  "weight": 75.0,
  "height": 1.75,
  "bmi": 24.5,
  "bmi_category": "Normal",
  "bmr": 1700.0,
  "daily_calories": 2500.0,
  "branch_id": 1
}
```

### Expected Success Response:
```json
{
  "message": "Customer registered successfully",
  "customer": {
    "id": 123,
    "full_name": "John Doe",
    "qr_code": "GYM-123",
    ...
  }
}
```

### What I Need:
- Fix or create the `/api/customers/register` endpoint
- Endpoint should require JWT authentication (Bearer token)
- Generate QR code as `f"GYM-{customer_id}"` after creating customer
- Return 201 status with customer object

---

## 🔴 ISSUE 2: Login Navigation Fails for Some Roles

### Current Behavior:
- Some users log in but don't navigate to their dashboard
- No error shown, just stays on login screen
- Affects: reception (front_desk), accountants

### Backend Role Strings:
My backend MUST return these **EXACT** role strings in login response:

1. `'owner'` - System owner (no branch_id)
2. `'branch_manager'` - Branch manager (has branch_id)
3. `'front_desk'` - Reception staff (has branch_id)
4. `'central_accountant'` - Central accountant (no branch_id)
5. `'branch_accountant'` - Branch accountant (has branch_id)

### Login Response Format:
```json
{
  "status": "success",
  "data": {
    "access_token": "...",
    "user": {
      "id": 5,
      "username": "reception1",
      "role": "front_desk",  // Must be exact lowercase with underscore
      "branch_id": 1,        // Integer or null
      "branch_name": "Dragon Club"
    }
  }
}
```

### Test Accounts:
- reception1 / reception123 → Should have role: "front_desk"
- accountant1 / accountant123 → Should have role: "central_accountant"
- baccountant1 / accountant123 → Should have role: "branch_accountant"

### What I Need:
- Verify login endpoint returns these exact role strings (lowercase with underscores)
- Verify branch_id is integer (not string) or null for owner/central_accountant
- Ensure response structure matches format above

---

## 🧪 TESTING COMMANDS

### Test Registration (with valid token):
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "full_name": "Test User",
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

### Test Login:
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "reception1", "password": "reception123"}'
```

---

## 📋 COMMON BACKEND ISSUES TO CHECK

### For Registration:
- [ ] Route exists: `/api/customers/register` (POST)
- [ ] Route is registered in Flask app
- [ ] Endpoint requires JWT authentication
- [ ] QR code generation: `customer.qr_code = f"GYM-{customer.id}"`
- [ ] Returns 201 status code
- [ ] Returns customer object in response

### For Login/Roles:
- [ ] Roles are exact strings: 'front_desk', 'central_accountant', 'branch_accountant'
- [ ] Roles are lowercase with underscores (not camelCase or spaces)
- [ ] branch_id is integer or null (not string)
- [ ] Response structure matches expected format

---

## ✅ SUCCESS CRITERIA

### Registration Working:
- POST to `/api/customers/register` returns 201 Created
- Customer saved to database with all fields
- QR code generated and returned
- Flutter app can register customers successfully

### Login Working:
- All test accounts can log in
- Correct role strings returned
- Users navigate to appropriate dashboards
- Data filtering works (branch-specific vs. system-wide)

---

## 💡 WHAT TO PROVIDE

Please analyze my backend code and provide:

1. **Root cause** of both issues
2. **Fixed code** for registration endpoint and role handling
3. **Working cURL commands** demonstrating fixes
4. **Deployment instructions** for PythonAnywhere

---

**Backend Framework**: Flask (Python)  
**Hosting**: PythonAnywhere (https://yamenmod91.pythonanywhere.com)  
**Frontend**: Flutter (already fixed and working correctly)  
**Database**: SQLite/MySQL (your backend)

**Note**: The Flutter frontend code is 100% correct. The issues are purely backend API problems.

[PASTE YOUR BACKEND CODE BELOW OR ATTACH FILES]
