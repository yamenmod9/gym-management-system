# BACKEND SEED DATA REQUIREMENTS (seed.py)

## PURPOSE
Create comprehensive test data for the Gym Management System to enable thorough testing of all features in both Staff and Client apps.

---

## REQUIRED SEED DATA

### 1. BRANCHES (Create 4 branches)

```python
branches = [
    {
        "name": "Dragon Club",
        "address": "123 Main St, Cairo",
        "phone": "01012345678",
        "email": "dragon@gymclub.com",
        "is_active": True,
        "capacity": 100,
        "opening_time": "06:00:00",
        "closing_time": "23:00:00"
    },
    {
        "name": "Titans Gym",
        "address": "456 Fitness Ave, Giza",
        "phone": "01087654321",
        "email": "titans@gymclub.com",
        "is_active": True,
        "capacity": 150,
        "opening_time": "05:00:00",
        "closing_time": "00:00:00"
    },
    {
        "name": "Phoenix Fitness",
        "address": "789 Health Blvd, Alexandria",
        "phone": "01098765432",
        "email": "phoenix@gymclub.com",
        "is_active": True,
        "capacity": 80,
        "opening_time": "07:00:00",
        "closing_time": "22:00:00"
    },
    {
        "name": "Iron Warriors",
        "address": "321 Power St, Mansoura",
        "phone": "01056789012",
        "email": "iron@gymclub.com",
        "is_active": True,
        "capacity": 120,
        "opening_time": "06:30:00",
        "closing_time": "23:30:00"
    }
]
```

### 2. SERVICES (Create 10 services per branch)

```python
services = [
    # Subscription Types
    {"name": "Monthly Membership", "price": 500.0, "duration_months": 1, "sessions": None, "coins": None},
    {"name": "Quarterly Membership", "price": 1350.0, "duration_months": 3, "sessions": None, "coins": None},
    {"name": "Annual Membership", "price": 4800.0, "duration_months": 12, "sessions": None, "coins": None},
    
    # Session-based
    {"name": "10 Sessions Pack", "price": 300.0, "duration_months": 2, "sessions": 10, "coins": None},
    {"name": "20 Sessions Pack", "price": 550.0, "duration_months": 3, "sessions": 20, "coins": None},
    {"name": "50 Sessions Pack", "price": 1200.0, "duration_months": 6, "sessions": 50, "coins": None},
    
    # Coins-based (flexible)
    {"name": "20 Coins Pack", "price": 400.0, "duration_months": 12, "sessions": None, "coins": 20},
    {"name": "50 Coins Pack", "price": 900.0, "duration_months": 12, "sessions": None, "coins": 50},
    {"name": "100 Coins Pack", "price": 1600.0, "duration_months": 12, "sessions": None, "coins": 100},
    
    # Special
    {"name": "Student Monthly Pass", "price": 350.0, "duration_months": 1, "sessions": None, "coins": None}
]
```

### 3. USERS (Staff - Create for each branch)

**IMPORTANT**: The system has ONE owner who can see all branches, but managers/accountants/receptionists are assigned to specific branches.

```python
# Owner (1 user - sees ALL branches)
owner = {
    "full_name": "System Owner",
    "email": "owner@gymclub.com",
    "phone": "01000000001",
    "role": "owner",
    "branch_id": None,  # NULL because owner manages all branches
    "password": "owner123",  # Plain password (will be hashed)
    "is_active": True
}

# For EACH branch, create:
# 1. Branch Manager (1 per branch)
branch_managers = [
    {
        "full_name": f"{branch_name} Manager",
        "email": f"manager@{branch_name.lower().replace(' ', '')}.com",
        "phone": f"0101000000{branch_id}",
        "role": "manager",
        "branch_id": branch_id,
        "password": "manager123",
        "is_active": True
    }
]

# 2. Accountant (1 per branch)
accountants = [
    {
        "full_name": f"{branch_name} Accountant",
        "email": f"accountant@{branch_name.lower().replace(' ', '')}.com",
        "phone": f"0102000000{branch_id}",
        "role": "accountant",
        "branch_id": branch_id,
        "password": "accountant123",
        "is_active": True
    }
]

# 3. Receptionists (2-3 per branch)
receptionists = [
    {
        "full_name": f"{branch_name} Receptionist 1",
        "email": f"reception1@{branch_name.lower().replace(' ', '')}.com",
        "phone": f"0103000000{branch_id}",
        "role": "reception",
        "branch_id": branch_id,
        "password": "reception123",
        "is_active": True
    },
    {
        "full_name": f"{branch_name} Receptionist 2",
        "email": f"reception2@{branch_name.lower().replace(' ', '')}.com",
        "phone": f"0104000000{branch_id}",
        "role": "reception",
        "branch_id": branch_id,
        "password": "reception123",
        "is_active": True
    }
]
```

**Total Staff**: 1 Owner + (4 Managers + 4 Accountants + 8 Receptionists) = 17 staff members

### 4. CUSTOMERS (Create 50 per branch = 200 total)

**CRITICAL**: Each customer must have:
- `temp_password`: 6-character temporary password (e.g., "AB12CD", "XY98ZF")
- `password_changed`: False (so they're forced to change on first login)
- `password`: Hashed version of temp_password (bcrypt)
- `qr_code`: Format "GYM-{branch_id}-{customer_id}"
- `is_active`: True
- Realistic health data (height, weight, BMI, BMR, calories)

```python
import random
import string

def generate_temp_password():
    """Generate 6-character password: 2 letters + 2 digits + 2 letters"""
    letters = string.ascii_uppercase
    digits = string.digits
    return (
        random.choice(letters) + random.choice(letters) +
        random.choice(digits) + random.choice(digits) +
        random.choice(letters) + random.choice(letters)
    )

# Example customers
customers = []
for branch_id in range(1, 5):  # 4 branches
    for i in range(1, 51):  # 50 customers per branch
        temp_password = generate_temp_password()
        
        # Random but realistic data
        gender = random.choice(["male", "female"])
        height = random.uniform(1.50, 1.95)  # meters
        weight = random.uniform(50.0, 120.0)  # kg
        age = random.randint(16, 65)
        birth_year = 2026 - age
        
        # Calculate BMI
        bmi = weight / (height ** 2)
        
        # Calculate BMR (Mifflin-St Jeor Equation)
        if gender == "male":
            bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) + 5
        else:
            bmr = (10 * weight) + (6.25 * height * 100) - (5 * age) - 161
        
        # Daily calories (BMR * activity factor - assume moderate)
        daily_calories = int(bmr * 1.55)
        
        customer = {
            "full_name": f"Customer {branch_id}-{i}",
            "phone": f"010{random.randint(10000000, 99999999)}",
            "email": f"customer{branch_id}_{i}@example.com",
            "branch_id": branch_id,
            "gender": gender,
            "date_of_birth": f"{birth_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
            "height": round(height, 2),
            "weight": round(weight, 1),
            "bmi": round(bmi, 2),
            "bmr": round(bmr, 2),
            "daily_calories": daily_calories,
            "temp_password": temp_password,  # IMPORTANT: Store this!
            "password": hash_password(temp_password),  # Bcrypt hash
            "password_changed": False,  # MUST be False for first-time login
            "qr_code": f"GYM-{branch_id}-{{customer_id}}",  # Will be updated with actual ID
            "is_active": True,
            "address": f"{random.randint(1, 999)} Street, City",
            "national_id": f"{random.randint(10000000000, 99999999999)}",
            "health_notes": random.choice([None, "Diabetes", "Hypertension", "Asthma", "Previous injury"])
        }
        customers.append(customer)
```

**IMPORTANT**: After creating each customer, update their `qr_code` with the actual customer ID:
```python
customer.qr_code = f"GYM-{customer.branch_id}-{customer.id}"
customer.save()
```

### 5. SUBSCRIPTIONS (Create varied subscriptions)

Create active subscriptions for about 70% of customers:
- 30% should have coins-based subscriptions
- 40% should have session-based subscriptions
- 30% should have unlimited monthly/quarterly/annual

```python
# For each customer (70% chance):
if random.random() < 0.7:
    service = random.choice(services)
    subscription_type = "coins" if service["coins"] else "sessions" if service["sessions"] else "unlimited"
    
    start_date = datetime.now() - timedelta(days=random.randint(0, 60))
    end_date = start_date + timedelta(days=service["duration_months"] * 30)
    
    # Calculate remaining sessions/coins (random usage)
    if subscription_type == "coins":
        total = service["coins"]
        used = random.randint(0, total)
        remaining = total - used
    elif subscription_type == "sessions":
        total = service["sessions"]
        used = random.randint(0, total)
        remaining = total - used
    else:
        remaining = None
    
    subscription = {
        "customer_id": customer.id,
        "service_id": service.id,
        "branch_id": customer.branch_id,
        "type": subscription_type,
        "coins": service["coins"],
        "sessions": service["sessions"],
        "remaining_sessions": remaining,
        "status": "active" if end_date > datetime.now() and (remaining is None or remaining > 0) else "expired",
        "start_date": start_date,
        "end_date": end_date,
        "amount": service["price"],
        "payment_method": random.choice(["cash", "card", "bank_transfer"]),
        "payment_status": "paid",
        "created_at": start_date
    }
```

### 6. PAYMENTS (Create payment records)

For each subscription, create a corresponding payment:

```python
payment = {
    "customer_id": subscription.customer_id,
    "subscription_id": subscription.id,
    "branch_id": subscription.branch_id,
    "amount": subscription.amount,
    "payment_method": subscription.payment_method,
    "payment_date": subscription.start_date,
    "recorded_by": random.choice(receptionists_for_branch).id,
    "notes": f"Payment for {service.name}",
    "status": "completed"
}
```

### 7. CHECK-INS (Create historical check-ins)

For customers with active subscriptions, create 5-20 random check-ins in the past 30 days:

```python
if subscription.status == "active":
    num_checkins = random.randint(5, 20)
    for _ in range(num_checkins):
        checkin_date = datetime.now() - timedelta(days=random.randint(0, 30))
        checkin = {
            "customer_id": customer.id,
            "subscription_id": subscription.id,
            "branch_id": customer.branch_id,
            "checked_in_at": checkin_date,
            "checked_in_by": random.choice(receptionists_for_branch).id,
            "sessions_deducted": 1 if subscription.type in ["coins", "sessions"] else 0,
            "notes": "Regular check-in"
        }
```

### 8. COMPLAINTS (Create some complaints)

Create 10-20 complaints per branch:

```python
complaints = []
for branch_id in range(1, 5):
    for i in range(random.randint(10, 20)):
        customer = random.choice(customers_in_branch)
        complaint = {
            "customer_id": customer.id,
            "branch_id": branch_id,
            "title": random.choice([
                "Equipment broken",
                "Locker issue",
                "AC not working",
                "Staff behavior",
                "Cleanliness issue",
                "Class schedule problem"
            ]),
            "description": "Detailed complaint description here...",
            "status": random.choice(["pending", "in_progress", "resolved"]),
            "priority": random.choice(["low", "medium", "high"]),
            "created_at": datetime.now() - timedelta(days=random.randint(0, 30)),
            "updated_at": datetime.now() - timedelta(days=random.randint(0, 15))
        }
        complaints.append(complaint)
```

---

## SUMMARY OF SEED DATA COUNTS

- **Branches**: 4
- **Services**: 40 (10 per branch)
- **Staff**: 17 (1 owner + 16 branch staff)
- **Customers**: 200 (50 per branch)
- **Subscriptions**: ~140 (70% of customers)
- **Payments**: ~140 (one per subscription)
- **Check-ins**: ~1400-2800 (10-20 per active subscription)
- **Complaints**: 40-80 (10-20 per branch)

---

## CRITICAL REQUIREMENTS

1. **Temporary Passwords**:
   - MUST be generated for every customer
   - MUST be stored in `temp_password` field (plain text or encrypted, NOT hashed)
   - MUST set `password_changed = False` initially
   - Reception should be able to see this password after customer creation

2. **QR Codes**:
   - Format: `GYM-{branch_id}-{customer_id}`
   - Must be unique per customer
   - Must be generated on customer creation
   - Must be regenerable via API

3. **Branch Association**:
   - Every customer belongs to ONE branch
   - Every subscription belongs to the same branch as the customer
   - Staff (except owner) belong to ONE branch
   - Owner has `branch_id = NULL` and can access all branches

4. **Active Subscriptions**:
   - About 70% of customers should have active subscriptions
   - Mix of types: coins (30%), sessions (40%), unlimited (30%)
   - Some should be near expiry for testing
   - Some should have low remaining sessions for testing

5. **Realistic Data**:
   - Phone numbers must be unique and valid Egyptian format (11 digits, starts with 010/011/012/015)
   - Email addresses must be unique
   - BMI, BMR, and calorie calculations must be accurate
   - Ages between 16-65
   - Heights between 1.50-1.95m
   - Weights between 50-120kg

6. **Test Credentials Output**:
   After seeding, print a summary file with:
   - All staff credentials (email + password)
   - Sample customer credentials (phone + temp_password) - at least 10 from each branch
   - Branch IDs and names
   - Service IDs and names

---

## EXAMPLE OUTPUT FILE: test_credentials.txt

```
=== GYM MANAGEMENT SYSTEM - TEST CREDENTIALS ===

OWNER:
Email: owner@gymclub.com
Password: owner123
Access: ALL BRANCHES

BRANCH 1: Dragon Club (ID: 1)
Manager: manager@dragonclub.com | manager123
Accountant: accountant@dragonclub.com | accountant123
Reception1: reception1@dragonclub.com | reception123
Reception2: reception2@dragonclub.com | reception123

Sample Customers (Branch 1):
Phone: 01077827638 | Temp Password: RX04AF | Name: Ahmed Hassan
Phone: 01022981052 | Temp Password: SI19IC | Name: Mohamed Ali
Phone: 01041244663 | Temp Password: PS02HC | Name: Sarah Ahmed
[... 7 more ...]

BRANCH 2: Titans Gym (ID: 2)
[... similar structure ...]

[... etc for all branches ...]
```

