# 🎯 HOW TO LOGIN AS A GYM CLIENT (CUSTOMER)

## 📱 Two Separate Apps

Your Flutter project has **TWO SEPARATE APPS**:

1. **Staff App** (`lib/main.dart`) - For reception, managers, accountants, owner
   - Uses username + password
   - For managing gym operations

2. **Client App** (`lib/client_main.dart`) - For gym members/customers
   - Uses phone/email + 6-digit activation code
   - For viewing subscription, QR code, entry history

---

## 🚀 HOW TO RUN THE CLIENT APP

### Method 1: Modify main.dart (Temporary)

1. Open `lib/main.dart`
2. Replace the entire content with:

```dart
import 'package:flutter/material.dart';
import 'client_main.dart';

void main() {
  runApp(const GymClientApp());
}
```

3. Run the app:
```bash
flutter run
```

### Method 2: Run Client App Directly (Command Line)

```bash
flutter run -t lib/client_main.dart
```

### Method 3: Create Build Configuration (Recommended)

In your IDE (Android Studio / VS Code):

**Android Studio:**
1. Run → Edit Configurations
2. Click `+` → Flutter
3. Name: "Client App"
4. Dart entrypoint: `lib/client_main.dart`
5. Click OK
6. Select "Client App" from dropdown and run

**VS Code:**
1. Create `.vscode/launch.json`:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Staff App",
      "request": "launch",
      "type": "dart",
      "program": "lib/main.dart"
    },
    {
      "name": "Client App",
      "request": "launch",
      "type": "dart",
      "program": "lib/client_main.dart"
    }
  ]
}
```
2. Press F5 and select "Client App"

---

## 🔐 HOW TO LOGIN AS A CLIENT

### Step 1: You Need a Customer Account First

Before logging in as a client, you need to be registered as a customer in the system.

**Option A: Ask Reception to Register You**
1. Run the **Staff App** (`lib/main.dart`)
2. Login as reception (e.g., `reception1` / `reception123`)
3. Go to "Register Customer"
4. Fill in your details (name, phone, email, etc.)
5. Register

**Option B: Use an Existing Customer**
- If you already have customers in the backend database, use their phone/email

---

### Step 2: Run the Client App

```bash
flutter run -t lib/client_main.dart
```

Or use one of the methods above.

---

### Step 3: Request Activation Code

When the client app opens, you'll see the **Welcome Screen**:

1. **Enter your phone or email** (the one used when registering)
   - Example: `01234567890` or `customer@example.com`
2. Click **"Request Activation Code"**

---

### Step 4: Backend Sends 6-Digit Code

The backend should:
1. Find your customer account by phone/email
2. Generate a 6-digit code (e.g., `123456`)
3. Save it with 10-minute expiration
4. Send it via SMS or email (can be mocked for testing)

**⚠️ IMPORTANT:** Check your backend logs to see the generated code!

For testing, the backend developer can:
- Print the code to console
- Return it in the API response
- Save it to a test file

---

### Step 5: Enter Activation Code

The app will navigate to the **Activation Screen**:

1. **Enter the 6-digit code** you received
2. The code auto-submits when all 6 digits are entered
3. Or click **"Verify"**

---

### Step 6: You're In! 🎉

After successful verification, you'll see the **Client Home Screen** with:
- Your profile information
- Active subscription details
- QR code for gym entry
- Entry history
- Settings

---

## 🛠️ BACKEND REQUIREMENTS

For client login to work, your backend MUST have these endpoints:

### 1. Request Activation Code
**Endpoint:** `POST /api/clients/request-activation`

**Request:**
```json
{
  "identifier": "01234567890"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Activation code sent"
}
```

**Backend Logic:**
```python
# Find customer by phone or email
customer = Customer.query.filter(
    (Customer.phone == identifier) | (Customer.email == identifier)
).first()

if not customer:
    return {"status": "error", "message": "Customer not found"}, 404

# Generate 6-digit code
import random
activation_code = f"{random.randint(100000, 999999)}"

# Save with expiration (10 minutes)
customer.activation_code = activation_code
customer.activation_code_expires = datetime.now() + timedelta(minutes=10)
db.session.commit()

# Send code (can print for testing)
print(f"Activation code for {customer.full_name}: {activation_code}")

return {"status": "success", "message": "Activation code sent"}
```

---

### 2. Verify Activation Code
**Endpoint:** `POST /api/clients/verify-activation`

**Request:**
```json
{
  "identifier": "01234567890",
  "activation_code": "123456"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Login successful",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "client": {
      "id": 123,
      "full_name": "Ahmed Hassan",
      "phone": "01234567890",
      "email": "ahmed@example.com",
      "qr_code": "GYM-123",
      "branch_name": "Dragon Club"
    }
  }
}
```

**Backend Logic:**
```python
# Find customer
customer = Customer.query.filter(
    (Customer.phone == identifier) | (Customer.email == identifier)
).first()

if not customer:
    return {"status": "error", "message": "Customer not found"}, 404

# Check code
if customer.activation_code != activation_code:
    return {"status": "error", "message": "Invalid code"}, 400

# Check expiration
if customer.activation_code_expires < datetime.now():
    return {"status": "error", "message": "Code expired"}, 400

# Generate JWT token with type: 'client'
token = create_jwt_token(customer.id, type='client')

# Clear activation code
customer.activation_code = None
customer.activation_code_expires = None
db.session.commit()

return {
    "status": "success",
    "data": {
        "access_token": token,
        "client": customer.to_dict()
    }
}
```

---

### 3. Get Client Profile
**Endpoint:** `GET /api/clients/me`

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "full_name": "Ahmed Hassan",
    "phone": "01234567890",
    "email": "ahmed@example.com",
    "qr_code": "GYM-123",
    "branch_name": "Dragon Club",
    "weight": 80,
    "height": 175,
    "bmi": 26.1,
    "active_subscription": {
      "service_name": "Monthly Gym",
      "end_date": "2026-03-11",
      "status": "active"
    }
  }
}
```

---

### 4. Get QR Code
**Endpoint:** `GET /api/clients/qr`

**Headers:**
```
Authorization: Bearer {token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "qr_code": "GYM-123",
    "qr_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expires_at": "2026-02-11T11:00:00Z"
  }
}
```

---

## 🧪 TESTING THE CLIENT APP

### Test Case 1: New Customer Login

1. **Register a test customer** (via Staff App):
   - Name: Test Client
   - Phone: `01111111111`
   - Email: `testclient@test.com`

2. **Run Client App:**
   ```bash
   flutter run -t lib/client_main.dart
   ```

3. **Enter phone:** `01111111111`

4. **Click "Request Activation Code"**

5. **Check backend logs** for the 6-digit code

6. **Enter the code** in the app

7. **Expected:** You should see the home screen with profile

---

### Test Case 2: View QR Code

1. Login as client (follow Test Case 1)
2. Tap on the **QR Code icon** in the bottom navigation
3. You should see your QR code displayed
4. This QR code is used for gym entry

---

### Test Case 3: View Subscription

1. Login as client
2. Tap on the **Subscription icon** in bottom navigation
3. You should see:
   - Active subscription (if you have one)
   - Or "No active subscription" message

---

## 🔧 TROUBLESHOOTING

### Problem: "Customer not found"
**Solution:** Make sure you're registered as a customer first via the Staff App.

### Problem: Backend returns 404
**Solution:** Backend needs to implement the client authentication endpoints.

### Problem: "Invalid code"
**Solution:** Check backend logs for the actual code generated, or check if it expired (10 min).

### Problem: App doesn't navigate after code entry
**Solution:** Check Flutter console for errors. Might be a backend response format issue.

---

## 📝 QUICK BACKEND IMPLEMENTATION

If your backend developer needs to implement these endpoints quickly, send them this:

```python
# Add to Customer model
class Customer(db.Model):
    # ...existing fields...
    activation_code = db.Column(db.String(6), nullable=True)
    activation_code_expires = db.Column(db.DateTime, nullable=True)

# Add routes
@app.route('/api/clients/request-activation', methods=['POST'])
def request_client_activation():
    identifier = request.json.get('identifier')
    customer = Customer.query.filter(
        (Customer.phone == identifier) | (Customer.email == identifier)
    ).first()
    
    if not customer:
        return jsonify({"status": "error", "message": "Customer not found"}), 404
    
    # Generate code
    import random
    code = f"{random.randint(100000, 999999)}"
    customer.activation_code = code
    customer.activation_code_expires = datetime.now() + timedelta(minutes=10)
    db.session.commit()
    
    # For testing, print to console
    print(f"🔑 Activation code for {customer.full_name}: {code}")
    
    return jsonify({"status": "success", "message": "Activation code sent"})

@app.route('/api/clients/verify-activation', methods=['POST'])
def verify_client_activation():
    identifier = request.json.get('identifier')
    code = request.json.get('activation_code')
    
    customer = Customer.query.filter(
        (Customer.phone == identifier) | (Customer.email == identifier)
    ).first()
    
    if not customer:
        return jsonify({"status": "error", "message": "Customer not found"}), 404
    
    if customer.activation_code != code:
        return jsonify({"status": "error", "message": "Invalid code"}), 400
    
    if customer.activation_code_expires < datetime.now():
        return jsonify({"status": "error", "message": "Code expired"}), 400
    
    # Generate token
    from flask_jwt_extended import create_access_token
    token = create_access_token(
        identity=customer.id,
        additional_claims={"type": "client"}
    )
    
    # Clear code
    customer.activation_code = None
    customer.activation_code_expires = None
    db.session.commit()
    
    return jsonify({
        "status": "success",
        "data": {
            "access_token": token,
            "client": {
                "id": customer.id,
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
                "qr_code": customer.qr_code,
                "branch_name": customer.branch.name if customer.branch else None
            }
        }
    })

@app.route('/api/clients/me', methods=['GET'])
@jwt_required()
def get_client_profile():
    from flask_jwt_extended import get_jwt_identity, get_jwt
    
    claims = get_jwt()
    if claims.get('type') != 'client':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({"status": "error", "message": "Customer not found"}), 404
    
    return jsonify({
        "status": "success",
        "data": {
            "id": customer.id,
            "full_name": customer.full_name,
            "phone": customer.phone,
            "email": customer.email,
            "qr_code": customer.qr_code,
            "branch_name": customer.branch.name if customer.branch else None
            # Add more fields as needed
        }
    })

@app.route('/api/clients/qr', methods=['GET'])
@jwt_required()
def get_client_qr():
    from flask_jwt_extended import get_jwt_identity, get_jwt
    
    claims = get_jwt()
    if claims.get('type') != 'client':
        return jsonify({"status": "error", "message": "Unauthorized"}), 403
    
    customer_id = get_jwt_identity()
    customer = Customer.query.get(customer_id)
    
    if not customer:
        return jsonify({"status": "error", "message": "Customer not found"}), 404
    
    return jsonify({
        "status": "success",
        "data": {
            "qr_code": customer.qr_code,
            "qr_token": customer.qr_code  # Or generate a time-limited token
        }
    })
```

---

## 🎯 SUMMARY

1. **Two separate apps:** Staff app (`main.dart`) and Client app (`client_main.dart`)
2. **Run client app:** `flutter run -t lib/client_main.dart`
3. **Login flow:** Enter phone/email → Get 6-digit code → Enter code → Login
4. **Backend needs:** 4 client endpoints (request code, verify code, get profile, get QR)
5. **Test customer:** Register via Staff App first

---

**Need help?** Check the backend logs for activation codes during testing! 🔍

