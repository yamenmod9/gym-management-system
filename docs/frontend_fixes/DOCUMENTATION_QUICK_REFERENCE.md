# 🎴 DOCUMENTATION QUICK REFERENCE

**Bookmark this page for instant access**

---

## 📂 NEW ORGANIZED STRUCTURE

```
📁 backend_fixes/
   ├── QUICK_FIX_GUIDE.md              (120 lines - 5 min read)
   └── ALL_BACKEND_FIXES_REQUIRED.md   (590 lines - 20 min read)

📁 documentation/
   ├── README.md                       (140 lines - Quick start)
   ├── INDEX.md                        (280 lines - Navigation)
   ├── APP_DOCUMENTATION.md            (450 lines - Full docs)
   └── PROJECT_STATUS.md               (220 lines - Status)

📄 READ_ME_FIRST.md                    (25 lines - Entry point)
```

**Total: 7 essential files** (was 200+)

---

## 🚀 QUICK COMMANDS

```bash
# Run Staff App
flutter run --flavor staff

# Run Client App
flutter run --flavor client

# Clean & Rebuild
flutter clean && flutter pub get && flutter run --flavor staff
```

---

## 🔐 LOGIN CREDENTIALS

### Staff App
```
Email: receptionist.branch1@example.com
Password: password123
```

### Client App
```
Phone: 01077827638
Temp Password: RX04AF
```

---

## 📖 WHICH FILE DO I READ?

| Your Goal | Read This File |
|-----------|----------------|
| 🚀 Run the app quickly | `documentation/README.md` |
| 🔧 Fix backend issues | `backend_fixes/QUICK_FIX_GUIDE.md` |
| 📱 Understand all features | `documentation/APP_DOCUMENTATION.md` |
| 📊 Check project status | `documentation/PROJECT_STATUS.md` |
| 🗺️ Navigate documentation | `documentation/INDEX.md` |
| ❓ I'm lost, help! | `READ_ME_FIRST.md` |

---

## ⚡ TOP 3 BACKEND FIXES

### 1️⃣ Registration Fix (Line 2)
```python
staff_branch_id = int(staff_branch_id) if staff_branch_id else None
requested_branch_id = int(requested_branch_id) if requested_branch_id else None
```

### 2️⃣ Check-in Fix (Line 5)
```python
if qr_code and 'customer_id:' in qr_code:
    customer_id = int(qr_code.split('customer_id:')[1])
customer = Customer.query.get(customer_id)
branch_id = customer.branch_id  # Use customer's branch
```

### 3️⃣ QR Code Fix (Line 1)
```python
customer.qr_code = f"customer_id:{customer.id}"
```

**See full guide:** `backend_fixes/ALL_BACKEND_FIXES_REQUIRED.md`

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

### Test Client Login
```bash
curl -X POST http://localhost:5000/api/client/auth/login \
  -H "Content-Type: application/json" \
  -d '{"phone":"01077827638","password":"RX04AF"}'
```

---

## 📊 PROJECT STATUS

| Component | Status | Progress |
|-----------|--------|----------|
| Flutter Staff App | ✅ Complete | 100% |
| Flutter Client App | ✅ Complete | 100% |
| UI/UX | ✅ Complete | 100% |
| Documentation | ✅ Complete | 100% |
| Backend API | ❌ Needs fixes | 60% |

---

## 🎯 FEATURES AT A GLANCE

### Staff App
- ✅ Dashboard with metrics
- ✅ Customer management
- ✅ QR code scanner
- ✅ Subscription activation
- ✅ Settings

### Client App
- ✅ Login with temp password
- ✅ QR code display
- ✅ Subscription status
- ✅ Health metrics
- ✅ Profile management

---

## 🔗 QUICK LINKS

- **Entry Point:** `READ_ME_FIRST.md`
- **Quick Start:** `documentation/README.md`
- **Navigation:** `documentation/INDEX.md`
- **Full Docs:** `documentation/APP_DOCUMENTATION.md`
- **Status:** `documentation/PROJECT_STATUS.md`
- **Backend Quick Fix:** `backend_fixes/QUICK_FIX_GUIDE.md`
- **Backend Complete:** `backend_fixes/ALL_BACKEND_FIXES_REQUIRED.md`

---

## ✅ CHECKLIST

### To Run App
- [ ] Backend running on `http://localhost:5000`
- [ ] Flutter installed
- [ ] Device/emulator connected
- [ ] Run `flutter run --flavor staff`

### To Fix Backend
- [ ] Read `backend_fixes/QUICK_FIX_GUIDE.md`
- [ ] Apply 3 critical fixes
- [ ] Test with curl commands
- [ ] Verify all endpoints work

### To Test Features
- [ ] Login as staff
- [ ] Register new customer
- [ ] Scan QR code
- [ ] Login as client
- [ ] View subscription

---

## 🚨 CURRENT BLOCKERS

All blockers are **backend-only**:
1. ❌ Customer registration blocked
2. ❌ Check-in system not working
3. ❌ QR codes showing null
4. ❌ Coins not decreasing
5. ❌ Temp password not visible

**Flutter is 100% ready!**

---

## 📞 GET HELP

| Issue Type | Solution |
|------------|----------|
| Can't run app | `documentation/README.md` |
| Backend error | `backend_fixes/QUICK_FIX_GUIDE.md` |
| Need features list | `documentation/APP_DOCUMENTATION.md` |
| Check progress | `documentation/PROJECT_STATUS.md` |
| Lost/confused | `documentation/INDEX.md` |

---

## 🎨 COLOR CODES

- ✅ = Complete/Working
- ❌ = Issue/Needs fix
- ⏳ = Pending/Waiting
- ⚡ = Quick/Fast
- 📖 = Documentation
- 🔧 = Technical/Fix

---

## 💡 PRO TIPS

1. **Start with:** `READ_ME_FIRST.md`
2. **For urgent fix:** Go to `backend_fixes/QUICK_FIX_GUIDE.md`
3. **All docs have:** Table of contents at top
4. **Use emojis:** To quickly scan sections
5. **Lost?** Check `documentation/INDEX.md`

---

## 📏 FILE SIZES

| File | Lines | Read Time |
|------|-------|-----------|
| READ_ME_FIRST.md | 25 | 1 min |
| QUICK_FIX_GUIDE.md | 120 | 5 min |
| README.md | 140 | 7 min |
| PROJECT_STATUS.md | 220 | 10 min |
| INDEX.md | 280 | 12 min |
| APP_DOCUMENTATION.md | 450 | 20 min |
| ALL_BACKEND_FIXES | 590 | 25 min |

---

**Last Updated:** February 16, 2026  
**Status:** Documentation Complete  
**Next:** Apply backend fixes

---

**🎉 START HERE:** [`READ_ME_FIRST.md`](READ_ME_FIRST.md)

---

**END OF QUICK REFERENCE**

