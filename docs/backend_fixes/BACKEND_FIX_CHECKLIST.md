# ✅ BACKEND FIX CHECKLIST

**Date:** February 16, 2026  
**Print this and check off as you go!**

---

## 📋 PRE-IMPLEMENTATION

- [ ] Located `CLAUDE_BACKEND_FIX_PROMPT_FEB16.md`
- [ ] Read through the 3 issues
- [ ] Opened Claude Sonnet 4.5
- [ ] Backend server is running
- [ ] Database is accessible

---

## 🔨 IMPLEMENTATION

### Issue 1: Customer Registration
- [ ] Found `POST /api/customers/register` endpoint
- [ ] Updated branch validation logic
- [ ] Allows same-branch registration
- [ ] Still blocks cross-branch for receptionists
- [ ] Tested with curl command
- [ ] Returns temp_password in response
- [ ] Commits to database properly

### Issue 2: Subscription Display
- [ ] Added `calculate_display_metrics()` function
- [ ] Function handles coin-based subscriptions
- [ ] Function handles time-based subscriptions
- [ ] Function handles session-based subscriptions
- [ ] Updated `GET /api/subscriptions/customer/{id}` endpoint
- [ ] Response includes `display_metric`
- [ ] Response includes `display_value`
- [ ] Response includes `display_label`
- [ ] Response includes `validity_type`
- [ ] Tested with curl command

### Issue 3: Check-in Validation
- [ ] Found `POST /api/attendance` endpoint
- [ ] Reads `branch_id` from request
- [ ] Uses `branch_id` in attendance record
- [ ] Validates required fields
- [ ] Handles coin deduction
- [ ] Handles session deduction
- [ ] Commits to database properly
- [ ] Tested with curl command

---

## 🧪 TESTING

### Test 1: Registration
- [ ] Opened terminal
- [ ] Got receptionist JWT token
- [ ] Ran curl command for registration
- [ ] Response status = 201
- [ ] Response includes customer ID
- [ ] Response includes temp_password
- [ ] Response includes qr_code
- [ ] No "another branch" error
- [ ] Customer visible in database

### Test 2: Subscription Display
- [ ] Got customer JWT token
- [ ] Ran curl command for subscriptions
- [ ] Response includes `display_metric`
- [ ] Coin subscription shows `"display_metric": "coins"`
- [ ] Response includes `"display_value": 50` (or actual coins)
- [ ] Response includes `"display_label": "50 Coins"`
- [ ] Time subscription shows `"display_metric": "time"`
- [ ] Values are correct and non-zero

### Test 3: Check-in
- [ ] Got receptionist JWT token
- [ ] Ran curl command for check-in
- [ ] Response status = 201
- [ ] Response includes attendance ID
- [ ] Response includes customer_id
- [ ] Response includes branch_id
- [ ] No "branch_id required" error
- [ ] Attendance record in database

---

## 📱 FLUTTER APP TESTING

### Staff App
- [ ] Opened staff app
- [ ] Logged in as receptionist
- [ ] Navigated to "Add Customer"
- [ ] Filled in customer form
- [ ] Clicked "Register"
- [ ] Saw success message
- [ ] Customer appeared in list
- [ ] Opened QR scanner
- [ ] Scanned customer QR code
- [ ] Customer info displayed
- [ ] Clicked "Check-In"
- [ ] Saw success message

### Client App
- [ ] Opened client app
- [ ] Logged in with test customer
- [ ] Dashboard loaded successfully
- [ ] Subscription card shows correct type
- [ ] If coins: Shows "X Coins Remaining"
- [ ] If time: Shows "X days Remaining"
- [ ] Values are correct (not 0)
- [ ] QR code displays
- [ ] Can navigate all screens
- [ ] Plan screen shows correct info

---

## 🗄️ DATABASE VERIFICATION

### Check Tables
- [ ] customers table exists
- [ ] subscriptions table exists
- [ ] attendance table exists
- [ ] services table exists

### Check Columns (subscriptions)
- [ ] Has `coins` column
- [ ] Has `remaining_sessions` column
- [ ] Has `initial_coins` column
- [ ] Has `initial_sessions` column
- [ ] Has `is_expired` column

### Check Data
- [ ] New customer inserted
- [ ] Customer has temp_password
- [ ] Customer has qr_code
- [ ] Attendance record inserted
- [ ] Attendance has branch_id
- [ ] Subscription data correct

---

## 🎯 FINAL VERIFICATION

### Critical Features
- [ ] Receptionists can register customers
- [ ] Registration doesn't show "another branch" error
- [ ] QR code scanning works
- [ ] Check-in doesn't show "branch_id required" error
- [ ] Client dashboard shows correct subscription type
- [ ] Coin subscriptions show coin count
- [ ] Time subscriptions show time remaining
- [ ] All data persists in database

### No Regressions
- [ ] Existing customers still work
- [ ] Existing subscriptions still work
- [ ] Login still works
- [ ] Owner dashboard still works
- [ ] Manager dashboard still works
- [ ] All other features untouched

---

## 📊 RESULTS

### Expected Outcomes

#### ✅ Success Indicators:
- Customer registration: **Works**
- QR code check-in: **Works**
- Coin display: **Shows "50 Coins"**
- Time display: **Shows "45 days"**
- Database: **All records saved**
- No errors: **Clean logs**

#### ❌ Failure Indicators:
- Still getting "another branch" error
- Still getting "branch_id required" error
- Dashboard shows "0 days" for coins
- Data not saving to database
- Flutter app crashes

---

## 🔄 IF TESTS FAIL

### Registration Still Fails:
- [ ] Check branch_id validation logic
- [ ] Verify user role is "receptionist"
- [ ] Check user.branch_id vs request.branch_id
- [ ] Enable debug logging
- [ ] Check exact error message

### Display Metrics Missing:
- [ ] Verify function is called
- [ ] Check service.subscription_type value
- [ ] Debug function output
- [ ] Check response structure
- [ ] Verify all fields included

### Check-in Still Fails:
- [ ] Verify branch_id is read from request
- [ ] Check if it's None
- [ ] Verify database column exists
- [ ] Check attendance model
- [ ] Debug request.json

---

## 📝 NOTES SECTION

**Issues Encountered:**
```
(Write any problems you faced here)




```

**Solutions Applied:**
```
(Write how you fixed them here)




```

**Time Taken:**
```
Start: ___:___
End:   ___:___
Total: ___ minutes
```

---

## ✨ COMPLETION

- [ ] All tests passing
- [ ] Flutter app working perfectly
- [ ] No console errors
- [ ] Database has correct data
- [ ] Code committed to repository
- [ ] Documentation updated
- [ ] Ready for production

---

## 🎉 SUCCESS!

**Date Completed:** ___________  
**Completed By:** ___________  
**Total Time:** ___ minutes

**Notes:**
```
(Any final notes or observations)




```

---

**Congratulations! The gym management system is now fully functional! 🎊**

---

## 📞 REFERENCE DOCUMENTS

- `CLAUDE_BACKEND_FIX_PROMPT_FEB16.md` - Full implementation guide
- `BACKEND_FIXES_REQUIRED_FEB16.md` - Technical details
- `ISSUES_SUMMARY_FEB16.md` - Overview summary
- `QUICK_START_BACKEND_FIX.md` - Quick start guide

**Keep this checklist for future reference!**

