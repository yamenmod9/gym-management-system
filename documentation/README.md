# 🚀 QUICK START GUIDE

**Get up and running in 5 minutes**

---

## 📋 PREREQUISITES

- Flutter SDK installed
- Backend API running on `http://localhost:5000`
- Android device or emulator

---

## 🏃 RUNNING THE APPS

### Option 1: Staff App
```bash
cd C:\Programming\Flutter\gym_frontend
flutter run --flavor staff
```

### Option 2: Client App
```bash
cd C:\Programming\Flutter\gym_frontend
flutter run --flavor client
```

### Option 3: Both Apps (2 terminals)
Terminal 1:
```bash
flutter run --flavor staff
```

Terminal 2:
```bash
flutter run --flavor client
```

---

## 🔑 LOGIN CREDENTIALS

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

## 🔧 IF SOMETHING DOESN'T WORK

### Backend Issues?
Check: `backend_fixes/ALL_BACKEND_FIXES_REQUIRED.md`

### Need App Info?
Check: `documentation/APP_DOCUMENTATION.md`

### Want Status Update?
Check: `documentation/PROJECT_STATUS.md`

---

## 📱 TESTING FEATURES

### Staff App
1. Login with credentials above
2. Go to "Customers" tab
3. Try registering a new customer
4. Try scanning QR code (if backend fixed)

### Client App
1. Login with phone + temp password
2. Change password (first-time login)
3. View dashboard
4. See QR code

---

## ⚠️ KNOWN ISSUES

**All issues are in the BACKEND** (Flutter is complete)

- Customer registration may fail
- Check-in may not work
- QR codes may show as null
- Coins may not decrease

**Fix:** Apply backend fixes from `backend_fixes/` folder

---

## 📚 FULL DOCUMENTATION

See `documentation/` folder for complete guides:
- `APP_DOCUMENTATION.md` - Features & API
- `PROJECT_STATUS.md` - Current status
- `README.md` - This file

---

## 🐛 TROUBLESHOOTING

### App won't build?
```bash
flutter clean
flutter pub get
flutter run --flavor staff
```

### Backend connection error?
- Make sure backend is running on `http://localhost:5000`
- Check `lib/core/constants/api_constants.dart`

### Can't login?
- Check backend is running
- Check credentials are correct
- Check backend seeded data

---

## ✅ SUCCESS CHECKLIST

- [ ] Backend running
- [ ] Flutter app runs
- [ ] Can login
- [ ] Can see dashboard
- [ ] No errors in console

---

**That's it! You're ready to go.** 🎉

For detailed info, see other files in `documentation/` folder.

---

**END OF QUICK START**

