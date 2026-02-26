# 🚨 COMPLETE BACKEND FIX PROMPT - February 16, 2026

## CRITICAL BACKEND ISSUES TO FIX

### Issue 1: QR Code Regeneration - 404 Error
**Problem:** When receptionist clicks "Regenerate" button for customer QR code, backend returns 404.

**Current Endpoint Being Called:**
```
POST /api/customers/{customer_id}/regenerate-qr
```

**What Backend Needs to Do:**
```python
@app.post("/api/customers/{customer_id}/regenerate-qr")
def regenerate_qr_code(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Regenerate QR code for customer"""
    try:
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Customer not found"}
            )
        
        # Generate new QR code
        import secrets
        new_qr_code = f"GYM-{customer_id}-{secrets.token_hex(4).upper()}"
        
        customer.qr_code = new_qr_code
        db.commit()
        
        return {
            "success": True,
            "message": "QR code regenerated successfully",
            "qr_code": new_qr_code
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

---

### Issue 2: Check-In Endpoint - Resource Not Found
**Problem:** When receptionist scans QR and tries to check in customer, backend returns "resource not found".

**Current Endpoint Being Called:**
```
POST /api/attendance
```

**Request Body:**
```json
{
  "customer_id": 115,
  "check_in_time": "2026-02-16T10:30:00Z",
  "action": "check_in_only"
}
```

**What Backend Needs to Do:**
```python
@app.post("/api/attendance")
def record_attendance(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Record customer check-in"""
    try:
        customer_id = data.get('customer_id')
        check_in_time = data.get('check_in_time')
        action = data.get('action', 'check_in_only')
        subscription_id = data.get('subscription_id')
        
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Customer not found"}
            )
        
        if not customer.is_active:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Customer account is inactive"}
            )
        
        # Create attendance record
        attendance = Attendance(
            customer_id=customer_id,
            branch_id=current_user.branch_id,
            check_in_time=datetime.now(),
            action=action,
            subscription_id=subscription_id
        )
        
        db.add(attendance)
        db.commit()
        db.refresh(attendance)
        
        return {
            "success": True,
            "message": "Check-in recorded successfully",
            "data": {
                "attendance_id": attendance.id,
                "customer_id": customer_id,
                "customer_name": customer.full_name,
                "check_in_time": attendance.check_in_time.isoformat(),
                "branch_id": current_user.branch_id
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

**Note:** If you don't have an `Attendance` model, create one:
```python
class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    check_in_time = Column(DateTime, default=datetime.now)
    action = Column(String)  # 'check_in_only' or 'check_in_with_deduction'
    created_at = Column(DateTime, default=datetime.now)
    
    customer = relationship("Customer", back_populates="attendance_records")
```

---

### Issue 3: Temporary Password Not Showing in Customer List
**Problem:** When receptionist views customer list, `temp_password` field shows `null` despite having seeded data.

**Current Endpoint Being Called:**
```
GET /api/customers?branch_id=1
```

**What Backend MUST Return:**
```json
{
  "data": {
    "items": [
      {
        "id": 1,
        "full_name": "Mohamed Salem",
        "phone": "01077827638",
        "email": "customer1@example.com",
        "branch_id": 1,
        "temp_password": "RX04AF",  ← MUST BE INCLUDED
        "password_changed": false,   ← MUST BE INCLUDED
        "qr_code": "GYM-1-ABC123",
        "is_active": true,
        ...
      }
    ]
  }
}
```

**Fix in Backend:**
```python
@app.get("/api/customers")
def get_customers(
    branch_id: Optional[int] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Get all customers with temp passwords"""
    try:
        query = db.query(Customer)
        
        # Filter by branch if not owner
        if current_user.role != "owner" and branch_id:
            query = query.filter(Customer.branch_id == branch_id)
        
        customers = query.all()
        
        # IMPORTANT: Include temp_password in response
        customer_list = []
        for customer in customers:
            customer_dict = {
                "id": customer.id,
                "full_name": customer.full_name,
                "phone": customer.phone,
                "email": customer.email,
                "branch_id": customer.branch_id,
                "qr_code": customer.qr_code,
                "is_active": customer.is_active,
                "temp_password": customer.temp_password,  # ← INCLUDE THIS
                "password_changed": customer.password_changed if hasattr(customer, 'password_changed') else False,
                "height": customer.height,
                "weight": customer.weight,
                "bmi": customer.bmi,
                "date_of_birth": customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                "gender": str(customer.gender) if customer.gender else None,
                "address": customer.address,
                "national_id": customer.national_id,
                "health_notes": customer.health_notes,
                "created_at": customer.created_at.isoformat() if customer.created_at else None,
            }
            customer_list.append(customer_dict)
        
        return {
            "success": True,
            "data": {
                "items": customer_list,
                "total": len(customer_list)
            }
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

---

### Issue 4: Subscription Activation - Branch Mismatch (ALREADY FIXED IN FLUTTER)
**Status:** Flutter app now correctly fetches customer's branch_id before activating subscription.

**What Backend Should Validate:**
```python
@app.post("/api/subscriptions/activate")
def activate_subscription(
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Activate subscription for customer"""
    try:
        customer_id = data.get('customer_id')
        service_id = data.get('service_id')
        branch_id = data.get('branch_id')  # Now correctly uses customer's branch
        amount = data.get('amount')
        payment_method = data.get('payment_method')
        
        # Verify customer exists
        customer = db.query(Customer).filter(Customer.id == customer_id).first()
        if not customer:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Customer not found"}
            )
        
        # Validate that provided branch_id matches customer's branch
        if customer.branch_id != branch_id:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Branch mismatch"}
            )
        
        # Check for existing active subscription
        existing_sub = db.query(Subscription).filter(
            Subscription.customer_id == customer_id,
            Subscription.status == "active"
        ).first()
        
        if existing_sub:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Customer already has an active subscription"}
            )
        
        # Get service details
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Service not found"}
            )
        
        # Calculate dates based on subscription type
        start_date = datetime.now().date()
        
        if data.get('subscription_type') == 'coins':
            # Coins package - set expiry based on validity_months
            validity_months = data.get('validity_months', 12)
            end_date = start_date + timedelta(days=validity_months * 30)
            remaining_sessions = data.get('coins', 0)
        elif data.get('subscription_type') == 'sessions':
            # Session package
            validity_months = data.get('validity_months', 1)
            end_date = start_date + timedelta(days=validity_months * 30)
            remaining_sessions = data.get('sessions', 0)
        else:
            # Monthly subscription
            duration_months = service.duration_months or 1
            end_date = start_date + timedelta(days=duration_months * 30)
            remaining_sessions = None
        
        # Create subscription
        subscription = Subscription(
            customer_id=customer_id,
            service_id=service_id,
            branch_id=branch_id,
            start_date=start_date,
            end_date=end_date,
            status="active",
            amount=amount,
            payment_method=payment_method,
            remaining_sessions=remaining_sessions,
            subscription_type=data.get('subscription_type', 'monthly')
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        return {
            "success": True,
            "message": "Subscription activated successfully",
            "data": {
                "subscription_id": subscription.id,
                "customer_id": customer_id,
                "customer_name": customer.full_name,
                "service_id": service_id,
                "service_name": service.name,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "status": "active",
                "amount": amount,
                "remaining_sessions": remaining_sessions
            }
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

---

### Issue 5: Session/Coin Deduction for QR Check-In
**Problem:** When receptionist scans QR and clicks "Deduct 1 Session", backend needs to update subscription.

**Current Endpoint Being Called:**
```
POST /api/subscriptions/{subscription_id}/deduct
```

**What Backend Needs to Do:**
```python
@app.post("/api/subscriptions/{subscription_id}/deduct")
def deduct_session(
    subscription_id: int,
    data: dict,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_staff)
):
    """Deduct one session/coin from subscription"""
    try:
        subscription = db.query(Subscription).filter(
            Subscription.id == subscription_id
        ).first()
        
        if not subscription:
            return JSONResponse(
                status_code=404,
                content={"success": False, "error": "Subscription not found"}
            )
        
        if subscription.status != "active":
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "Subscription is not active"}
            )
        
        # Check if subscription has sessions/coins
        if subscription.remaining_sessions is None or subscription.remaining_sessions <= 0:
            return JSONResponse(
                status_code=400,
                content={"success": False, "error": "No sessions/coins remaining"}
            )
        
        # Deduct 1 session/coin
        subscription.remaining_sessions -= 1
        
        # If no sessions left, mark as expired
        if subscription.remaining_sessions == 0:
            subscription.status = "expired"
        
        db.commit()
        db.refresh(subscription)
        
        # Also create attendance record
        attendance = Attendance(
            customer_id=subscription.customer_id,
            branch_id=current_user.branch_id,
            subscription_id=subscription_id,
            check_in_time=datetime.now(),
            action="check_in_with_deduction"
        )
        db.add(attendance)
        db.commit()
        
        return {
            "success": True,
            "message": "Session deducted successfully",
            "data": {
                "subscription_id": subscription_id,
                "remaining_sessions": subscription.remaining_sessions,
                "status": subscription.status
            }
        }
    except Exception as e:
        db.rollback()
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": str(e)}
        )
```

---

## DATABASE SCHEMA UPDATES REQUIRED

### 1. Add temp_password and password_changed to Customer Model
```python
class Customer(Base):
    __tablename__ = "customers"
    
    # ...existing fields...
    
    temp_password = Column(String(6), nullable=True)  # 6-character temp password
    password_changed = Column(Boolean, default=False)  # Has customer changed password?
```

### 2. Create Attendance Model (if not exists)
```python
class Attendance(Base):
    __tablename__ = "attendance"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    branch_id = Column(Integer, ForeignKey("branches.id"))
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    check_in_time = Column(DateTime, default=datetime.now)
    action = Column(String)  # 'check_in_only' or 'check_in_with_deduction'
    created_at = Column(DateTime, default=datetime.now)
```

### 3. Update Subscription Model to Include remaining_sessions
```python
class Subscription(Base):
    __tablename__ = "subscriptions"
    
    # ...existing fields...
    
    remaining_sessions = Column(Integer, nullable=True)  # For coins/session packages
    subscription_type = Column(String)  # 'monthly', 'coins', 'sessions'
```

---

## SEED DATA UPDATES REQUIRED

### Update seed.py to Include Temporary Passwords
```python
import random
import string

def generate_temp_password():
    """Generate 6-character password in format: AB12CD"""
    letters = ''.join(random.choices(string.ascii_uppercase, k=2))
    numbers = ''.join(random.choices(string.digits, k=2))
    letters2 = ''.join(random.choices(string.ascii_uppercase, k=2))
    return f"{letters}{numbers}{letters2}"

# When creating customers:
for i in range(1, 151):
    temp_pwd = generate_temp_password()
    customer = Customer(
        full_name=f"Customer {i}",
        phone=f"0107782{i:04d}",
        email=f"customer{i}@example.com",
        password=hash_password(temp_pwd),  # Hash the temp password
        temp_password=temp_pwd,  # Store plain text for receptionist to see
        password_changed=False,  # Customer hasn't changed it yet
        branch_id=((i - 1) % 3) + 1,  # Distribute across 3 branches
        # ...other fields...
    )
    db.add(customer)
```

### Sample Seed Data for Testing
Create these 5 customers with known temp passwords:

| Customer ID | Name | Phone | Temp Password | Branch |
|-------------|------|-------|---------------|--------|
| 1 | Mohamed Salem | 01077827638 | RX04AF | 1 |
| 2 | Layla Rashad | 01022981052 | SI19IC | 1 |
| 3 | Ibrahim Hassan | 01041244663 | PS02HC | 1 |
| 4 | Hadeer Youssef | 01095899313 | PE71JZ | 2 |
| 5 | Somaya Hassan | 01085345555 | RK94GG | 2 |

---

## TESTING CHECKLIST

After implementing these fixes, test in this order:

### Test 1: Temporary Password Display ✅
1. Login as receptionist
2. Go to Clients tab
3. Click any customer
4. **Expected:** See orange "Temporary Password" card with 6-character code (e.g., "RX04AF")

### Test 2: QR Code Regeneration ✅
1. In customer detail screen
2. Click "Regenerate" button
3. **Expected:** 
   - Success message appears
   - QR code updates immediately
   - No 404 error

### Test 3: QR Code Scanning ✅
1. Tap "Scan Customer QR Code"
2. Scan a customer's QR code
3. **Expected:**
   - Customer details appear
   - Shows subscription status
   - Shows "Deduct 1 Session" and "Check-In Only" buttons

### Test 4: Check-In Only ✅
1. After scanning QR
2. Click "Check-In Only"
3. **Expected:**
   - Success message: "Customer checked in successfully"
   - No "resource not found" error

### Test 5: Deduct Session ✅
1. Scan customer with active subscription (coins/sessions)
2. Click "Deduct 1 Session"
3. **Expected:**
   - Success message with remaining count
   - Subscription updated in database

### Test 6: Subscription Activation ✅
1. Click "Activate Subscription"
2. Select customer from different branch
3. Fill form and submit
4. **Expected:**
   - Success! No "branch mismatch" error
   - Subscription created with customer's branch_id

---

## SUMMARY OF REQUIRED BACKEND ENDPOINTS

| Endpoint | Method | Status | Priority |
|----------|--------|--------|----------|
| `/api/customers/{id}/regenerate-qr` | POST | ❌ Missing | HIGH |
| `/api/attendance` | POST | ❌ Broken | HIGH |
| `/api/customers` | GET | ⚠️ Missing temp_password | HIGH |
| `/api/subscriptions/activate` | POST | ✅ Working | DONE |
| `/api/subscriptions/{id}/deduct` | POST | ❌ Missing | HIGH |

---

## FILES TO MODIFY IN BACKEND

1. **models.py** - Add temp_password, password_changed, Attendance model
2. **routes/customers.py** - Add regenerate-qr endpoint, update GET to include temp_password
3. **routes/attendance.py** - Add POST attendance endpoint
4. **routes/subscriptions.py** - Add deduct endpoint, update activate validation
5. **seed.py** - Generate temp passwords for all customers

---

## READY TO IMPLEMENT? 🚀

Copy this entire prompt and give it to your backend developer or Claude Sonnet to implement all fixes at once!

**Expected Time:** 1-2 hours  
**Testing Time:** 30 minutes  
**Total:** Ready in < 3 hours!

---

**Status:** 📋 DOCUMENTED - Ready for Implementation  
**Date:** February 16, 2026  
**Priority:** 🔥 URGENT - Blocking QR scanning workflow

