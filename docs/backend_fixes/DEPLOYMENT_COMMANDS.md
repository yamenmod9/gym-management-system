# 🚀 PYTHONANYWHERE DEPLOYMENT COMMANDS

**Last Updated:** February 17, 2026  
**Copy and paste these commands exactly as shown**

---

## ⚡ QUICK DEPLOY (Most Common)

If you've already pushed code to GitHub and just need to update PythonAnywhere:

```bash
cd ~/gym-management-system && git pull origin main
```

Then reload web app from Web tab (green "Reload" button).

---

## STEP 1: LOGIN TO PYTHONANYWHERE

1. Go to: https://www.pythonanywhere.com
2. Login with your account
3. Click on **"Consoles"** tab
4. Click **"Bash"** to open a terminal

---

## STEP 2: NAVIGATE TO PROJECT

```bash
cd ~/gym-management-system
```

**Expected output:**
```
(nothing - just changes directory)
```

---

## STEP 3: CHECK CURRENT STATUS (Optional)

```bash
git status
```

**Expected output:**
```
On branch main
Your branch is behind 'origin/main' by X commits
```

---

## STEP 4: PULL LATEST CODE

```bash
git pull origin main
```

**Expected output:**
```
Updating 6982166..1cbe9ca
Fast-forward
 app/routes/customers_routes.py | 10 +++++-----
 app/routes/subscriptions_routes.py | 8 ++++----
 app/routes/checkins_routes.py | 15 ++++++++++++---
 app/models/customer.py | 5 ++++-
 4 files changed, 25 insertions(+), 13 deletions(-)
```

✅ **SUCCESS!** If you see this, the code is updated.

---

## STEP 5: RELOAD WEB APP

### Option A: From Web Interface (Recommended)

1. Click on **"Web"** tab in PythonAnywhere
2. Find your web app (e.g., `yourusername.pythonanywhere.com`)
3. Click the big green **"Reload yourusername.pythonanywhere.com"** button
4. Wait for "Reload complete" message

### Option B: From Console

```bash
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

Replace `yourusername` with your actual PythonAnywhere username.

---

## STEP 6: VERIFY DEPLOYMENT

Test the API by running this curl command (replace `yourusername` with your PythonAnywhere username):

```bash
curl https://yourusername.pythonanywhere.com/api/auth/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"phone":"01511111111","password":"reception123"}'
```

**Expected output:**
```json
{
  "success": true,
  "data": {
    "token": "eyJhbGc...",
    "user": {
      "id": 5,
      "full_name": "Reception One",
      "role": "front_desk",
      "branch_id": 1
    }
  }
}
```

✅ **SUCCESS!** If you see a token, your API is working.

---

## 🆕 FEBRUARY 17, 2026 FIXES

This deployment includes fixes for:
- ✅ Customer registration branch restriction
- ✅ Subscription status display in customers list
- ✅ Health metrics calculation (BMI, age, timestamps)
- ✅ Dynamic subscription display (coins/time/sessions)
- ✅ Check-in branch_id handling

See `documentation/COMPLETE_ISSUE_RESOLUTION.md` for details.

---

## TROUBLESHOOTING

### Error: "fatal: not a git repository"

**Solution:** Clone the repository first:
```bash
cd ~
git clone https://github.com/yamenmod9/gym-management-system.git
cd gym-management-system
```

Then go back to STEP 4.

---

### Error: "Already up-to-date"

**This means:** You already have the latest code!

**Solution:** Just reload the web app (STEP 5).

---

### Error: After reload, still getting errors

**Check the error logs:**

1. Go to **"Web"** tab
2. Scroll down to **"Log files"**
3. Click on **"Error log"**
4. Look for recent errors

Common issues:
- **Module not found:** Run `pip install -r requirements.txt` in console
- **Database error:** Run database migrations (see below)

---

## DATABASE COMMANDS (If Needed)

### Reset Database (⚠️ Deletes all data)

```bash
cd ~/gym-management-system
source venv/bin/activate
rm instance/gym.db
flask db upgrade
python -c "from app import create_app, db; from app.seed import seed_all; app = create_app(); app.app_context().push(); seed_all()"
```

### Check Database Contents

```bash
cd ~/gym-management-system
source venv/bin/activate
python
```

Then in Python:
```python
from app import create_app, db
from app.models import Customer, User

app = create_app()
with app.app_context():
    print(f"Customers: {Customer.query.count()}")
    print(f"Staff: {User.query.count()}")
```

Type `exit()` to quit Python.

---

## COMPLETE SETUP (If Starting From Scratch)

If you don't have the project yet on PythonAnywhere:

```bash
# 1. Clone repository
cd ~
git clone https://github.com/yamenmod9/gym-management-system.git
cd gym-management-system

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Setup database
flask db upgrade
python -c "from app import create_app, db; from app.seed import seed_all; app = create_app(); app.app_context().push(); seed_all()"

# 5. Configure web app (do this manually in Web tab)
```

Then reload web app from Web tab.

---

## QUICK REFERENCE

**Pull latest code:**
```bash
cd ~/gym-management-system && git pull origin main
```

**Reload web app:**
```bash
touch /var/www/yourusername_pythonanywhere_com_wsgi.py
```

**Check logs:**
- Go to Web tab → Log files → Error log

---

## ✅ SUCCESS CHECKLIST

After running these commands:

- [ ] `git pull` showed updated files
- [ ] Web app reloaded successfully
- [ ] Login curl command returns token
- [ ] Flutter staff app can login
- [ ] Can register a customer
- [ ] Can activate subscription
- [ ] Can check in with QR code

---

**🎉 YOU'RE DONE!**

Your backend is now updated and all features should work!

---

**END OF COMMANDS**


