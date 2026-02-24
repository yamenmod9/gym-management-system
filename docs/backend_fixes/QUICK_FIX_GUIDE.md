# ⚡ QUICK FIX GUIDE

**For Backend Developers - 10 Minute Read**

---

## 🔥 TOP 3 CRITICAL FIXES

### 1. Customer Registration (2 minutes)
**Problem:** "Cannot register customer for another branch" error

**Fix:** Add before branch validation:
```python
staff_branch_id = int(staff_branch_id) if staff_branch_id is not None else None
requested_branch_id = int(requested_branch_id) if requested_branch_id is not None else None
```

### 2. Check-in System (5 minutes)
**Problem:** "qr_code is required" or "branch_id is required"

**Fix:** Extract customer_id from QR code, use customer's branch:
```python
customer_id = data.get('customer_id')
qr_code = data.get('qr_code')

if qr_code and 'customer_id:' in qr_code:
    customer_id = int(qr_code.split('customer_id:')[1])

customer = Customer.query.get(customer_id)
branch_id = customer.branch_id  # Use customer's branch, not from request
```

### 3. QR Code Generation (3 minutes)
**Problem:** QR codes are null

**Fix:** Generate on customer creation:
```python
customer.qr_code = f"customer_id:{customer.id}"
```

---

## 📋 ALL FIXES AT A GLANCE

| Issue | Location | Fix Time | Priority |
|-------|----------|----------|----------|
| Registration blocked | customer_routes.py | 2 min | CRITICAL |
| Check-in fails | checkin_routes.py | 5 min | CRITICAL |
| QR codes null | customer model | 3 min | HIGH |
| Coins not decreasing | checkin handler | 5 min | HIGH |
| Temp password hidden | customer endpoint | 3 min | MEDIUM |
| Branch validation | all routes | 10 min | HIGH |

---

## 🧪 TEST COMMANDS

### Test Registration
```bash
curl -X POST http://localhost:5000/api/customers/register \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"full_name":"Test","phone":"01234567890","branch_id":1,"gender":"male","age":25,"weight":75,"height":1.75}'
```

### Test Check-in
```bash
curl -X POST http://localhost:5000/api/checkins \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"qr_code":"customer_id:115"}'
```

---

## ✅ QUICK CHECKLIST

- [ ] Registration: Add int() conversion
- [ ] Check-in: Extract from QR, use customer.branch_id
- [ ] QR Code: Generate f"customer_id:{id}"
- [ ] Subscription: Decrease coins on check-in
- [ ] Temp Password: Return if not changed
- [ ] Test all endpoints

---

**See ALL_BACKEND_FIXES_REQUIRED.md for detailed implementations**

