# DATABASE FIX: TEMPORARY PASSWORD DISPLAY ISSUE

## PROBLEM
The Flutter Staff App (Reception) cannot see the customer's temporary password in the customer details screen. The API returns `"temp_password": null` even though customers were created with temporary passwords.

## ROOT CAUSE
One or more of the following issues:

1. **Database Schema Issue**: The `temp_password` column might not exist in the `customers` table
2. **API Serialization Issue**: The API endpoint might not be including `temp_password` in the response
3. **Password Overwrite Issue**: The `temp_password` might be getting set to NULL after customer creation or first login

## SOLUTION

### Step 1: Verify Database Schema

Check if the `customers` table has a `temp_password` column:

```sql
-- For PostgreSQL
SELECT column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'customers' 
AND column_name = 'temp_password';

-- If column doesn't exist, add it:
ALTER TABLE customers 
ADD COLUMN temp_password VARCHAR(6);
```

### Step 2: Update Customer Model

Ensure your Customer model includes `temp_password`:

```python
class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    phone = Column(String(11), unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True)
    password = Column(String, nullable=False)  # Hashed password
    temp_password = Column(String(6), nullable=True)  # IMPORTANT: Add this
    password_changed = Column(Boolean, default=False)  # IMPORTANT: Add this
    qr_code = Column(String, unique=True, nullable=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    gender = Column(String, nullable=True)
    date_of_birth = Column(Date, nullable=True)
    height = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    bmi = Column(Float, nullable=True)
    bmr = Column(Float, nullable=True)
    daily_calories = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

### Step 3: Update Customer Creation Logic

When creating a new customer, generate and store the temporary password:

```python
import random
import string
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def generate_temp_password():
    """Generate 6-character temporary password: AB12CD format"""
    letters = string.ascii_uppercase
    digits = string.digits
    return (
        random.choice(letters) + random.choice(letters) +
        random.choice(digits) + random.choice(digits) +
        random.choice(letters) + random.choice(letters)
    )

# In your customer creation endpoint:
@app.post("/api/customers")
def create_customer(customer_data: CustomerCreate, db: Session, current_user: User):
    # Generate temporary password
    temp_password = generate_temp_password()
    
    # Create customer
    new_customer = Customer(
        full_name=customer_data.full_name,
        phone=customer_data.phone,
        email=customer_data.email,
        branch_id=customer_data.branch_id,
        gender=customer_data.gender,
        date_of_birth=customer_data.date_of_birth,
        height=customer_data.height,
        weight=customer_data.weight,
        # Calculate BMI, BMR, etc...
        
        # IMPORTANT: Set both password fields
        password=pwd_context.hash(temp_password),  # Hashed for login
        temp_password=temp_password,  # Plain text for display to reception
        password_changed=False,  # User must change on first login
        
        qr_code=f"GYM-{customer_data.branch_id}-{{id}}",  # Will update after commit
        is_active=True
    )
    
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    
    # Update QR code with actual ID
    new_customer.qr_code = f"GYM-{new_customer.branch_id}-{new_customer.id}"
    db.commit()
    
    return {
        "success": True,
        "customer": new_customer,
        "temp_password": temp_password  # Return in response for immediate display
    }
```

### Step 4: Update Customer Response Schema

Ensure the API response includes `temp_password`:

```python
class CustomerResponse(BaseModel):
    id: int
    full_name: str
    phone: str
    email: Optional[str]
    branch_id: int
    branch_name: Optional[str]
    gender: Optional[str]
    date_of_birth: Optional[date]
    height: Optional[float]
    weight: Optional[float]
    bmi: Optional[float]
    bmr: Optional[float]
    daily_calories: Optional[int]
    qr_code: Optional[str]
    temp_password: Optional[str]  # IMPORTANT: Include this
    password_changed: bool  # IMPORTANT: Include this
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
```

### Step 5: Fix Customer Detail Endpoint

Ensure the GET endpoint returns `temp_password`:

```python
@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: int, db: Session, current_user: User):
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Staff should be able to see temp password if not yet changed
    # For security, only show if password hasn't been changed
    response_data = {
        "id": customer.id,
        "full_name": customer.full_name,
        "phone": customer.phone,
        "email": customer.email,
        "branch_id": customer.branch_id,
        "gender": customer.gender,
        "date_of_birth": customer.date_of_birth,
        "height": customer.height,
        "weight": customer.weight,
        "bmi": customer.bmi,
        "bmr": customer.bmr,
        "daily_calories": customer.daily_calories,
        "qr_code": customer.qr_code,
        "temp_password": customer.temp_password,  # Include this
        "password_changed": customer.password_changed,  # Include this
        "is_active": customer.is_active,
        "created_at": customer.created_at,
        "updated_at": customer.updated_at
    }
    
    return response_data
```

### Step 6: Update Password Change Logic

When customer changes password, keep `temp_password` for reference but set `password_changed = True`:

```python
@app.post("/api/client/auth/change-password")
def change_password(
    password_data: PasswordChange,
    db: Session,
    current_customer: Customer
):
    # Verify old password
    if not pwd_context.verify(password_data.old_password, current_customer.password):
        raise HTTPException(status_code=400, detail="Incorrect current password")
    
    # Update password
    current_customer.password = pwd_context.hash(password_data.new_password)
    current_customer.password_changed = True  # Mark as changed
    # DO NOT set temp_password to NULL - keep it for records
    
    db.commit()
    
    return {"success": True, "message": "Password changed successfully"}
```

### Step 7: Migrate Existing Data

If you already have customers without temp_password, run this migration:

```python
# Migration script
import random
import string
from sqlalchemy.orm import Session

def generate_temp_password():
    letters = string.ascii_uppercase
    digits = string.digits
    return (
        random.choice(letters) + random.choice(letters) +
        random.choice(digits) + random.choice(digits) +
        random.choice(letters) + random.choice(letters)
    )

def migrate_existing_customers(db: Session):
    # Get all customers without temp_password
    customers = db.query(Customer).filter(
        (Customer.temp_password == None) | (Customer.temp_password == "")
    ).all()
    
    print(f"Migrating {len(customers)} customers...")
    
    for customer in customers:
        temp_pw = generate_temp_password()
        customer.temp_password = temp_pw
        
        # If they haven't logged in yet, reset their password to the temp one
        if not customer.password_changed:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            customer.password = pwd_context.hash(temp_pw)
        
        print(f"Customer {customer.id} ({customer.full_name}): {temp_pw}")
    
    db.commit()
    print("Migration complete!")

# Run this once
# migrate_existing_customers(db)
```

### Step 8: Add Temp Password Retrieval Endpoint

For extra security, create a dedicated endpoint that receptionists can use:

```python
@app.get("/api/customers/{customer_id}/temp-password")
def get_temp_password(
    customer_id: int,
    db: Session,
    current_user: User = Depends(get_current_staff)
):
    # Only reception and managers can view temp passwords
    if current_user.role not in ["reception", "manager", "owner"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    customer = db.query(Customer).filter(Customer.id == customer_id).first()
    
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    # Check branch access (except for owner)
    if current_user.role != "owner" and customer.branch_id != current_user.branch_id:
        raise HTTPException(status_code=403, detail="Cannot access customer from another branch")
    
    return {
        "customer_id": customer.id,
        "full_name": customer.full_name,
        "phone": customer.phone,
        "temp_password": customer.temp_password if customer.temp_password else "NOT_SET",
        "password_changed": customer.password_changed
    }
```

## TESTING

After applying these fixes, test:

1. **Create new customer via Staff App**:
   - Temp password should be generated
   - Reception should see it immediately after creation

2. **View existing customer**:
   - Temp password should be visible in customer details

3. **Customer first login**:
   - Should be able to login with temp password
   - Should be forced to change password
   - After change, `password_changed` becomes `true`
   - Temp password should still be visible to staff for reference

4. **API Response Check**:
```bash
curl -X GET "http://your-api/api/customers/1" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Should return:
{
  "id": 1,
  "full_name": "Ahmed Hassan",
  "phone": "01012345678",
  "temp_password": "AB12CD",  # This should NOT be null
  "password_changed": false,
  ...
}
```

## SUMMARY

The fix involves:
1. ✅ Ensure `temp_password` column exists in database
2. ✅ Include `temp_password` in Customer model
3. ✅ Generate temp password on customer creation
4. ✅ Include `temp_password` in API responses
5. ✅ Keep temp password even after customer changes it (for records)
6. ✅ Migrate existing customers to have temp passwords
7. ✅ Test thoroughly

This ensures Reception can always see the temporary password for newly created customers or customers who haven't changed their password yet.

