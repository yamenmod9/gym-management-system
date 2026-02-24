# Deployment Instructions for PythonAnywhere

## ✅ Changes Summary
Successfully implemented customer registration fix with the following features:

- ✅ New endpoint: `POST /api/customers/register`
- ✅ QR code generation in format: `GYM-{customer_id}`
- ✅ Added 3 new database fields: `qr_code`, `bmi_category`, `bmr`
- ✅ Automatic health metrics calculation (BMI, BMR, BMI category)
- ✅ Age calculation from date_of_birth
- ✅ Database migration for existing 150 customers completed locally

## 🚀 PythonAnywhere Deployment Steps

### 1. Login to PythonAnywhere
Go to: https://www.pythonanywhere.com/user/yamenmod91/

### 2. Open a Bash Console
Click on "Consoles" → "Bash"

### 3. Navigate to Project Directory
```bash
cd ~/gym-management-system/backend
```

### 4. Pull Latest Changes from GitHub
```bash
git pull origin main
```

You should see:
- `app/models/customer.py` - Updated with new fields
- `app/routes/customers_routes.py` - New /register endpoint
- `migrate_customer_fields.py` - Migration script

### 5. Run Database Migration
```bash
python3 migrate_customer_fields.py
```

Expected output:
```
Starting database migration...
  ✓ Will add qr_code column with unique index
  ✓ Will add bmi_category column
  ✓ Will add bmr column

⚠️  Applying 4 migrations...
  Executing: ALTER TABLE customers ADD COLUMN qr_code VARCHAR(50)
  Executing: CREATE UNIQUE INDEX idx_customers_qr_code ON customers(qr_code)
  Executing: ALTER TABLE customers ADD COLUMN bmi_category VARCHAR(20)
  Executing: ALTER TABLE customers ADD COLUMN bmr FLOAT

✅ Database migration completed successfully!

Generating QR codes for existing customers...
  [150 customers will be processed]
✅ Generated 150 QR codes

Recalculating health metrics for existing customers...
  [150 customers will be processed]
✅ Updated health metrics for 150 customers
```

### 6. Reload Web App
1. Go to "Web" tab in PythonAnywhere dashboard
2. Click the green "Reload yamenmod91.pythonanywhere.com" button
3. Wait for confirmation message

### 7. Verify Deployment
Test the endpoint from Flutter app or use curl:

```bash
# Login first
curl -X POST https://yamenmod91.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "reception1", "password": "reception123"}'

# Copy the access_token from response, then:
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01999888777",
    "gender": "male",
    "age": 25,
    "height": 180,
    "weight": 75,
    "branch_id": 1
  }'
```

Expected response:
```json
{
  "success": true,
  "message": "Customer registered successfully",
  "data": {
    "id": 151,
    "qr_code": "GYM-151",
    "full_name": "Test Customer",
    "phone": "01999888777",
    "age": 25,
    "bmi": 23.15,
    "bmi_category": "Normal",
    "bmr": 1775.5,
    "daily_calories": 2752,
    ...
  }
}
```

## 📱 Flutter App Testing

After deployment, test from your Flutter app:
1. Login as reception1
2. Navigate to customer registration screen
3. Fill in customer details
4. Submit registration
5. Verify:
   - ✅ No more "Resource not found" error
   - ✅ Customer created successfully
   - ✅ QR code generated automatically
   - ✅ Health metrics calculated

## 🔍 Troubleshooting

### If migration fails:
```bash
# Check if columns already exist
sqlite3 ~/gym-management-system/backend/instance/gymdb.db
> PRAGMA table_info(customers);
> .quit
```

### If web app doesn't reload:
1. Check error log in PythonAnywhere "Web" tab
2. Look for import errors or syntax issues
3. Verify virtual environment is activated

### If endpoint returns 500 error:
1. Check error log: `/var/log/yamenmod91.pythonanywhere.com.error.log`
2. Verify Gender enum is imported in customers_routes.py
3. Check database migration completed successfully

## 📊 Database Changes

### New Columns Added
| Column Name | Type | Constraints | Description |
|------------|------|-------------|-------------|
| qr_code | VARCHAR(50) | UNIQUE, Indexed | Format: GYM-{id} |
| bmi_category | VARCHAR(20) | NULL | Underweight/Normal/Overweight/Obese |
| bmr | FLOAT | NULL | Basal Metabolic Rate |

### Existing Customers
- All 150 existing customers updated with QR codes
- Health metrics recalculated for customers with height/weight data

## 🎯 What's Fixed

### Before:
```
POST /api/customers/register
❌ 404 Not Found - Resource not found
```

### After:
```
POST /api/customers/register
✅ 201 Created - Customer registered successfully
{
  "qr_code": "GYM-151",
  "bmi_category": "Normal",
  "bmr": 1843.6,
  ...
}
```

## 🔗 Related Endpoints

The following endpoints are now available:

1. **Register Customer (NEW)**
   - `POST /api/customers/register`
   - Roles: owner, branch_manager, front_desk
   - Flutter-compatible format

2. **Create Customer (Existing)**
   - `POST /api/customers`
   - Now generates QR codes automatically
   - Uses schema validation

3. **Get Customer**
   - `GET /api/customers/{id}`
   - Returns customer with QR code and health metrics

4. **Get by Phone**
   - `GET /api/customers/phone/{phone}`
   - Search using phone number

---

**Deployed:** February 9, 2026  
**GitHub Commit:** 2d614a7  
**Local Testing:** ✅ Passed  
**Production Status:** ⏳ Awaiting deployment to PythonAnywhere

