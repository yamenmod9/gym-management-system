# 🌱 COMPLETE SEED DATA SPECIFICATION FOR GYM MANAGEMENT SYSTEM
**Date:** February 16, 2026  
**Purpose:** Comprehensive seed data requirements for testing all app features

---

## 📋 TABLE OF CONTENTS

1. [Branches](#1-branches)
2. [Services](#2-services)
3. [Staff Accounts](#3-staff-accounts)
4. [Customers](#4-customers)
5. [Subscriptions](#5-subscriptions)
6. [Attendance Records](#6-attendance-records)
7. [Payments](#7-payments)
8. [Expenses (Optional)](#8-expenses-optional)
9. [System Settings](#9-system-settings)

---

## 1. BRANCHES

Create **3 branches** with the following data:

### Branch 1: Dragon Club
```python
{
    "id": 1,
    "name": "Dragon Club",
    "prefix": "DRAGON",
    "address": "123 Main Street, Nasr City, Cairo",
    "phone": "0225551234",
    "email": "dragon@gym.com",
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

### Branch 2: Tigers Gym
```python
{
    "id": 2,
    "name": "Tigers Gym",
    "prefix": "TIGERS",
    "address": "456 Second Avenue, Giza",
    "phone": "0225555678",
    "email": "tigers@gym.com",
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

### Branch 3: Lions Fitness
```python
{
    "id": 3,
    "name": "Lions Fitness",
    "prefix": "LIONS",
    "address": "789 Third Boulevard, Maadi, Cairo",
    "phone": "0225559999",
    "email": "lions@gym.com",
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

**Total:** 3 branches

---

## 2. SERVICES

Create **10 services** with various types:

### Gym Services (5)

#### Service 1: Monthly Gym
```python
{
    "id": 1,
    "name": "Monthly Gym",
    "type": "gym",
    "description": "Full access to gym facilities for 30 days",
    "duration_days": 30,
    "price": 500.00,
    "is_active": True
}
```

#### Service 2: 3-Month Gym
```python
{
    "id": 2,
    "name": "3-Month Gym",
    "type": "gym",
    "description": "Full access to gym facilities for 90 days",
    "duration_days": 90,
    "price": 1200.00,
    "is_active": True
}
```

#### Service 3: 6-Month Gym
```python
{
    "id": 3,
    "name": "6-Month Gym",
    "type": "gym",
    "description": "Full access to gym facilities for 180 days",
    "duration_days": 180,
    "price": 2000.00,
    "is_active": True
}
```

#### Service 4: Annual Gym
```python
{
    "id": 4,
    "name": "Annual Gym",
    "type": "gym",
    "description": "Full access to gym facilities for 365 days",
    "duration_days": 365,
    "price": 3500.00,
    "is_active": True
}
```

#### Service 5: 30 Coins Package
```python
{
    "id": 5,
    "name": "30 Coins Package",
    "type": "coins",
    "description": "30 gym entry coins, valid for 12 months",
    "coins": 30,
    "validity_months": 12,
    "price": 600.00,
    "is_active": True
}
```

### Training Services (3)

#### Service 6: Personal Training - 10 Sessions
```python
{
    "id": 6,
    "name": "Personal Training - 10 Sessions",
    "type": "training",
    "description": "10 one-on-one personal training sessions",
    "sessions": 10,
    "validity_months": 3,
    "price": 1500.00,
    "is_active": True
}
```

#### Service 7: Personal Training - 20 Sessions
```python
{
    "id": 7,
    "name": "Personal Training - 20 Sessions",
    "type": "training",
    "description": "20 one-on-one personal training sessions",
    "sessions": 20,
    "validity_months": 6,
    "price": 2800.00,
    "is_active": True
}
```

#### Service 8: Group Training - Monthly
```python
{
    "id": 8,
    "name": "Group Training - Monthly",
    "type": "training",
    "description": "Unlimited group training classes for 30 days",
    "duration_days": 30,
    "price": 400.00,
    "is_active": True
}
```

### Special Services (2)

#### Service 9: 50 Coins Premium
```python
{
    "id": 9,
    "name": "50 Coins Premium",
    "type": "coins",
    "description": "50 gym entry coins, valid for 12 months",
    "coins": 50,
    "validity_months": 12,
    "price": 950.00,
    "is_active": True
}
```

#### Service 10: 12 Session Package
```python
{
    "id": 10,
    "name": "12 Session Package",
    "type": "sessions",
    "description": "12 gym sessions, valid for 2 months",
    "sessions": 12,
    "validity_months": 2,
    "price": 800.00,
    "is_active": True
}
```

**Total:** 10 services

---

## 3. STAFF ACCOUNTS

Create **15 staff members** across different roles and branches:

### Owners (2)

#### Staff 1: Main Owner
```python
{
    "id": 1,
    "full_name": "Ahmed Hassan",
    "phone": "01012345678",
    "email": "ahmed.owner@gym.com",
    "password": "owner123",  # Hash this
    "role": "owner",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 2: Co-Owner
```python
{
    "id": 2,
    "full_name": "Sarah Mohamed",
    "phone": "01098765432",
    "email": "sarah.owner@gym.com",
    "password": "owner123",  # Hash this
    "role": "owner",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

### Managers (3)

#### Staff 3: Manager - Dragon Club
```python
{
    "id": 3,
    "full_name": "Mohamed Ali",
    "phone": "01087654321",
    "email": "mohamed.manager@gym.com",
    "password": "manager123",  # Hash this
    "role": "manager",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 4: Manager - Tigers Gym
```python
{
    "id": 4,
    "full_name": "Fatima Ahmed",
    "phone": "01076543210",
    "email": "fatima.manager@gym.com",
    "password": "manager123",  # Hash this
    "role": "manager",
    "branch_id": 2,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 5: Manager - Lions Fitness
```python
{
    "id": 5,
    "full_name": "Omar Ibrahim",
    "phone": "01065432109",
    "email": "omar.manager@gym.com",
    "password": "manager123",  # Hash this
    "role": "manager",
    "branch_id": 3,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

### Accountants (4)

#### Staff 6: Accountant - Dragon Club
```python
{
    "id": 6,
    "full_name": "Layla Mahmoud",
    "phone": "01054321098",
    "email": "layla.accountant@gym.com",
    "password": "accountant123",  # Hash this
    "role": "accountant",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 7: Accountant - Tigers Gym
```python
{
    "id": 7,
    "full_name": "Hassan Khalil",
    "phone": "01043210987",
    "email": "hassan.accountant@gym.com",
    "password": "accountant123",  # Hash this
    "role": "accountant",
    "branch_id": 2,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 8: Accountant - Lions Fitness
```python
{
    "id": 8,
    "full_name": "Nour Salem",
    "phone": "01032109876",
    "email": "nour.accountant@gym.com",
    "password": "accountant123",  # Hash this
    "role": "accountant",
    "branch_id": 3,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 9: Head Accountant
```python
{
    "id": 9,
    "full_name": "Youssef Adel",
    "phone": "01021098765",
    "email": "youssef.accountant@gym.com",
    "password": "accountant123",  # Hash this
    "role": "accountant",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

### Receptionists (6)

#### Staff 10: Receptionist - Dragon Club (Morning)
```python
{
    "id": 10,
    "full_name": "Amira Hassan",
    "phone": "01045678901",
    "email": "amira.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 11: Receptionist - Dragon Club (Evening)
```python
{
    "id": 11,
    "full_name": "Karim Youssef",
    "phone": "01056789012",
    "email": "karim.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 1,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 12: Receptionist - Tigers Gym (Morning)
```python
{
    "id": 12,
    "full_name": "Heba Mohamed",
    "phone": "01067890123",
    "email": "heba.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 2,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 13: Receptionist - Tigers Gym (Evening)
```python
{
    "id": 13,
    "full_name": "Tamer Ali",
    "phone": "01078901234",
    "email": "tamer.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 2,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 14: Receptionist - Lions Fitness (Morning)
```python
{
    "id": 14,
    "full_name": "Rana Ibrahim",
    "phone": "01089012345",
    "email": "rana.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 3,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

#### Staff 15: Receptionist - Lions Fitness (Evening)
```python
{
    "id": 15,
    "full_name": "Mahmoud Khaled",
    "phone": "01090123456",
    "email": "mahmoud.reception@gym.com",
    "password": "receptionist123",  # Hash this
    "role": "receptionist",
    "branch_id": 3,
    "is_active": True,
    "created_at": "2026-01-01T00:00:00Z"
}
```

**Total:** 15 staff (2 owners, 3 managers, 4 accountants, 6 receptionists)

---

## 4. CUSTOMERS

Create **150 customers** distributed across branches:
- Dragon Club (Branch 1): 60 customers
- Tigers Gym (Branch 2): 50 customers
- Lions Fitness (Branch 3): 40 customers

### Customer Template & Requirements

Each customer should have:
```python
{
    "id": <unique_id>,
    "full_name": "<Name>",
    "phone": "010/011/012/015 + 8 digits (unique)",
    "email": "customer<id>@example.com",
    "national_id": "295/296/297 + 11 digits (unique)",
    "date_of_birth": "YYYY-MM-DD (age 18-45)",
    "gender": "male" or "female",
    "address": "<number> Street, <City>",
    "branch_id": <1, 2, or 3>,
    "height": 150.0 - 195.0 (cm),
    "weight": 50.0 - 120.0 (kg),
    "health_notes": "<Notes or None>",
    "qr_code": "CUST-<id>-<BRANCH_PREFIX>",
    "temp_password": "<6 random alphanumeric>",
    "password_changed": True/False (30% false, 70% true),
    "is_active": True (90% true, 10% false),
    "created_at": "2026-01-01 to 2026-02-15",
    "updated_at": "2026-01-01 to 2026-02-16"
}
```

**Important Fields:**
- `bmi`: Auto-calculated from weight and height
- `bmi_category`: "Underweight", "Normal", "Overweight", or "Obese"
- `bmr`: Auto-calculated basal metabolic rate
- `daily_calories`: Auto-calculated based on BMR
- `ideal_weight`: Auto-calculated based on height

### Sample Customers (First 20)

#### Customer 1-5: Dragon Club
```python
# Customer 1
{
    "id": 1,
    "full_name": "Mohamed Salem",
    "phone": "01077827638",
    "email": "customer1@example.com",
    "national_id": "29501011234567",
    "date_of_birth": "1995-01-01",
    "gender": "male",
    "address": "10 Main Street, Cairo",
    "branch_id": 1,
    "height": 175.0,
    "weight": 80.0,
    "health_notes": "None",
    "qr_code": "CUST-001-DRAGON",
    "temp_password": "RX04AF",
    "password_changed": True,
    "is_active": True
}

# Customer 2
{
    "id": 2,
    "full_name": "Layla Rashad",
    "phone": "01022981052",
    "email": "customer2@example.com",
    "national_id": "29601021234568",
    "date_of_birth": "1996-01-02",
    "gender": "female",
    "address": "20 Second Avenue, Cairo",
    "branch_id": 1,
    "height": 165.0,
    "weight": 60.0,
    "health_notes": "Allergic to dust",
    "qr_code": "CUST-002-DRAGON",
    "temp_password": "SI19IC",
    "password_changed": True,
    "is_active": True
}

# Customer 3
{
    "id": 3,
    "full_name": "Ibrahim Hassan",
    "phone": "01041244663",
    "email": "customer3@example.com",
    "national_id": "29701031234569",
    "date_of_birth": "1997-01-03",
    "gender": "male",
    "address": "30 Third Boulevard, Cairo",
    "branch_id": 1,
    "height": 180.0,
    "weight": 85.0,
    "health_notes": "Previous knee injury",
    "qr_code": "CUST-003-DRAGON",
    "temp_password": "PS02HC",
    "password_changed": False,
    "is_active": True
}

# Customer 4
{
    "id": 4,
    "full_name": "Hadeer Youssef",
    "phone": "01095899313",
    "email": "customer4@example.com",
    "national_id": "29501041234570",
    "date_of_birth": "1995-01-04",
    "gender": "female",
    "address": "40 Fourth Street, Cairo",
    "branch_id": 1,
    "height": 170.0,
    "weight": 65.0,
    "health_notes": "None",
    "qr_code": "CUST-004-DRAGON",
    "temp_password": "PE71JZ",
    "password_changed": True,
    "is_active": True
}

# Customer 5
{
    "id": 5,
    "full_name": "Somaya Hassan",
    "phone": "01085345555",
    "email": "customer5@example.com",
    "national_id": "29601051234571",
    "date_of_birth": "1996-01-05",
    "gender": "female",
    "address": "50 Fifth Avenue, Cairo",
    "branch_id": 1,
    "height": 162.0,
    "weight": 58.0,
    "health_notes": "Vegetarian diet",
    "qr_code": "CUST-005-DRAGON",
    "temp_password": "RK94GG",
    "password_changed": True,
    "is_active": True
}
```

#### Customer 61-65: Tigers Gym
```python
# Customer 61
{
    "id": 61,
    "full_name": "Adel Saad",
    "phone": "01025867870",
    "email": "customer61@example.com",
    "national_id": "29507293823553",
    "date_of_birth": "1993-08-25",
    "gender": "male",
    "address": "41 Street, Giza",
    "branch_id": 2,
    "height": 172.0,
    "weight": 92.0,
    "health_notes": "Asthma - no heavy cardio",
    "qr_code": "CUST-061-TIGERS",
    "temp_password": "AB12CD",
    "password_changed": False,
    "is_active": True
}

# Customer 62
{
    "id": 62,
    "full_name": "Ahmed Salem",
    "phone": "01022802372",
    "email": "customer62@example.com",
    "national_id": "29905898890707",
    "date_of_birth": "1987-05-19",
    "gender": "male",
    "address": "83 Street, Giza",
    "branch_id": 2,
    "height": 167.0,
    "weight": 72.0,
    "health_notes": "Previous knee injury",
    "qr_code": "CUST-062-TIGERS",
    "temp_password": "EF34GH",
    "password_changed": False,
    "is_active": True
}

# Continue with 63-65 following similar pattern...
```

#### Customer 111-115: Lions Fitness
```python
# Customer 111
{
    "id": 111,
    "full_name": "Khaled Mostafa",
    "phone": "01011122233",
    "email": "customer111@example.com",
    "national_id": "29501111234580",
    "date_of_birth": "1995-05-15",
    "gender": "male",
    "address": "100 Lion Street, Maadi",
    "branch_id": 3,
    "height": 178.0,
    "weight": 82.0,
    "health_notes": "None",
    "qr_code": "CUST-111-LIONS",
    "temp_password": "IJ56KL",
    "password_changed": True,
    "is_active": True
}

# Continue with 112-115 following similar pattern...
```

### Customer Distribution by Status
- **Active (is_active=True):** 135 customers (90%)
- **Inactive (is_active=False):** 15 customers (10%)
- **Password Changed (password_changed=True):** 105 customers (70%)
- **Password Not Changed (password_changed=False):** 45 customers (30%)

**Total:** 150 customers

---

## 5. SUBSCRIPTIONS

Create **120 active subscriptions** + **30 expired subscriptions** = **150 total**

### Subscription Distribution

#### By Branch:
- Dragon Club: 60 subscriptions (50 active, 10 expired)
- Tigers Gym: 50 subscriptions (40 active, 10 expired)
- Lions Fitness: 40 subscriptions (30 active, 10 expired)

#### By Type:
- **Coins:** 60 subscriptions (50%)
- **Time-based:** 45 subscriptions (37.5%)
- **Sessions:** 10 subscriptions (8.3%)
- **Training:** 5 subscriptions (4.2%)

### Subscription Template
```python
{
    "id": <unique_id>,
    "customer_id": <customer_id>,
    "service_id": <service_id>,
    "branch_id": <branch_id>,
    "subscription_type": "coins|time_based|sessions|training",
    "start_date": "2026-01-XX or 2026-02-XX",
    "end_date": "<calculated based on service>",
    "validity_months": <from service or null>,
    "status": "active|expired",
    "remaining_coins": <0-50 or null>,
    "total_coins": <from service or null>,
    "remaining_sessions": <0-20 or null>,
    "total_sessions": <from service or null>,
    "amount": <from service price>,
    "payment_method": "cash|card",
    "discount": 0.00 - 100.00,
    "notes": "<optional notes>",
    "created_at": "2026-01-XX or 2026-02-XX",
    "display_metric": "coins|time|sessions|training",
    "display_value": <numeric value>,
    "display_label": "<formatted string>"
}
```

### Sample Subscriptions (First 10)

#### Subscription 1: Coins-based (Active)
```python
{
    "id": 1,
    "customer_id": 1,
    "service_id": 5,  # 30 Coins Package
    "branch_id": 1,
    "subscription_type": "coins",
    "start_date": "2026-02-01",
    "end_date": "2027-02-01",
    "validity_months": 12,
    "status": "active",
    "remaining_coins": 25,
    "total_coins": 30,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 600.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": "First subscription",
    "created_at": "2026-02-01T10:00:00Z",
    "display_metric": "coins",
    "display_value": 25,
    "display_label": "25 Coins"
}
```

#### Subscription 2: Time-based (Active)
```python
{
    "id": 2,
    "customer_id": 2,
    "service_id": 1,  # Monthly Gym
    "branch_id": 1,
    "subscription_type": "time_based",
    "start_date": "2026-02-05",
    "end_date": "2026-03-07",
    "validity_months": 1,
    "status": "active",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 500.00,
    "payment_method": "card",
    "discount": 0.00,
    "notes": None,
    "created_at": "2026-02-05T10:00:00Z",
    "display_metric": "time",
    "display_value": 19,
    "display_label": "19 days"
}
```

#### Subscription 3: Sessions (Active)
```python
{
    "id": 3,
    "customer_id": 3,
    "service_id": 10,  # 12 Session Package
    "branch_id": 1,
    "subscription_type": "sessions",
    "start_date": "2026-02-10",
    "end_date": "2026-04-10",
    "validity_months": 2,
    "status": "active",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": 8,
    "total_sessions": 12,
    "amount": 800.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": None,
    "created_at": "2026-02-10T10:00:00Z",
    "display_metric": "sessions",
    "display_value": 8,
    "display_label": "8 Sessions"
}
```

#### Subscription 4: Training (Active)
```python
{
    "id": 4,
    "customer_id": 4,
    "service_id": 6,  # Personal Training - 10 Sessions
    "branch_id": 1,
    "subscription_type": "training",
    "start_date": "2026-02-08",
    "end_date": "2026-05-08",
    "validity_months": 3,
    "status": "active",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": 7,
    "total_sessions": 10,
    "amount": 1500.00,
    "payment_method": "cash",
    "discount": 100.00,
    "notes": "New member discount",
    "created_at": "2026-02-08T10:00:00Z",
    "display_metric": "training",
    "display_value": 7,
    "display_label": "7 Training Sessions"
}
```

#### Subscription 5: Coins-based with many coins (Active)
```python
{
    "id": 5,
    "customer_id": 5,
    "service_id": 9,  # 50 Coins Premium
    "branch_id": 1,
    "subscription_type": "coins",
    "start_date": "2026-01-20",
    "end_date": "2027-01-20",
    "validity_months": 12,
    "status": "active",
    "remaining_coins": 48,
    "total_coins": 50,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 950.00,
    "payment_method": "card",
    "discount": 0.00,
    "notes": None,
    "created_at": "2026-01-20T10:00:00Z",
    "display_metric": "coins",
    "display_value": 48,
    "display_label": "48 Coins"
}
```

#### Subscription 6: 3-Month Gym (Active)
```python
{
    "id": 6,
    "customer_id": 6,
    "service_id": 2,  # 3-Month Gym
    "branch_id": 1,
    "subscription_type": "time_based",
    "start_date": "2026-01-01",
    "end_date": "2026-04-01",
    "validity_months": 3,
    "status": "active",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 1200.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": None,
    "created_at": "2026-01-01T10:00:00Z",
    "display_metric": "time",
    "display_value": 44,
    "display_label": "1 month, 14 days"
}
```

#### Subscription 7: Expired (Coins depleted)
```python
{
    "id": 7,
    "customer_id": 7,
    "service_id": 5,  # 30 Coins Package
    "branch_id": 1,
    "subscription_type": "coins",
    "start_date": "2025-12-01",
    "end_date": "2026-12-01",
    "validity_months": 12,
    "status": "expired",
    "remaining_coins": 0,
    "total_coins": 30,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 600.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": "Coins depleted",
    "created_at": "2025-12-01T10:00:00Z",
    "display_metric": "coins",
    "display_value": 0,
    "display_label": "0 Coins"
}
```

#### Subscription 8: Expired (Time passed)
```python
{
    "id": 8,
    "customer_id": 8,
    "service_id": 1,  # Monthly Gym
    "branch_id": 1,
    "subscription_type": "time_based",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31",
    "validity_months": 1,
    "status": "expired",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 500.00,
    "payment_method": "card",
    "discount": 0.00,
    "notes": "Expired - time passed",
    "created_at": "2026-01-01T10:00:00Z",
    "display_metric": "time",
    "display_value": 0,
    "display_label": "Expired"
}
```

#### Subscription 9: Expired (Sessions depleted)
```python
{
    "id": 9,
    "customer_id": 9,
    "service_id": 10,  # 12 Session Package
    "branch_id": 1,
    "subscription_type": "sessions",
    "start_date": "2025-12-15",
    "end_date": "2026-02-15",
    "validity_months": 2,
    "status": "expired",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": 0,
    "total_sessions": 12,
    "amount": 800.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": "All sessions used",
    "created_at": "2025-12-15T10:00:00Z",
    "display_metric": "sessions",
    "display_value": 0,
    "display_label": "0 Sessions"
}
```

#### Subscription 10: Active (6-Month)
```python
{
    "id": 10,
    "customer_id": 10,
    "service_id": 3,  # 6-Month Gym
    "branch_id": 1,
    "subscription_type": "time_based",
    "start_date": "2026-01-15",
    "end_date": "2026-07-15",
    "validity_months": 6,
    "status": "active",
    "remaining_coins": None,
    "total_coins": None,
    "remaining_sessions": None,
    "total_sessions": None,
    "amount": 2000.00,
    "payment_method": "cash",
    "discount": 0.00,
    "notes": None,
    "created_at": "2026-01-15T10:00:00Z",
    "display_metric": "time",
    "display_value": 149,
    "display_label": "4 months, 29 days"
}
```

### Subscription Status Requirements
- **Active subscriptions:** 120 (80%)
  - With coins remaining: 50
  - With time remaining: 45
  - With sessions remaining: 20
  - With training sessions: 5
- **Expired subscriptions:** 30 (20%)
  - Coins depleted: 10
  - Time passed: 15
  - Sessions depleted: 5

**Total:** 150 subscriptions

---

## 6. ATTENDANCE RECORDS

Create **2,000 attendance records** distributed across:
- Last 30 days
- All active customers
- Realistic patterns (more in evenings, weekdays vs weekends)

### Attendance Template
```python
{
    "id": <unique_id>,
    "customer_id": <customer_id>,
    "subscription_id": <subscription_id>,
    "branch_id": <branch_id>,
    "check_in_time": "2026-XX-XX HH:MM:SS",
    "action": "check_in|check_in_with_coin|check_in_with_session",
    "coins_deducted": 0 or 1,
    "sessions_deducted": 0 or 1,
    "created_at": "2026-XX-XX HH:MM:SS"
}
```

### Sample Attendance Records

#### Attendance 1: Coin-based check-in
```python
{
    "id": 1,
    "customer_id": 1,
    "subscription_id": 1,
    "branch_id": 1,
    "check_in_time": "2026-02-16T09:30:00Z",
    "action": "check_in_with_coin",
    "coins_deducted": 1,
    "sessions_deducted": 0,
    "created_at": "2026-02-16T09:30:00Z"
}
```

#### Attendance 2: Session-based check-in
```python
{
    "id": 2,
    "customer_id": 3,
    "subscription_id": 3,
    "branch_id": 1,
    "check_in_time": "2026-02-16T10:00:00Z",
    "action": "check_in_with_session",
    "coins_deducted": 0,
    "sessions_deducted": 1,
    "created_at": "2026-02-16T10:00:00Z"
}
```

#### Attendance 3: Time-based check-in (no deduction)
```python
{
    "id": 3,
    "customer_id": 2,
    "subscription_id": 2,
    "branch_id": 1,
    "check_in_time": "2026-02-16T11:15:00Z",
    "action": "check_in",
    "coins_deducted": 0,
    "sessions_deducted": 0,
    "created_at": "2026-02-16T11:15:00Z"
}
```

### Time Distribution Guidelines
- **Morning (6AM-12PM):** 30% of records
- **Afternoon (12PM-6PM):** 25% of records
- **Evening (6PM-10PM):** 40% of records
- **Night (10PM-12AM):** 5% of records

### Day Distribution Guidelines
- **Weekdays (Mon-Thu):** 60% of records
- **Weekend (Fri-Sat):** 35% of records
- **Sunday:** 5% of records

**Total:** 2,000 attendance records

---

## 7. PAYMENTS

Create **150 payment records** (one for each subscription)

### Payment Template
```python
{
    "id": <unique_id>,
    "customer_id": <customer_id>,
    "subscription_id": <subscription_id>,
    "branch_id": <branch_id>,
    "amount": <service_price - discount>,
    "payment_method": "cash|card|bank_transfer",
    "discount": 0.00 - 100.00,
    "collected_by_staff_id": <staff_id>,
    "payment_date": "<subscription_created_at>",
    "notes": "<optional notes>",
    "created_at": "<subscription_created_at>"
}
```

### Sample Payments

#### Payment 1: Cash payment
```python
{
    "id": 1,
    "customer_id": 1,
    "subscription_id": 1,
    "branch_id": 1,
    "amount": 600.00,
    "payment_method": "cash",
    "discount": 0.00,
    "collected_by_staff_id": 10,  # Receptionist
    "payment_date": "2026-02-01T10:00:00Z",
    "notes": "Full payment",
    "created_at": "2026-02-01T10:00:00Z"
}
```

#### Payment 2: Card payment
```python
{
    "id": 2,
    "customer_id": 2,
    "subscription_id": 2,
    "branch_id": 1,
    "amount": 500.00,
    "payment_method": "card",
    "discount": 0.00,
    "collected_by_staff_id": 10,
    "payment_date": "2026-02-05T10:00:00Z",
    "notes": None,
    "created_at": "2026-02-05T10:00:00Z"
}
```

#### Payment 3: Cash with discount
```python
{
    "id": 3,
    "customer_id": 4,
    "subscription_id": 4,
    "branch_id": 1,
    "amount": 1400.00,
    "payment_method": "cash",
    "discount": 100.00,
    "collected_by_staff_id": 10,
    "payment_date": "2026-02-08T10:00:00Z",
    "notes": "New member discount 100 EGP",
    "created_at": "2026-02-08T10:00:00Z"
}
```

### Payment Method Distribution
- **Cash:** 60% (90 payments)
- **Card:** 35% (52 payments)
- **Bank Transfer:** 5% (8 payments)

### Discount Distribution
- **No discount (0 EGP):** 80% (120 payments)
- **Small discount (50-100 EGP):** 15% (22 payments)
- **Large discount (>100 EGP):** 5% (8 payments)

**Total:** 150 payments

---

## 8. EXPENSES (Optional)

Create **50 expense records** for testing accountant features

### Expense Template
```python
{
    "id": <unique_id>,
    "branch_id": <branch_id>,
    "category": "rent|utilities|salaries|equipment|maintenance|marketing|other",
    "amount": 500.00 - 10000.00,
    "description": "<expense description>",
    "expense_date": "2026-01-XX or 2026-02-XX",
    "recorded_by_staff_id": <accountant_staff_id>,
    "payment_method": "cash|bank_transfer",
    "notes": "<optional notes>",
    "created_at": "2026-01-XX or 2026-02-XX"
}
```

### Sample Expenses

#### Expense 1: Rent
```python
{
    "id": 1,
    "branch_id": 1,
    "category": "rent",
    "amount": 10000.00,
    "description": "February 2026 rent",
    "expense_date": "2026-02-01",
    "recorded_by_staff_id": 6,  # Accountant
    "payment_method": "bank_transfer",
    "notes": "Monthly rent payment",
    "created_at": "2026-02-01T08:00:00Z"
}
```

#### Expense 2: Utilities
```python
{
    "id": 2,
    "branch_id": 1,
    "category": "utilities",
    "amount": 2500.00,
    "description": "Electricity and water bill",
    "expense_date": "2026-02-10",
    "recorded_by_staff_id": 6,
    "payment_method": "cash",
    "notes": "January 2026 bills",
    "created_at": "2026-02-10T10:00:00Z"
}
```

#### Expense 3: Equipment
```python
{
    "id": 3,
    "branch_id": 1,
    "category": "equipment",
    "amount": 5000.00,
    "description": "New treadmill purchase",
    "expense_date": "2026-02-12",
    "recorded_by_staff_id": 6,
    "payment_method": "bank_transfer",
    "notes": "Treadmill model XYZ-2000",
    "created_at": "2026-02-12T14:00:00Z"
}
```

### Expense Category Distribution
- **Rent:** 15% (7-8 records)
- **Utilities:** 20% (10 records)
- **Salaries:** 25% (12-13 records)
- **Equipment:** 15% (7-8 records)
- **Maintenance:** 15% (7-8 records)
- **Marketing:** 5% (2-3 records)
- **Other:** 5% (2-3 records)

**Total:** 50 expenses

---

## 9. SYSTEM SETTINGS

Create system-wide settings:

```python
{
    "gym_name": "Dragon Fitness Group",
    "currency": "EGP",
    "timezone": "Africa/Cairo",
    "business_hours": {
        "open": "06:00",
        "close": "23:00"
    },
    "features": {
        "qr_checkin": True,
        "online_payments": False,
        "freeze_subscriptions": True,
        "max_freeze_days": 7
    },
    "contact": {
        "phone": "0225551234",
        "email": "info@dragonfitness.com",
        "website": "www.dragonfitness.com"
    },
    "social_media": {
        "facebook": "DragonFitnessEG",
        "instagram": "@dragonfitness",
        "twitter": "@dragonfitness"
    }
}
```

---

## 📊 SEED DATA SUMMARY

| Category | Count | Details |
|----------|-------|---------|
| **Branches** | 3 | Dragon Club, Tigers Gym, Lions Fitness |
| **Services** | 10 | 5 gym, 3 training, 2 special |
| **Staff** | 15 | 2 owners, 3 managers, 4 accountants, 6 receptionists |
| **Customers** | 150 | 60 Dragon, 50 Tigers, 40 Lions |
| **Subscriptions** | 150 | 120 active, 30 expired |
| **Attendance** | 2,000 | Last 30 days, all branches |
| **Payments** | 150 | One per subscription |
| **Expenses** | 50 | Optional, for accountant features |
| **Settings** | 1 | System-wide configuration |

**TOTAL RECORDS:** ~2,500+

---

## ✅ SEED DATA GENERATION CHECKLIST

### Phase 1: Core Setup
- [ ] Create 3 branches
- [ ] Create 10 services
- [ ] Create 15 staff accounts
- [ ] Create system settings

### Phase 2: Customer Data
- [ ] Generate 150 customers with unique phones/national IDs
- [ ] Assign customers to branches (60/50/40 distribution)
- [ ] Calculate BMI, BMR, daily calories for each
- [ ] Generate QR codes and temporary passwords
- [ ] Set password_changed and is_active flags

### Phase 3: Subscription Data
- [ ] Create 120 active subscriptions
- [ ] Create 30 expired subscriptions
- [ ] Distribute subscriptions by type (coins/time/sessions/training)
- [ ] Calculate display_metric, display_value, display_label
- [ ] Ensure realistic remaining values

### Phase 4: Transaction Data
- [ ] Create 150 payment records (one per subscription)
- [ ] Distribute payment methods (cash/card/bank)
- [ ] Add realistic discounts to 20% of payments
- [ ] Create 2,000 attendance records
- [ ] Distribute attendance across 30 days with realistic patterns

### Phase 5: Optional Data
- [ ] Create 50 expense records
- [ ] Distribute expenses across categories
- [ ] Link expenses to branches and accountants

---

## 🔑 IMPORTANT NOTES

1. **Unique Constraints:**
   - Customer phone numbers must be unique
   - Customer national IDs must be unique
   - Customer emails must be unique
   - Staff phone numbers must be unique
   - Staff emails must be unique

2. **Calculated Fields:**
   - BMI = weight / (height/100)²
   - BMR (Mifflin-St Jeor for males) = (10 × weight) + (6.25 × height) - (5 × age) + 5
   - BMR (Mifflin-St Jeor for females) = (10 × weight) + (6.25 × height) - (5 × age) - 161
   - Daily Calories = BMR × 1.55 (moderate activity)
   - Ideal Weight = 22 × (height/100)²

3. **Subscription Display Logic:**
   - **Coins:** display_metric="coins", display_value=remaining_coins, display_label="{coins} Coins"
   - **Time:** display_metric="time", display_value=days_remaining, display_label="{months} months, {days} days"
   - **Sessions:** display_metric="sessions", display_value=remaining_sessions, display_label="{sessions} Sessions"
   - **Training:** display_metric="training", display_value=remaining_sessions, display_label="{sessions} Training Sessions"

4. **Password Hashing:**
   - All staff passwords should be hashed using bcrypt or similar
   - Customer temporary passwords should be stored in plain text (for display to receptionist)
   - Customer actual passwords (after change) should be hashed

5. **Date Ranges:**
   - Customers created: 2026-01-01 to 2026-02-15
   - Subscriptions created: 2026-01-01 to 2026-02-15
   - Attendance records: 2026-01-17 to 2026-02-16 (last 30 days)
   - Expenses: 2026-01-01 to 2026-02-16

6. **Branch Validation:**
   - Staff can only see/manage data for their assigned branch
   - Exception: Owners can access all branches
   - Receptionists can only activate subscriptions for customers in their branch

---

## 🚀 IMPLEMENTATION EXAMPLE (Python seed.py)

```python
from datetime import datetime, timedelta
from random import choice, randint, uniform
import string

def generate_phone():
    """Generate unique Egyptian phone number"""
    prefix = choice(['010', '011', '012', '015'])
    number = ''.join([str(randint(0, 9)) for _ in range(8)])
    return prefix + number

def generate_temp_password():
    """Generate 6-character temporary password"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(choice(chars) for _ in range(6))

def calculate_bmi(weight, height):
    """Calculate BMI"""
    height_m = height / 100
    return round(weight / (height_m ** 2), 2)

def calculate_bmr(weight, height, age, gender):
    """Calculate BMR using Mifflin-St Jeor"""
    bmr = (10 * weight) + (6.25 * height) - (5 * age)
    if gender == 'male':
        bmr += 5
    else:
        bmr -= 161
    return round(bmr, 2)

def get_display_label(subscription):
    """Generate display label for subscription"""
    if subscription['subscription_type'] == 'coins':
        coins = subscription['remaining_coins']
        return f"{coins} Coins"
    elif subscription['subscription_type'] == 'time_based':
        days = subscription['display_value']
        months = days // 30
        remaining_days = days % 30
        if months > 0:
            return f"{months} months, {remaining_days} days"
        return f"{days} days"
    elif subscription['subscription_type'] == 'sessions':
        sessions = subscription['remaining_sessions']
        return f"{sessions} Sessions"
    elif subscription['subscription_type'] == 'training':
        sessions = subscription['remaining_sessions']
        return f"{sessions} Training Sessions"

# Use these helper functions when generating seed data
```

---

**Document Version:** 1.0  
**Date:** February 16, 2026  
**Status:** Complete Seed Data Specification  
**Total Expected Records:** ~2,500+

