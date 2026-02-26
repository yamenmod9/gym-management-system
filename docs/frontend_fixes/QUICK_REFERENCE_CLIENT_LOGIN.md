# 🎯 QUICK REFERENCE - CLIENT APP LOGIN SYSTEM

## 📱 How It Works

### For Reception Staff:

1. **Register New Customer:**
   - Customer gets phone + temporary password (e.g., "AB12CD")
   - Give credentials to customer
   - Tell them to download gym member app

2. **View Customer Credentials:**
   - Go to "All Customers" screen
   - Click on customer to expand
   - See login credentials section
   - Copy password if needed (only visible if not changed)

### For Gym Members:

1. **First Login:**
   - Open gym member app
   - Enter phone OR email
   - Enter temporary password from reception
   - App forces password change
   - Set new password (min 6 characters)

2. **Regular Login (After First Time):**
   - Enter phone OR email
   - Enter YOUR new password (not temporary one)
   - Access app normally

---

## 🔑 Login Credentials Format

**What Customer Gets:**
```
Login: 01234567890 (phone) or email@example.com
Password: AB12CD (temporary)
```

**What They Can Use:**
- Phone number: `01234567890`, `+201234567890`, `012-345-67890` (all work)
- Email: `customer@example.com`
- Password: Temporary password first time, then their own password

---

## 🎨 UI Flow

### Client App (Customer Side)

**Welcome Screen:**
```
┌─────────────────────────────────────┐
│    🏋️ Gym Member Portal             │
│                                     │
│  Login to access your membership    │
│                                     │
│  [Phone Number or Email]            │
│  Use credentials from reception     │
│                                     │
│  [Password]                         │
│  First-time? Use temporary password │
│                                     │
│  [      Login      ]                │
│                                     │
│  ─────── First Time? ───────        │
│                                     │
│  ℹ️ New Member?                     │
│  Visit reception to get login       │
│  credentials                        │
└─────────────────────────────────────┘
```

**First Login → Password Change (Forced):**
```
┌─────────────────────────────────────┐
│  ← (Back disabled) Set New Password │
│                                     │
│  ⚠️ Please change your temporary   │
│     password before continuing      │
│                                     │
│  [Temporary Password]               │
│                                     │
│  [New Password]                     │
│  Minimum 6 characters               │
│                                     │
│  [Confirm New Password]             │
│                                     │
│  [   Change Password   ]            │
└─────────────────────────────────────┘
```

### Reception App (Staff Side)

**Customer List:**
```
┌─────────────────────────────────────────┐
│  Ahmed Hassan                          │
│  ID: 123 • Active Subscription ✅       │
│                                         │
│  Click to view details ▼                │
└─────────────────────────────────────────┘
   ↓ (Expanded)
┌─────────────────────────────────────────┐
│  📞 Phone: 01234567890 📋               │
│  📧 Email: ahmed@example.com 📋         │
│  🎫 QR Code: GYM-000123 📋              │
│                                         │
│  ┌───────────────────────────────────┐ │
│  │ 🔐 Client App Credentials         │ │
│  ├───────────────────────────────────┤ │
│  │ Login: 01234567890                │ │
│  │ Password: AB12CD 📋               │ │
│  │ ⚠️ First-time login - not         │ │
│  │    changed yet                    │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**After Password Changed:**
```
│  ┌───────────────────────────────────┐ │
│  │ 🔐 Client App Credentials         │ │
│  ├───────────────────────────────────┤ │
│  │ Login: 01234567890                │ │
│  │ Password: •••••••• (Changed)      │ │
│  │ ✅ Password has been changed      │ │
│  │    by user                        │ │
│  └───────────────────────────────────┘ │
```

---

## 🧪 Testing Scenarios

### Scenario 1: New Customer Registration

**Reception:**
1. Login: `reception1` / `reception123`
2. Click "Register Customer"
3. Fill form (name, phone, email, etc.)
4. Submit
5. **Get:** Temporary password (e.g., "XY34AB")
6. **Write down:** Phone + Password
7. **Give to customer:** These credentials

**Customer:**
1. Receives: `01234567890` + `XY34AB`
2. Downloads gym app
3. Opens app
4. Enters phone: `01234567890`
5. Enters password: `XY34AB`
6. Clicks Login
7. **Redirected to:** Password change screen (forced)
8. Enters temporary password: `XY34AB`
9. Enters new password: `mypassword123`
10. Confirms: `mypassword123`
11. Submits
12. **Success:** Home screen opens

### Scenario 2: Regular Login (After Password Change)

**Customer:**
1. Opens app
2. Enters phone: `01234567890`
3. Enters password: `mypassword123` (NOT temporary)
4. Clicks Login
5. **Success:** Directly to home screen

### Scenario 3: Reception Views Customer Status

**Reception:**
1. Click "All Customers"
2. Find customer "Ahmed Hassan"
3. Expand card
4. **See:** 
   - If password not changed: `Password: AB12CD` ⚠️
   - If password changed: `Password: ••••••••` ✅

### Scenario 4: Password Forgotten

**Customer:**
1. Forgot password
2. Contacts reception

**Reception:**
1. Can NOT see customer's password (security)
2. Must reset in backend OR
3. Register customer again with new temp password

---

## 🚀 Backend Endpoints Used

### Client App:
- `POST /api/clients/auth/login` - Login
- `POST /api/clients/change-password` - Change password
- `GET /api/clients/profile` - Get profile
- `GET /api/clients/qr` - Get QR code
- `GET /api/clients/entry-history` - Entry history

### Reception App:
- `POST /api/customers/register` - Register (returns temp password)
- `GET /api/customers/list-with-credentials` - View all customers
- `POST /api/subscriptions/activate` - Activate subscription

---

## 🔒 Security Features

1. **Passwords:** Hashed in database (bcrypt)
2. **JWT Tokens:** Secure authentication
3. **Token Type:** Client tokens separate from staff tokens
4. **Phone Normalization:** Auto-removes spaces/dashes
5. **Password Requirements:** Minimum 6 characters
6. **First-Time Security:** Forces password change on first login
7. **No Password Exposure:** Reception cannot see changed passwords

---

## 📋 Backend Implementation Files

**Main Prompt:** `BACKEND_IMPLEMENTATION_PROMPT_COMPLETE.md`
- Contains all endpoint implementations
- Database schema changes
- Testing commands
- Security guidelines

**Status Doc:** `CLIENT_APP_READY_FOR_BACKEND.md`
- Current implementation status
- Testing workflow
- Known issues

---

## ✅ Checklist Before Testing

**Backend:**
- [ ] Database columns added (temporary_password, password_changed, etc.)
- [ ] All client endpoints implemented
- [ ] Customer registration returns temporary password
- [ ] Subscription activation fixed
- [ ] CORS enabled for mobile app

**Frontend:**
- [✅] Client login screen
- [✅] Password change screen
- [✅] Phone normalization
- [✅] Reception customer list
- [✅] Credential display

**Testing:**
- [ ] Create test customer from reception
- [ ] Note temporary password
- [ ] Login from client app
- [ ] Change password
- [ ] Login again with new password
- [ ] Verify subscription activation works

---

## 🐛 Troubleshooting

**Issue:** Login fails
- Check phone number format (remove spaces)
- Verify temporary password is correct
- Check backend logs

**Issue:** Password change fails
- Ensure current password is correct
- New password must be 6+ characters
- Cannot reuse current password

**Issue:** Cannot see customer credentials
- Make sure customer has temporary_password field
- Check backend returns password_changed flag
- Verify customer exists in database

**Issue:** Subscription activation fails
- Check backend logs
- Verify service_id exists
- Check foreign key constraints
- Ensure branch_id matches

---

## 📞 Support

**Backend API:** `https://yamenmod91.pythonanywhere.com`

**Test Accounts:**
- Reception: `reception1` / `reception123`
- Manager: `manager1` / `manager123`
- Owner: `owner` / `owner123`

**For Backend Issues:**
- Check `BACKEND_IMPLEMENTATION_PROMPT_COMPLETE.md`
- Test endpoints with curl commands
- Review error logs on PythonAnywhere

**For Frontend Issues:**
- Check Flutter console for errors
- Verify API service configuration
- Check network connectivity

---

**Everything is ready! Just waiting for backend implementation! 🎉**

