# 🔧 BACKEND DATABASE FIX: TEMPORARY PASSWORD STORAGE AND RETRIEVAL

**Date:** February 14, 2026  
**Priority:** CRITICAL  
**Issue:** Temporary passwords are not stored in database and cannot be retrieved by staff

---

## 🚨 THE CORE PROBLEM

The temporary passwords (format: AB12CD) that are generated when creating customers are:
1. ❌ **NOT stored in the database** (only the hashed version exists)
2. ❌ **Lost forever after customer creation** (cannot be retrieved later)
3. ❌ **Not returned to receptionists** who need to give them to customers

This breaks the entire first-time login flow for customers.

---

## 🎯 REQUIRED DATABASE SCHEMA CHANGES

### Step 1: Add `temp_password` Column to customers Table

```sql
-- Run this SQL migration:
ALTER TABLE customers ADD COLUMN temp_password VARCHAR(10);
ALTER TABLE customers ADD COLUMN password_changed BOOLEAN DEFAULT FALSE;
```

**Or using Alembic migration:**

```python
"""add temp_password field

Revision ID: xxx
Revises: yyy
Create Date: 2026-02-14
"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('customers', 
        sa.Column('temp_password', sa.String(10), nullable=True))
    op.add_column('customers',
        sa.Column('password_changed', sa.Boolean(), 
                  nullable=False, server_default='false'))

def downgrade():
    op.drop_column('customers', 'temp_password')
    op.drop_column('customers', 'password_changed')
```

---

## 📝 REQUIRED MODEL CHANGES

### File: `backend/app/models/customer.py`

```python
from sqlalchemy import Column, Integer, String, Boolean, Float, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from datetime import datetime

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String(100), nullable=False, index=True)
    phone = Column(String(20), unique=True, nullable=False, index=True)
    email = Column(String(100), nullable=True)
    password = Column(String(255), nullable=False)  # Hashed password
    
    # ⭐ ADD THESE TWO FIELDS:
    temp_password = Column(String(10), nullable=True)  # Plain text for staff viewing
    password_changed = Column(Boolean, default=False, nullable=False)  # Track if changed
    
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    qr_code = Column(String(50), unique=True, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Health & Personal Info
    date_of_birth = Column(Date, nullable=True)
    gender = Column(String(20), nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    bmi_category = Column(String(50), nullable=True)
    bmr = Column(Float, nullable=True)
    ideal_weight = Column(Float, nullable=True)
    daily_calories = Column(Integer, nullable=True)
    address = Column(String(255), nullable=True)
    national_id = Column(String(20), nullable=True)
    health_notes = Column(String(500), nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branch = relationship("Branch", back_populates="customers")
    subscriptions = relationship("Subscription", back_populates="customer")
    complaints = relationship("Complaint", back_populates="customer")
```

---

## 🔄 REQUIRED API CHANGES

### File: `backend/app/api/v1/endpoints/customers.py`

#### 1. Update CREATE Customer Endpoint

```python
from app.utils.password import generate_temp_password, hash_password

@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a new customer - STAFF ONLY"""
    
    # Check if phone already exists
    existing = db.query(Customer).filter(Customer.phone == customer_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="Phone number already registered")
    
    # Generate temporary password
    temp_password = generate_temp_password()  # Returns: "AB12CD"
    
    # Calculate health metrics
    bmi = None
    bmi_category = None
    bmr = None
    ideal_weight = None
    daily_calories = None
    
    if customer_data.height and customer_data.weight:
        bmi = round(customer_data.weight / ((customer_data.height / 100) ** 2), 2)
        bmi_category = get_bmi_category(bmi)
        
        if customer_data.date_of_birth and customer_data.gender:
            age = calculate_age(customer_data.date_of_birth)
            bmr = calculate_bmr(customer_data.weight, customer_data.height, age, customer_data.gender)
            ideal_weight = calculate_ideal_weight(customer_data.height, customer_data.gender)
            daily_calories = calculate_daily_calories(bmr, "MODERATE")
    
    # Create customer
    new_customer = Customer(
        full_name=customer_data.full_name,
        phone=customer_data.phone,
        email=customer_data.email,
        password=hash_password(temp_password),  # Store HASHED version
        temp_password=temp_password,  # ⭐ Store PLAIN version for staff
        password_changed=False,  # ⭐ Mark as not changed
        branch_id=customer_data.branch_id,
        qr_code=f"CUST-{customer_data.phone[-6:]}-{datetime.now().strftime('%Y%m%d')}",
        date_of_birth=customer_data.date_of_birth,
        gender=customer_data.gender,
        height=customer_data.height,
        weight=customer_data.weight,
        bmi=bmi,
        bmi_category=bmi_category,
        bmr=bmr,
        ideal_weight=ideal_weight,
        daily_calories=daily_calories,
        address=customer_data.address,
        national_id=customer_data.national_id,
        health_notes=customer_data.health_notes,
        is_active=True,
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Return response with temp_password
    return CustomerResponse(
        id=new_customer.id,
        full_name=new_customer.full_name,
        phone=new_customer.phone,
        email=new_customer.email,
        branch_id=new_customer.branch_id,
        branch_name=new_customer.branch.name if new_customer.branch else None,
        qr_code=new_customer.qr_code,
        is_active=new_customer.is_active,
        password_changed=new_customer.password_changed,
        temp_password=new_customer.temp_password,  # ⭐ INCLUDE IN RESPONSE
        date_of_birth=new_customer.date_of_birth,
        gender=new_customer.gender,
        height=new_customer.height,
        weight=new_customer.weight,
        bmi=new_customer.bmi,
        bmi_category=new_customer.bmi_category,
        bmr=new_customer.bmr,
        ideal_weight=new_customer.ideal_weight,
        daily_calories=new_customer.daily_calories,
        created_at=new_customer.created_at,
        updated_at=new_customer.updated_at,
    )
```

#### 2. Update GET Customer by ID Endpoint

```python
@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get customer details - STAFF ONLY"""
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Build response
    return CustomerResponse(
        id=customer.id,
        full_name=customer.full_name,
        phone=customer.phone,
        email=customer.email,
        branch_id=customer.branch_id,
        branch_name=customer.branch.name if customer.branch else None,
        qr_code=customer.qr_code,
        is_active=customer.is_active,
        password_changed=customer.password_changed,
        temp_password=customer.temp_password if not customer.password_changed else None,  # ⭐ INCLUDE
        date_of_birth=customer.date_of_birth,
        gender=customer.gender,
        height=customer.height,
        weight=customer.weight,
        bmi=customer.bmi,
        bmi_category=customer.bmi_category,
        bmr=customer.bmr,
        ideal_weight=customer.ideal_weight,
        daily_calories=customer.daily_calories,
        created_at=customer.created_at,
        updated_at=customer.updated_at,
    )
```

#### 3. Update LIST Customers Endpoint

```python
@router.get("/", response_model=CustomerListResponse)
async def list_customers(
    branch_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """List all customers - STAFF ONLY"""
    
    query = db.query(Customer)
    
    # Filter by branch if specified
    if branch_id:
        query = query.filter(Customer.branch_id == branch_id)
    
    # Search by name or phone
    if search:
        query = query.filter(
            (Customer.full_name.ilike(f"%{search}%")) | 
            (Customer.phone.ilike(f"%{search}%"))
        )
    
    total = query.count()
    customers = query.offset(skip).limit(limit).all()
    
    # Build response items
    items = []
    for customer in customers:
        items.append(CustomerResponse(
            id=customer.id,
            full_name=customer.full_name,
            phone=customer.phone,
            email=customer.email,
            branch_id=customer.branch_id,
            branch_name=customer.branch.name if customer.branch else None,
            qr_code=customer.qr_code,
            is_active=customer.is_active,
            password_changed=customer.password_changed,
            temp_password=customer.temp_password if not customer.password_changed else None,  # ⭐ INCLUDE
            date_of_birth=customer.date_of_birth,
            gender=customer.gender,
            height=customer.height,
            weight=customer.weight,
            bmi=customer.bmi,
            bmi_category=customer.bmi_category,
            bmr=customer.bmr,
            ideal_weight=customer.ideal_weight,
            daily_calories=customer.daily_calories,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        ))
    
    return CustomerListResponse(
        items=items,
        total=total,
        skip=skip,
        limit=limit
    )
```

---

## 📦 UPDATE RESPONSE SCHEMA

### File: `backend/app/schemas/customer.py`

```python
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import date, datetime

class CustomerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[EmailStr]
    branch_id: int
    branch_name: Optional[str]
    qr_code: str
    is_active: bool
    password_changed: bool
    temp_password: Optional[str] = None  # ⭐ ADD THIS FIELD
    
    # Personal Info
    date_of_birth: Optional[date]
    gender: Optional[str]
    address: Optional[str]
    national_id: Optional[str]
    health_notes: Optional[str]
    
    # Health Metrics
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    bmi_category: Optional[str]
    bmr: Optional[float]
    ideal_weight: Optional[float]
    daily_calories: Optional[int]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

---

## 🔐 UPDATE PASSWORD CHANGE ENDPOINT

### File: `backend/app/api/v1/endpoints/client_auth.py`

```python
@router.post("/change-password")
async def change_password(
    password_change: PasswordChange,
    db: Session = Depends(get_db),
    current_customer: Customer = Depends(get_current_customer),
):
    """Change customer password - CLIENT ONLY"""
    
    # Verify old password
    if not verify_password(password_change.old_password, current_customer.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Validate new password
    if len(password_change.new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters")
    
    # Update password
    current_customer.password = hash_password(password_change.new_password)
    current_customer.password_changed = True  # ⭐ Mark as changed
    current_customer.temp_password = None  # ⭐ Clear temp password
    
    db.commit()
    
    return {"message": "Password changed successfully"}
```

---

## 🌱 UPDATE SEED DATA

### File: `backend/seed.py`

```python
def create_customers(db: Session):
    """Create 150 sample customers"""
    
    print("\n🔄 Creating 150 customers...")
    
    for i in range(1, 151):
        branch_id = ((i - 1) % 5) + 1  # Distribute across 5 branches
        
        # Generate temporary password
        temp_password = generate_temp_password()  # e.g., "AB12CD"
        
        # Create customer
        customer = Customer(
            full_name=fake_names[i-1],
            phone=fake_phones[i-1],
            email=f"customer{i}@example.com",
            password=hash_password(temp_password),  # Store hashed
            temp_password=temp_password,  # ⭐ Store plain for staff
            password_changed=False,  # ⭐ Not changed yet
            branch_id=branch_id,
            qr_code=f"CUST-{i:03d}-{branch_names[branch_id-1].upper().replace(' ', '')}",
            is_active=True,
            date_of_birth=fake.date_of_birth(minimum_age=18, maximum_age=60),
            gender=random.choice(["MALE", "FEMALE"]),
            height=round(random.uniform(150, 195), 2),
            weight=round(random.uniform(50, 120), 2),
            address=fake.address(),
            national_id=fake.ssn() if random.random() > 0.3 else None,
            health_notes=random.choice([None, "Asthma", "Knee injury", "Back pain"]),
            created_at=fake.date_time_between(start_date='-1y', end_date='now'),
        )
        
        # Calculate health metrics
        if customer.height and customer.weight:
            customer.bmi = round(customer.weight / ((customer.height / 100) ** 2), 2)
            customer.bmi_category = get_bmi_category(customer.bmi)
            
            if customer.date_of_birth and customer.gender:
                age = calculate_age(customer.date_of_birth)
                customer.bmr = calculate_bmr(customer.weight, customer.height, age, customer.gender)
                customer.ideal_weight = calculate_ideal_weight(customer.height, customer.gender)
                customer.daily_calories = calculate_daily_calories(customer.bmr, "MODERATE")
        
        db.add(customer)
        
        # Print for reference
        print(f"  Customer {i:3d}: {customer.full_name:30s} | Phone: {customer.phone} | Password: {temp_password}")
    
    db.commit()
    print("✅ Customers created successfully!\n")
```

---

## 🧪 TESTING STEPS

### 1. Run Database Migration
```bash
cd backend
alembic upgrade head
```

### 2. Re-seed Database
```bash
cd backend
python seed.py
```

### 3. Test API Endpoint
```bash
# Login as receptionist first
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "receptionist1",
    "password": "receptionist123"
  }'

# Get customer details
curl -X GET "http://localhost:8000/api/customers/1" \
  -H "Authorization: Bearer <your_token_here>"
```

**Expected Response:**
```json
{
  "id": 1,
  "full_name": "Mohamed Salem",
  "phone": "01077827638",
  "email": "customer1@example.com",
  "temp_password": "AB12CD",  // ⭐ SHOULD BE PRESENT
  "password_changed": false,
  "qr_code": "CUST-001-DRAGON",
  "is_active": true,
  "branch_id": 1,
  "branch_name": "Dragon Club",
  ...
}
```

### 4. Test in Staff App
1. Login as receptionist
2. Go to Customers screen
3. Tap on any customer
4. Verify temporary password is displayed (e.g., "AB12CD")
5. Test copy and share buttons

### 5. Test Client App Flow
1. Login with phone and temp password
2. Should be forced to change password screen
3. Change password
4. Verify `password_changed` becomes `true`
5. Verify `temp_password` becomes `null`
6. Try logging in again with temp password - should FAIL
7. Login with new password - should SUCCEED

---

## ✅ SUCCESS CRITERIA

After these changes:
- [x] Database has `temp_password` and `password_changed` columns
- [x] New customers get temp passwords stored
- [x] Staff can see temp passwords in API responses
- [x] Staff app displays temp passwords correctly
- [x] Temp passwords are cleared after customer changes password
- [x] Security: Only staff can see temp passwords
- [x] Security: Customers cannot see their own temp password
- [x] First-time login flow works end-to-end

---

## 🔒 SECURITY NOTES

1. **Temp passwords are ONLY visible to staff**
   - Customers CANNOT see their temp password via client API
   - Only returned in staff endpoints with staff authentication

2. **Temp passwords are cleared after first change**
   - Once `password_changed = True`, temp_password is set to `NULL`
   - Cannot be recovered after clearing

3. **Audit trail**
   - Consider logging when temp password is viewed
   - Track password change events

4. **Future enhancement**
   - Add `temp_password_expires_at` field
   - Auto-expire temp passwords after 30 days
   - Force password reset if expired

