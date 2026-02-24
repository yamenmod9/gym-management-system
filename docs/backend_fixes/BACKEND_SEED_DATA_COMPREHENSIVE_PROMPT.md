# 🌱 COMPREHENSIVE SEED DATA GUIDE FOR GYM MANAGEMENT SYSTEM

**Date:** February 14, 2026  
**For:** Claude Sonnet 4.5  
**Purpose:** Complete seed.py data requirements for thorough Flutter app testing

---

## 📋 TABLE OF CONTENTS

1. [Database Schema Requirements](#database-schema-requirements)
2. [Seed Data Overview](#seed-data-overview)
3. [Detailed Seed Data by Table](#detailed-seed-data-by-table)
4. [Test Scenarios Coverage](#test-scenarios-coverage)
5. [Validation Checklist](#validation-checklist)

---

## 🗄️ DATABASE SCHEMA REQUIREMENTS

### Core Tables Needed

1. **users** - Staff accounts (owner, managers, receptionists, accountants)
2. **branches** - Gym branch locations
3. **customers** - Gym members/clients
4. **services** - Subscription types (monthly, 3-month, etc.)
5. **subscriptions** - Customer subscription records
6. **payments** - Payment transactions
7. **entry_logs** - Customer check-in records (QR scans)
8. **complaints** - Customer complaints
9. **expenses** - Branch expenses
10. **attendance** - Staff attendance records
11. **cash_differences** - Daily closing cash differences

---

## 📊 SEED DATA OVERVIEW

### Summary Statistics

| Entity | Count | Purpose |
|--------|-------|---------|
| Branches | 3 | Test multi-branch features |
| Services | 6 | Various subscription types |
| Staff Users | 14 | All role types covered |
| Customers | 150 | Realistic dataset size |
| Active Subscriptions | 83 | ~55% active rate |
| Expired Subscriptions | 45 | Test renewal prompts |
| Frozen Subscriptions | 8 | Test freeze/unfreeze |
| Payments | 245 | Transaction history |
| Entry Logs | 3,500+ | Check-in history |
| Complaints | 50 | 11 open, 39 resolved |
| Expenses | 45 | 10 pending, 35 approved |
| Attendance Records | 280 | 1 month per staff |

**Total Revenue:** ~164,521 EGP

---

## 🏢 DETAILED SEED DATA BY TABLE

### 1. BRANCHES (3 records)

```python
branches = [
    {
        "id": 1,
        "name": "Dragon Club",
        "location": "Nasr City, Cairo",
        "address": "123 Street, Nasr City, Cairo",
        "phone": "01012345678",
        "email": "dragon@gym.com",
        "is_active": True,
        "opening_hour": "06:00:00",
        "closing_hour": "23:00:00",
        "created_at": datetime(2025, 1, 1)
    },
    {
        "id": 2,
        "name": "Phoenix Fitness",
        "location": "Maadi, Cairo",
        "address": "456 Road, Maadi, Cairo",
        "phone": "01023456789",
        "email": "phoenix@gym.com",
        "is_active": True,
        "opening_hour": "06:00:00",
        "closing_hour": "23:00:00",
        "created_at": datetime(2025, 1, 1)
    },
    {
        "id": 3,
        "name": "Tiger Gym",
        "location": "Heliopolis, Cairo",
        "address": "789 Avenue, Heliopolis, Cairo",
        "phone": "01034567890",
        "email": "tiger@gym.com",
        "is_active": True,
        "opening_hour": "06:00:00",
        "closing_hour": "22:00:00",
        "created_at": datetime(2025, 1, 1)
    }
]
```

**Distribution:**
- Dragon Club: 60 customers (40% of total) - Best performing
- Phoenix Fitness: 55 customers (37% of total)
- Tiger Gym: 35 customers (23% of total) - Highest complaints

---

### 2. SERVICES (6 records)

```python
services = [
    {
        "id": 1,
        "name": "Monthly Gym",
        "description": "Full gym access for 1 month with all equipment",
        "price": 500.0,
        "duration_days": 30,
        "service_type": "gym",
        "total_coins": 30,  # 1 coin per day
        "freeze_days_allowed": 5,
        "is_active": True
    },
    {
        "id": 2,
        "name": "3-Month Gym",
        "description": "Full gym access for 3 months - Save 10%",
        "price": 1350.0,  # 450 per month
        "duration_days": 90,
        "service_type": "gym",
        "total_coins": 90,
        "freeze_days_allowed": 15,
        "is_active": True
    },
    {
        "id": 3,
        "name": "6-Month Gym",
        "description": "Full gym access for 6 months - Save 15%",
        "price": 2550.0,  # 425 per month
        "duration_days": 180,
        "service_type": "gym",
        "total_coins": 180,
        "freeze_days_allowed": 30,
        "is_active": True
    },
    {
        "id": 4,
        "name": "Personal Training - 8 Sessions",
        "description": "8 one-hour personal training sessions",
        "price": 800.0,  # 100 per session
        "duration_days": 30,
        "service_type": "training",
        "total_coins": 8,
        "freeze_days_allowed": 5,
        "is_active": True
    },
    {
        "id": 5,
        "name": "Personal Training - 16 Sessions",
        "description": "16 one-hour personal training sessions - Save 10%",
        "price": 1440.0,  # 90 per session
        "duration_days": 60,
        "service_type": "training",
        "total_coins": 16,
        "freeze_days_allowed": 10,
        "is_active": True
    },
    {
        "id": 6,
        "name": "Day Pass",
        "description": "Single day gym access",
        "price": 50.0,
        "duration_days": 1,
        "service_type": "day_pass",
        "total_coins": 1,
        "freeze_days_allowed": 0,
        "is_active": True
    }
]
```

**Pricing Strategy:**
- Monthly: 500 EGP (base price)
- 3-Month: 1,350 EGP (10% discount)
- 6-Month: 2,550 EGP (15% discount)
- Personal Training: Premium pricing
- Day Pass: For walk-ins

---

### 3. USERS (14 staff records)

#### Owner (1 user)

```python
{
    "id": 1,
    "username": "owner",
    "password": hash("owner123"),  # Use bcrypt or werkzeug.security
    "role": "owner",
    "branch_id": None,  # Access to all branches
    "full_name": "System Owner",
    "email": "owner@gym.com",
    "phone": "01000000001",
    "is_active": True,
    "created_at": datetime(2025, 1, 1)
}
```

#### Branch Managers (3 users - 1 per branch)

```python
managers = [
    {
        "id": 2,
        "username": "manager_dragon",
        "password": hash("manager123"),
        "role": "branch_manager",
        "branch_id": 1,
        "full_name": "Dragon Manager",
        "email": "manager.dragon@gym.com",
        "phone": "01000000002",
        "is_active": True
    },
    {
        "id": 3,
        "username": "manager_phoenix",
        "password": hash("manager123"),
        "role": "branch_manager",
        "branch_id": 2,
        "full_name": "Phoenix Manager",
        "email": "manager.phoenix@gym.com",
        "phone": "01000000003",
        "is_active": True
    },
    {
        "id": 4,
        "username": "manager_tiger",
        "password": hash("manager123"),
        "role": "branch_manager",
        "branch_id": 3,
        "full_name": "Tiger Manager",
        "email": "manager.tiger@gym.com",
        "phone": "01000000004",
        "is_active": True
    }
]
```

#### Receptionists (6 users - 2 per branch)

```python
receptionists = [
    # Dragon Club (2)
    {
        "id": 5,
        "username": "reception_dragon_1",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 1,
        "full_name": "Dragon Reception 1",
        "email": "reception1.dragon@gym.com",
        "phone": "01000000005",
        "is_active": True
    },
    {
        "id": 6,
        "username": "reception_dragon_2",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 1,
        "full_name": "Dragon Reception 2",
        "email": "reception2.dragon@gym.com",
        "phone": "01000000006",
        "is_active": True
    },
    # Phoenix Fitness (2)
    {
        "id": 7,
        "username": "reception_phoenix_1",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 2,
        "full_name": "Phoenix Reception 1",
        "email": "reception1.phoenix@gym.com",
        "phone": "01000000007",
        "is_active": True
    },
    {
        "id": 8,
        "username": "reception_phoenix_2",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 2,
        "full_name": "Phoenix Reception 2",
        "email": "reception2.phoenix@gym.com",
        "phone": "01000000008",
        "is_active": True
    },
    # Tiger Gym (2)
    {
        "id": 9,
        "username": "reception_tiger_1",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 3,
        "full_name": "Tiger Reception 1",
        "email": "reception1.tiger@gym.com",
        "phone": "01000000009",
        "is_active": True
    },
    {
        "id": 10,
        "username": "reception_tiger_2",
        "password": hash("reception123"),
        "role": "front_desk",
        "branch_id": 3,
        "full_name": "Tiger Reception 2",
        "email": "reception2.tiger@gym.com",
        "phone": "01000000010",
        "is_active": True
    }
]
```

#### Accountants (4 users)

```python
accountants = [
    # Central Accountants (2) - Access all branches
    {
        "id": 11,
        "username": "accountant_central_1",
        "password": hash("accountant123"),
        "role": "central_accountant",
        "branch_id": None,  # All branches
        "full_name": "Central Accountant 1",
        "email": "accountant1@gym.com",
        "phone": "01000000011",
        "is_active": True
    },
    {
        "id": 12,
        "username": "accountant_central_2",
        "password": hash("accountant123"),
        "role": "central_accountant",
        "branch_id": None,  # All branches
        "full_name": "Central Accountant 2",
        "email": "accountant2@gym.com",
        "phone": "01000000012",
        "is_active": True
    },
    # Branch Accountants (2)
    {
        "id": 13,
        "username": "accountant_dragon",
        "password": hash("accountant123"),
        "role": "branch_accountant",
        "branch_id": 1,
        "full_name": "Dragon Accountant",
        "email": "accountant.dragon@gym.com",
        "phone": "01000000013",
        "is_active": True
    },
    {
        "id": 14,
        "username": "accountant_phoenix",
        "password": hash("accountant123"),
        "role": "branch_accountant",
        "branch_id": 2,
        "full_name": "Phoenix Accountant",
        "email": "accountant.phoenix@gym.com",
        "phone": "01000000014",
        "is_active": True
    }
]
```

---

### 4. CUSTOMERS (150 records)

**Distribution by Branch:**
- Dragon Club (branch_id=1): 60 customers
- Phoenix Fitness (branch_id=2): 55 customers
- Tiger Gym (branch_id=3): 35 customers

**Customer Template:**

```python
def generate_customer(id, branch_id, name, phone, email=None, has_subscription=True):
    """
    Generate customer with realistic health metrics
    """
    # Randomize health data
    weight = random.uniform(60, 100)  # kg
    height = random.uniform(1.60, 1.90)  # meters
    bmi = weight / (height ** 2)
    
    # Calculate BMI category
    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"
    
    # Calculate ideal weight (using BMI of 22)
    ideal_weight = 22 * (height ** 2)
    
    # Calculate daily calories
    age = random.randint(18, 50)
    if gender == "male":
        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * (height * 100) - 5 * age - 161
    daily_calories = int(bmr * 1.55)  # Moderate activity
    
    return {
        "id": id,
        "full_name": name,
        "phone": phone,
        "email": email or f"customer{id}@gmail.com",
        "qr_code": f"GYM-{id}",
        "branch_id": branch_id,
        "weight": round(weight, 1),
        "height": round(height, 2),
        "bmi": round(bmi, 2),
        "bmi_category": bmi_category,
        "ideal_weight": round(ideal_weight, 1),
        "daily_calories": daily_calories,
        "date_of_birth": f"{random.randint(1975, 2005)}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
        "gender": random.choice(["male", "female"]),
        "address": f"Address {id}, Cairo, Egypt",
        "national_id": f"2{random.randint(90, 99)}{random.randint(0,1)}{random.randint(1,12):02d}{random.randint(1,28):02d}0{random.randint(100000,999999)}",
        "health_notes": None,
        "is_active": True,
        "password_hash": hash("client123"),  # Default password for client app
        "created_at": datetime(2025, random.randint(1, 12), random.randint(1, 28)),
        "updated_at": datetime.now()
    }
```

**Sample Customers (150 total):**

```python
# Dragon Club - 60 customers
dragon_customers = [
    generate_customer(1, 1, "Ahmed Hassan", "01001234567"),
    generate_customer(2, 1, "Mohamed Ali", "01001234568"),
    generate_customer(3, 1, "Sara Ibrahim", "01001234569"),
    # ... continue to 60
]

# Phoenix Fitness - 55 customers
phoenix_customers = [
    generate_customer(61, 2, "Fatma Ahmed", "01002345678"),
    generate_customer(62, 2, "Omar Khaled", "01002345679"),
    # ... continue to 115
]

# Tiger Gym - 35 customers
tiger_customers = [
    generate_customer(116, 3, "Nour Mohamed", "01003456789"),
    generate_customer(117, 3, "Hassan Ali", "01003456790"),
    # ... continue to 150
]
```

**Important Note:**
- Customer ID becomes their QR code: `GYM-{id}`
- Example: Customer ID 151 → QR code "GYM-151"
- Phone numbers must be unique (10-11 digits)
- Emails must be unique

---

### 5. SUBSCRIPTIONS (136 total records)

**Status Distribution:**
- Active: 83 (61%)
- Expired: 45 (33%)
- Frozen: 8 (6%)

**Subscription Template:**

```python
def create_subscription(customer_id, service_id, branch_id, status="active", days_offset=0):
    """
    Create subscription with calculated dates
    """
    service = services[service_id - 1]
    start_date = datetime.now() - timedelta(days=days_offset)
    end_date = start_date + timedelta(days=service["duration_days"])
    
    # Calculate remaining days and coins
    if status == "active":
        remaining_days = max(0, (end_date - datetime.now()).days)
        # Coins decrease as subscription is used
        coins_used = random.randint(0, service["total_coins"] // 2)
        remaining_coins = service["total_coins"] - coins_used
    elif status == "expired":
        remaining_days = 0
        remaining_coins = 0
    elif status == "frozen":
        remaining_days = (end_date - datetime.now()).days
        remaining_coins = service["total_coins"] - random.randint(0, 5)
    
    return {
        "customer_id": customer_id,
        "service_id": service_id,
        "branch_id": branch_id,
        "start_date": start_date.date(),
        "end_date": end_date.date(),
        "original_end_date": end_date.date(),
        "status": status,
        "remaining_days": remaining_days,
        "remaining_coins": remaining_coins,
        "total_coins": service["total_coins"],
        "freeze_days_used": random.randint(0, 2) if status == "frozen" else 0,
        "freeze_days_allowed": service["freeze_days_allowed"],
        "amount": service["price"],
        "discount": random.choice([0, 50, 100]),
        "notes": None,
        "created_at": start_date,
        "created_by_id": random.randint(5, 10),  # Random receptionist
    }
```

**Examples:**

```python
subscriptions = [
    # Active subscriptions (83)
    # Expiring TODAY (2) - for smart alerts
    create_subscription(1, 1, 1, "active", days_offset=29),  # Expires today
    create_subscription(2, 1, 1, "active", days_offset=29),  # Expires today
    
    # Expiring in 7 days (11) - for alerts
    create_subscription(3, 1, 1, "active", days_offset=23),  # Expires in 7 days
    create_subscription(4, 1, 1, "active", days_offset=23),
    # ... 9 more
    
    # Low coins (8) - for alerts (less than 3 coins)
    {**create_subscription(13, 1, 1, "active", days_offset=15), "remaining_coins": 2},
    {**create_subscription(14, 1, 1, "active", days_offset=18), "remaining_coins": 1},
    # ... 6 more
    
    # Normal active subscriptions (62)
    create_subscription(20, 1, 1, "active", days_offset=5),
    create_subscription(21, 2, 1, "active", days_offset=10),
    create_subscription(22, 3, 1, "active", days_offset=20),
    # ... continue
    
    # Expired subscriptions (45) - for renewal prompts
    create_subscription(100, 1, 1, "expired", days_offset=60),
    create_subscription(101, 1, 2, "expired", days_offset=45),
    # ... continue
    
    # Frozen subscriptions (8)
    {**create_subscription(130, 1, 1, "active", days_offset=10), "status": "frozen"},
    # ... 7 more
]
```

**Subscription Distribution by Branch:**
- Dragon Club: 40 active, 15 expired, 3 frozen = 58 total
- Phoenix Fitness: 35 active, 20 expired, 3 frozen = 58 total
- Tiger Gym: 8 active, 10 expired, 2 frozen = 20 total

**Subscription Distribution by Service:**
- Monthly Gym (ID 1): 60 subscriptions
- 3-Month Gym (ID 2): 45 subscriptions
- 6-Month Gym (ID 3): 20 subscriptions
- Personal Training 8 (ID 4): 8 subscriptions
- Personal Training 16 (ID 5): 2 subscriptions
- Day Pass (ID 6): 1 subscription

---

### 6. PAYMENTS (245 records)

**Payment Methods Distribution:**
- Cash: 73% (180 payments)
- Card: 22% (54 payments)
- Online: 5% (11 payments)

**Payment Template:**

```python
def create_payment(subscription, payment_number):
    """
    Create payment record for subscription
    """
    payment_methods = ["cash"] * 73 + ["card"] * 22 + ["online"] * 5
    payment_method = random.choice(payment_methods)
    
    # Generate receipt number
    payment_date = subscription["created_at"]
    receipt_number = f"RCP-{payment_date.strftime('%Y%m%d')}-{payment_number:03d}"
    
    return {
        "subscription_id": subscription["id"],
        "amount": subscription["amount"],
        "discount": subscription["discount"],
        "payment_method": payment_method,
        "payment_date": payment_date,
        "receipt_number": receipt_number,
        "notes": None,
        "processed_by_id": subscription["created_by_id"],
        "created_at": payment_date
    }
```

**Total Revenue Calculation:**
```python
# Dragon Club: 65,000 EGP
# Phoenix Fitness: 58,000 EGP
# Tiger Gym: 41,521 EGP
# TOTAL: 164,521 EGP
```

---

### 7. ENTRY LOGS (3,500+ records)

**Purpose:** Track customer check-ins via QR scanning

**Entry Template:**

```python
def create_entry_log(customer_id, subscription_id, branch_id, days_ago):
    """
    Create entry log for customer check-in
    """
    entry_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(6, 22))
    
    return {
        "customer_id": customer_id,
        "subscription_id": subscription_id,
        "branch_id": branch_id,
        "entry_time": entry_time,
        "entry_type": "qr_scan",
        "coins_used": 1,
        "notes": None,
        "created_at": entry_time
    }
```

**Generation Strategy:**

```python
entry_logs = []
entry_id = 1

# For each active subscription, create entry logs
for subscription in active_subscriptions:
    customer_id = subscription["customer_id"]
    # Average 25 visits per month for monthly subscriptions
    num_entries = random.randint(15, 30)
    
    for i in range(num_entries):
        days_ago = random.randint(0, 30)
        entry_logs.append({
            "id": entry_id,
            **create_entry_log(customer_id, subscription["id"], subscription["branch_id"], days_ago)
        })
        entry_id += 1

# Total entries: ~83 active * 25 avg visits = ~2,075 entries
# Add historical entries from expired subscriptions: +1,500
# TOTAL: ~3,500 entries
```

**Distribution:**
- Dragon Club: ~1,500 entries (40 active customers * 25 visits)
- Phoenix Fitness: ~1,300 entries (35 active customers * 25 visits)
- Tiger Gym: ~700 entries (8 active customers * 25 visits + historical)

---

### 8. COMPLAINTS (50 records)

**Status Distribution:**
- Open: 11 (22%)
- Resolved: 39 (78%)

**Categories:**
- equipment (40%)
- cleanliness (25%)
- staff (15%)
- facility (10%)
- other (10%)

**Priority:**
- high: 15%
- medium: 60%
- low: 25%

**Complaint Template:**

```python
complaints = [
    # Dragon Club - 12 complaints (1 open)
    {
        "id": 1,
        "customer_id": 1,
        "branch_id": 1,
        "category": "equipment",
        "priority": "high",
        "status": "open",
        "description": "Treadmill #3 not working properly",
        "submitted_at": datetime.now() - timedelta(days=2),
        "resolved_at": None,
        "resolution_notes": None,
        "submitted_by_id": 5
    },
    {
        "id": 2,
        "customer_id": 3,
        "branch_id": 1,
        "category": "cleanliness",
        "priority": "medium",
        "status": "resolved",
        "description": "Locker room needs cleaning",
        "submitted_at": datetime.now() - timedelta(days=10),
        "resolved_at": datetime.now() - timedelta(days=9),
        "resolution_notes": "Cleaning schedule updated, issue resolved",
        "submitted_by_id": 5
    },
    # ... 10 more for Dragon Club
    
    # Phoenix Fitness - 16 complaints (0 open, all resolved)
    {
        "id": 13,
        "customer_id": 61,
        "branch_id": 2,
        "category": "facility",
        "priority": "medium",
        "status": "resolved",
        "description": "AC not cooling properly",
        "submitted_at": datetime.now() - timedelta(days=15),
        "resolved_at": datetime.now() - timedelta(days=13),
        "resolution_notes": "AC serviced and fixed",
        "submitted_by_id": 7
    },
    # ... 15 more for Phoenix Fitness
    
    # Tiger Gym - 22 complaints (10 open) - Highest complaint rate
    {
        "id": 29,
        "customer_id": 116,
        "branch_id": 3,
        "category": "equipment",
        "priority": "high",
        "status": "open",
        "description": "Leg press machine broken",
        "submitted_at": datetime.now() - timedelta(days=1),
        "resolved_at": None,
        "resolution_notes": None,
        "submitted_by_id": 9
    },
    # ... 21 more for Tiger Gym (10 open, 12 resolved)
]
```

**Distribution by Branch:**
- Dragon Club: 12 total (1 open) - 8% open rate
- Phoenix Fitness: 16 total (0 open) - 0% open rate ✅ Best
- Tiger Gym: 22 total (10 open) - 45% open rate ⚠️ Needs attention

---

### 9. EXPENSES (45 records)

**Status Distribution:**
- Pending: 10 (22%)
- Approved: 35 (78%)

**Categories:**
- maintenance (30%)
- equipment (25%)
- utilities (20%)
- supplies (15%)
- other (10%)

**Priority:**
- urgent: 3 (30% of pending)
- normal: 7 (70% of pending)

**Expense Template:**

```python
expenses = [
    # Dragon Club - Pending (3 urgent, 2 normal)
    {
        "id": 1,
        "branch_id": 1,
        "category": "maintenance",
        "amount": 5000.0,
        "description": "AC repair - main hall",
        "status": "pending",
        "priority": "urgent",
        "requested_date": datetime.now() - timedelta(days=1),
        "requested_by_id": 2,  # manager_dragon
        "approved_date": None,
        "approved_by_id": None,
        "notes": "AC completely broken, urgent fix needed"
    },
    {
        "id": 2,
        "branch_id": 1,
        "category": "equipment",
        "amount": 12000.0,
        "description": "New treadmill purchase",
        "status": "pending",
        "priority": "urgent",
        "requested_date": datetime.now() - timedelta(days=2),
        "requested_by_id": 2,
        "approved_date": None,
        "approved_by_id": None,
        "notes": "Old treadmill beyond repair"
    },
    {
        "id": 3,
        "branch_id": 1,
        "category": "supplies",
        "amount": 2000.0,
        "description": "Cleaning supplies for month",
        "status": "pending",
        "priority": "normal",
        "requested_date": datetime.now() - timedelta(days=3),
        "requested_by_id": 2,
        "approved_date": None,
        "approved_by_id": None,
        "notes": None
    },
    
    # Phoenix Fitness - Pending (3)
    {
        "id": 4,
        "branch_id": 2,
        "category": "utilities",
        "amount": 8000.0,
        "description": "Electricity bill - January 2026",
        "status": "pending",
        "priority": "normal",
        "requested_date": datetime.now() - timedelta(days=4),
        "requested_by_id": 3,  # manager_phoenix
        "approved_date": None,
        "approved_by_id": None,
        "notes": None
    },
    
    # Tiger Gym - Pending (4, including 1 urgent)
    {
        "id": 7,
        "branch_id": 3,
        "category": "maintenance",
        "amount": 15000.0,
        "description": "Complete locker room renovation",
        "status": "pending",
        "priority": "urgent",
        "requested_date": datetime.now() - timedelta(days=5),
        "requested_by_id": 4,  # manager_tiger
        "approved_date": None,
        "approved_by_id": None,
        "notes": "Customer complaints high - urgent"
    },
    
    # Approved Expenses (35) - Historical
    {
        "id": 11,
        "branch_id": 1,
        "category": "equipment",
        "amount": 25000.0,
        "description": "5 new exercise bikes",
        "status": "approved",
        "priority": "normal",
        "requested_date": datetime(2026, 1, 15),
        "requested_by_id": 2,
        "approved_date": datetime(2026, 1, 17),
        "approved_by_id": 1,  # owner
        "notes": "Approved for Q1 budget"
    },
    # ... 34 more approved expenses
]
```

**Total Pending Expenses:** 35,000 EGP (3 urgent = 32,000 EGP)

---

### 10. ATTENDANCE (280 records)

**Coverage:** 1 month of attendance for all 14 staff members

**Attendance Template:**

```python
def generate_attendance(user_id, branch_id, days=30):
    """
    Generate attendance records for staff member
    """
    attendance_records = []
    
    for day in range(days):
        date = datetime.now().date() - timedelta(days=day)
        
        # 95% attendance rate (random absences)
        if random.random() < 0.95:
            check_in = time(random.randint(8, 9), random.randint(0, 59))
            check_out = time(random.randint(17, 19), random.randint(0, 59))
            
            # Calculate hours
            check_in_dt = datetime.combine(date, check_in)
            check_out_dt = datetime.combine(date, check_out)
            hours_worked = (check_out_dt - check_in_dt).seconds / 3600
            
            attendance_records.append({
                "user_id": user_id,
                "branch_id": branch_id,
                "date": date,
                "check_in": check_in,
                "check_out": check_out,
                "status": "present",
                "hours_worked": round(hours_worked, 2),
                "notes": None
            })
        else:
            attendance_records.append({
                "user_id": user_id,
                "branch_id": branch_id,
                "date": date,
                "check_in": None,
                "check_out": None,
                "status": "absent",
                "hours_worked": 0,
                "notes": "Sick leave" if random.random() < 0.5 else "Personal leave"
            })
    
    return attendance_records

# Generate for all staff
attendance = []
for user in users[1:]:  # Skip owner (id=1)
    attendance.extend(generate_attendance(user["id"], user.get("branch_id")))

# Total: 13 staff * 30 days * 0.95 attendance = ~280 records
```

---

### 11. CASH DIFFERENCES (90 records)

**Purpose:** Track daily closing discrepancies

**Template:**

```python
def generate_cash_differences(branch_id, days=30):
    """
    Generate daily cash closing records
    """
    differences = []
    
    for day in range(days):
        date = datetime.now().date() - timedelta(days=day)
        
        # Daily expected cash (average per branch)
        if branch_id == 1:  # Dragon Club
            expected_cash = random.uniform(1800, 2500)
        elif branch_id == 2:  # Phoenix
            expected_cash = random.uniform(1600, 2200)
        else:  # Tiger
            expected_cash = random.uniform(1200, 1600)
        
        # 80% of days have small differences (-100 to +100)
        # 20% of days are exact
        if random.random() < 0.8:
            difference = random.uniform(-100, 100)
        else:
            difference = 0
        
        actual_cash = expected_cash + difference
        
        differences.append({
            "branch_id": branch_id,
            "date": date,
            "expected_cash": round(expected_cash, 2),
            "actual_cash": round(actual_cash, 2),
            "difference": round(difference, 2),
            "notes": "Customer change" if abs(difference) > 50 else None,
            "recorded_by_id": random.randint(5, 10),  # Random receptionist
            "created_at": datetime.combine(date, time(23, 0))
        })
    
    return differences

cash_differences = []
for branch_id in [1, 2, 3]:
    cash_differences.extend(generate_cash_differences(branch_id, 30))

# Total: 3 branches * 30 days = 90 records
```

**Total Cash Differences:** -150 EGP (cumulative across all branches)

---

## 🧪 TEST SCENARIOS COVERAGE

### Owner Dashboard Tests

✅ **Total Revenue Display**
- Data: 164,521 EGP from 245 payments
- Test: Owner sees correct total revenue

✅ **Active Subscriptions Count**
- Data: 83 active subscriptions
- Test: Owner sees 83 active subscriptions

✅ **Total Customers**
- Data: 150 customers across 3 branches
- Test: Owner sees 150 customers

✅ **Branch Count**
- Data: 3 branches (Dragon, Phoenix, Tiger)
- Test: Owner sees 3 branches in list

✅ **Smart Alerts**
- Expiring Today: 2 subscriptions
- Expiring in 7 days: 11 subscriptions
- Low Coins: 8 subscriptions (< 3 coins)
- Open Complaints: 11 complaints
- Pending Expenses: 10 (3 urgent)

✅ **Branch Comparison**
- Dragon: Best performer (40 active subs, 65k revenue, 1 open complaint)
- Phoenix: Good (35 active subs, 58k revenue, 0 open complaints)
- Tiger: Needs attention (8 active subs, 41k revenue, 10 open complaints)

---

### Manager Dashboard Tests

✅ **Dragon Manager**
- Customers: 60
- Active Subscriptions: 40
- Revenue: 65,000 EGP
- Open Complaints: 1
- Staff: 2 receptionists

✅ **Phoenix Manager**
- Customers: 55
- Active Subscriptions: 35
- Revenue: 58,000 EGP
- Open Complaints: 0
- Staff: 2 receptionists

✅ **Tiger Manager**
- Customers: 35
- Active Subscriptions: 8
- Revenue: 41,521 EGP
- Open Complaints: 10 ⚠️
- Staff: 2 receptionists

---

### Reception Staff Tests

✅ **Customer Registration**
- Can create new customers
- BMI auto-calculated
- QR code auto-generated

✅ **Subscription Activation**
- Can activate subscriptions
- Payment recorded
- End date auto-calculated

✅ **QR Scanner**
- Can scan customer QR codes
- Verifies active subscription
- Deducts coins
- Records entry log

✅ **Daily Closing**
- Records cash differences
- Tracks expected vs actual

---

### Accountant Tests

✅ **Central Accountant**
- Views all 3 branches
- Sees total revenue: 164,521 EGP
- Sees all 245 payments
- Access to all financial reports

✅ **Branch Accountant**
- Views only assigned branch
- Sees branch-specific revenue
- Sees branch payments only

---

### Client App Tests

✅ **Login with Activation Code**
- Customer phone: "01001234567"
- Activation code sent
- Login successful

✅ **Profile Display**
- Shows customer details
- Shows health metrics (BMI, ideal weight, calories)
- Shows active subscription

✅ **Subscription Display**
- Shows remaining days
- Shows remaining coins
- Shows freeze days available

✅ **Entry History**
- Shows check-in records
- Sorted by date (newest first)

✅ **QR Code Display**
- Shows QR code for scanning
- Can refresh QR code

---

## ✅ VALIDATION CHECKLIST

### Database Integrity

- [ ] All foreign keys valid (branch_id, customer_id, service_id, etc.)
- [ ] No orphaned records
- [ ] Unique constraints enforced (phone, email, username)
- [ ] Date logic correct (start_date < end_date)
- [ ] Prices and amounts > 0
- [ ] Status values from allowed set

### Business Logic

- [ ] Active subscriptions have remaining_days > 0
- [ ] Expired subscriptions have remaining_days = 0
- [ ] Frozen subscriptions have freeze_days_used < freeze_days_allowed
- [ ] Payments sum matches subscription amounts
- [ ] Entry logs only for active/frozen subscriptions
- [ ] Coins deducted in entry logs <= total_coins
- [ ] Revenue calculations accurate

### Role-Based Access

- [ ] Owner has branch_id = null
- [ ] Central accountants have branch_id = null
- [ ] Branch managers have valid branch_id
- [ ] Receptionists have valid branch_id
- [ ] Branch accountants have valid branch_id
- [ ] Each branch has 1 manager and 2 receptionists

### Test Data Quality

- [ ] Realistic names and data
- [ ] Egyptian phone numbers (01xxxxxxxxx)
- [ ] Valid email formats
- [ ] Reasonable health metrics (BMI 18-35)
- [ ] Varied complaint categories
- [ ] Mixed payment methods (cash dominant)
- [ ] Recent dates (last 1-3 months)

### Feature Coverage

- [ ] All subscription statuses represented
- [ ] All service types used
- [ ] All complaint categories present
- [ ] All payment methods used
- [ ] All priorities (low, medium, high) used
- [ ] Both resolved and open complaints
- [ ] Both approved and pending expenses

---

## 📝 SEED DATA SUMMARY

```
Total Database Records: ~4,500+

Staff Users: 14
  - Owner: 1
  - Branch Managers: 3
  - Receptionists: 6
  - Accountants: 4

Branches: 3
Services: 6
Customers: 150
Subscriptions: 136
  - Active: 83
  - Expired: 45
  - Frozen: 8

Payments: 245 (Total: 164,521 EGP)
Entry Logs: 3,500+
Complaints: 50 (11 open, 39 resolved)
Expenses: 45 (10 pending, 35 approved)
Attendance: 280 records
Cash Differences: 90 records
```

---

## 🚀 IMPLEMENTATION NOTES

### Password Hashing

```python
from werkzeug.security import generate_password_hash

# All staff passwords
staff_password = generate_password_hash("staff_password123")

# All client passwords
client_password = generate_password_hash("client123")
```

### Date Generation

```python
from datetime import datetime, timedelta

# Recent date (last 3 months)
recent_date = datetime.now() - timedelta(days=random.randint(0, 90))

# Subscription end date
end_date = start_date + timedelta(days=duration_days)
```

### QR Code Format

```python
qr_code = f"GYM-{customer_id}"
# Examples: GYM-1, GYM-151, GYM-150
```

### Receipt Number Format

```python
receipt_number = f"RCP-{date.strftime('%Y%m%d')}-{sequence:03d}"
# Example: RCP-20260214-001
```

---

## 🎯 EXPECTED RESULTS AFTER SEEDING

### Owner Dashboard Should Show:
- Total Revenue: 164,521 EGP ✅
- Active Subscriptions: 83 ✅
- Total Customers: 150 ✅
- Branches: 3 ✅
- Smart Alerts: 5 categories with counts ✅
- Branch comparison chart with 3 branches ✅

### Branch Manager Dashboards Should Show:
- Dragon: 60 customers, 40 subs, 65k revenue ✅
- Phoenix: 55 customers, 35 subs, 58k revenue ✅
- Tiger: 35 customers, 8 subs, 41.5k revenue ✅

### Reception Screens Should Show:
- Customer lists filtered by branch ✅
- 45 expired subscriptions for renewal ✅
- Ability to scan QR codes ✅
- Payment recording works ✅
- Daily closing functional ✅

### Client App Should Show:
- Can login with phone + activation code ✅
- Profile shows health metrics ✅
- Subscription shows remaining days/coins ✅
- Entry history displays check-ins ✅
- QR code displays for scanning ✅

---

**END OF SEED DATA GUIDE**

**Date:** February 14, 2026  
**Version:** 1.0  
**Status:** Complete ✅

**Use this guide to create a comprehensive seed.py file that provides realistic, production-quality test data for the Gym Management System.**

