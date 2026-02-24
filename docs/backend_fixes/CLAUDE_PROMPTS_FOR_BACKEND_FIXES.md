# CLAUDE SONNET 4.5 - COMPLETE BACKEND FIX PROMPTS

This document contains all the prompts you need to give to Claude Sonnet 4.5 to fix the backend issues for the Gym Management System.

---

## PROMPT 1: IMPLEMENT ALL REQUIRED ENDPOINTS

```
I'm building a Gym Management System backend using FastAPI and SQLAlchemy. 
I need you to implement all the required API endpoints for both the Staff App and Client App.

Please read the attached file "BACKEND_ENDPOINTS_REQUIRED.md" which lists all endpoints, 
request/response formats, and important notes about branch filtering, authentication, QR codes, 
and temporary passwords.

Key requirements:
1. Owner sees ALL branches data (branch_id can be NULL or filtered via query param)
2. Manager/Accountant/Reception see only THEIR branch data (branch_id is fixed)
3. Customers can only access their own data
4. Temporary passwords must be stored and returned to staff
5. QR codes must be in format: GYM-{branch_id}-{customer_id}
6. All subscriptions have proper session/coin deduction logic
7. Check-ins can optionally deduct sessions/coins

Please implement:
- All authentication endpoints (staff and client)
- All CRUD endpoints for branches, staff, customers, subscriptions
- Dashboard statistics endpoints
- Check-in and QR scanning endpoints
- Payment and reports endpoints
- Proper error handling with consistent response format
- JWT authentication with role-based access control

Use the response formats specified in the document.
```

---

## PROMPT 2: CREATE COMPREHENSIVE SEED DATA

```
I need you to create a comprehensive seed.py file for the Gym Management System database 
to enable thorough testing of both Staff and Client apps.

Please read the attached file "BACKEND_SEED_DATA_REQUIREMENTS.md" which specifies:
- Exactly what data to create (branches, services, staff, customers, subscriptions, etc.)
- How many of each entity
- Required fields for each entity (especially temp_password, qr_code, branch_id)
- Data validation rules (phone numbers, BMI calculations, etc.)

Critical requirements:
1. Create 200 customers (50 per branch) with:
   - Unique 6-character temporary passwords (e.g., "AB12CD")
   - password_changed = False
   - qr_code in format: "GYM-{branch_id}-{customer_id}"
   - Realistic health data (BMI, BMR, calories)

2. Create 1 Owner + 4 Managers + 4 Accountants + 8 Receptionists (17 staff total)
   - Owner has branch_id = NULL
   - Others assigned to specific branches

3. Create active subscriptions for 70% of customers
   - Mix of coins (30%), sessions (40%), unlimited (30%)
   - Some near expiry and low session counts for testing

4. Generate a test_credentials.txt file with all login information

Please implement the seed.py file with all the data as specified.
```

---

## PROMPT 3: FIX TEMPORARY PASSWORD DATABASE ISSUE

```
I have an issue where the temporary password is not being returned in API responses.

Please read the attached file "BACKEND_DATABASE_FIX_TEMP_PASSWORD.md" which explains:
- The problem (temp_password returns null)
- The root causes
- Complete solution with code examples

Please:
1. Verify the Customer model has temp_password and password_changed fields
2. Update customer creation to generate and store temp_password
3. Ensure GET /api/customers/{id} returns temp_password in response
4. Create POST /api/customers/{id}/temp-password endpoint for staff to retrieve it
5. Keep temp_password even after customer changes password (for records)
6. Create a migration script for existing customers without temp_password

The temporary password should be:
- 6 characters in format: LLDDLL (e.g., "AB12CD")
- Shown to reception after customer creation
- Visible to staff until customer changes it
- Stored separately from the hashed password
```

---

## PROMPT 4: FIX ALL REMAINING ISSUES

```
I have several issues in the backend that are preventing the Flutter apps from working properly.

Please read the attached file "BACKEND_COMPREHENSIVE_FIXES_REQUIRED.md" which details:

1. Branch Mismatch on Subscription Activation (403 error)
   - Customers are being assigned to wrong branches in seed data
   - Backend should allow owner to create subscriptions for any branch
   - Reception/Manager can only create for their branch

2. QR Code Regeneration Returns 404
   - Need to implement POST /api/customers/{id}/regenerate-qr endpoint

3. Check-In Fails After QR Scan
   - POST /api/checkins endpoint not working
   - POST /api/subscriptions/{id}/use-coins not implemented
   - POST /api/subscriptions/{id}/deduct-session not implemented

4. Dashboard Shows Zero Data
   - GET /api/dashboard/statistics not returning data
   - GET /api/branches not working properly
   - GET /api/staff not returning staff members

Please fix all these issues with proper error handling, branch filtering, and response formats.
```

---

## HOW TO USE THESE PROMPTS

1. **Open Claude Sonnet 4.5** (or Claude 3.5 Sonnet)

2. **For Prompt 1** (Endpoints):
   - Upload file: `BACKEND_ENDPOINTS_REQUIRED.md`
   - Paste Prompt 1
   - Claude will generate all endpoint implementations

3. **For Prompt 2** (Seed Data):
   - Upload file: `BACKEND_SEED_DATA_REQUIREMENTS.md`
   - Paste Prompt 2
   - Claude will generate seed.py file

4. **For Prompt 3** (Temp Password):
   - Upload file: `BACKEND_DATABASE_FIX_TEMP_PASSWORD.md`
   - Paste Prompt 3
   - Claude will fix the temp password issue

5. **For Prompt 4** (Comprehensive Fixes):
   - Upload file: `BACKEND_COMPREHENSIVE_FIXES_REQUIRED.md`
   - Paste Prompt 4
   - Claude will fix all remaining issues

---

## TESTING AFTER IMPLEMENTATION

After implementing all fixes, test:

1. **Staff Login**:
   - Login as: owner@gymclub.com / owner123
   - Login as: reception1@dragonclub.com / reception123

2. **Customer Registration**:
   - Create new customer
   - Verify temp_password is returned and displayed
   - Verify QR code is generated

3. **Subscription Activation**:
   - Activate subscription for customer in same branch → Should work
   - (As owner) Activate for customer in any branch → Should work
   - (As reception) Try to activate for customer in other branch → Should fail with clear error

4. **QR Code Scanning**:
   - Scan customer QR code
   - Check-in with session deduction → Should work
   - Check-in without deduction → Should work
   - Verify remaining sessions decrements

5. **Dashboard**:
   - Owner dashboard should show all branches data
   - Manager/Accountant dashboard should show their branch data
   - All numbers should be > 0 if data exists

6. **Client Login**:
   - Login with phone: 01077827638 / password: RX04AF (from seed data)
   - Should be forced to change password
   - After change, should access app features

---

## EXPECTED RESULTS

After all fixes:
- ✅ All endpoints respond correctly
- ✅ 200 customers with temp passwords and QR codes
- ✅ 17 staff members across 4 branches
- ✅ 140+ active subscriptions
- ✅ Dashboard shows real data
- ✅ QR scanning works
- ✅ Subscription activation works
- ✅ Check-ins work with session deduction
- ✅ Branch filtering enforced properly
- ✅ Owner can access all branches
- ✅ Staff can only access their branch

---

## FILES TO ATTACH

When using these prompts, attach the corresponding markdown files:
1. BACKEND_ENDPOINTS_REQUIRED.md
2. BACKEND_SEED_DATA_REQUIREMENTS.md  
3. BACKEND_DATABASE_FIX_TEMP_PASSWORD.md
4. BACKEND_COMPREHENSIVE_FIXES_REQUIRED.md

All files are in the root directory of the Flutter project: `C:\Programming\Flutter\gym_frontend\`

