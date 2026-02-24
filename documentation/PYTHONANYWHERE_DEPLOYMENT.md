# 🚀 PYTHONANYWHERE DEPLOYMENT GUIDE

**Last Updated:** February 17, 2026

---

## 📋 QUICK DEPLOYMENT

### Step 1: Pull Latest Changes

```bash
cd ~/gym-management-system
git pull origin main
```

### Step 2: Reload Web App

1. Go to **Web** tab on PythonAnywhere dashboard
2. Click **"Reload"** button

**That's it!** Your app is updated.

---

## 🔍 VERIFY DEPLOYMENT

### Test Customer Registration

```bash
# Get token first (login as receptionist)
curl -X POST https://yourusername.pythonanywhere.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "01511111111",
    "password": "reception123"
  }'

# Copy the token from response, then:
curl -X POST https://yourusername.pythonanywhere.com/api/customers/register \
  -H "Authorization: Bearer {YOUR_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Test Customer",
    "phone": "01999999999",
    "gender": "male",
    "age": 25,
    "weight": 75,
    "height": 175,
    "branch_id": 1
  }'
```

**Expected:** Status 201 with customer data including `temporary_password`

---

## 🛠️ FULL SETUP (If Starting Fresh)

### 1. Clone Repository

```bash
cd ~
git clone https://github.com/yamenmod9/gym-management-system.git
cd gym-management-system
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Database

```bash
# Initialize database
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# Seed with test data
python -c "from app import create_app, db; from app.seed import seed_all; app = create_app(); app.app_context().push(); seed_all()"
```

### 5. Configure PythonAnywhere Web App

**Web Tab Settings:**

- **Source code:** `/home/yourusername/gym-management-system`
- **Working directory:** `/home/yourusername/gym-management-system`
- **Virtualenv:** `/home/yourusername/gym-management-system/venv`
- **WSGI configuration file:** Edit to point to your app

**WSGI Configuration (`/var/www/yourusername_pythonanywhere_com_wsgi.py`):**

```python
import sys
import os

# Add your project directory
project_home = '/home/yourusername/gym-management-system'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Set environment variables
os.environ['FLASK_ENV'] = 'production'

# Import Flask app
from app import create_app
application = create_app()
```

### 6. Set Environment Variables

Create `.env` file in project root:

```bash
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
DATABASE_URL=sqlite:///gym.db
FLASK_ENV=production
```

### 7. Reload Web App

Go to Web tab → Click "Reload"

---

## 🔧 TROUBLESHOOTING

### Error: Module not found

```bash
cd ~/gym-management-system
source venv/bin/activate
pip install -r requirements.txt
```

### Error: Database not found

```bash
cd ~/gym-management-system
source venv/bin/activate
flask db upgrade
python -c "from app import create_app, db; from app.seed import seed_all; app = create_app(); app.app_context().push(); seed_all()"
```

### Error: Permission denied

```bash
chmod +x ~/gym-management-system
```

### Check Logs

Go to **Web** tab → **Log files** section:
- **Error log**: Shows Python errors
- **Server log**: Shows requests

---

## 📦 UPDATE WORKFLOW

When you make changes to the backend:

1. **Commit and Push:**
   ```bash
   # On local machine
   cd C:\Programming\Flutter\gym_frontend\Gym_backend\backend
   git add .
   git commit -m "Your commit message"
   git push origin main
   ```

2. **Pull on PythonAnywhere:**
   ```bash
   # On PythonAnywhere terminal
   cd ~/gym-management-system
   git pull origin main
   ```

3. **Reload Web App:**
   - Go to Web tab
   - Click "Reload"

---

## 🧪 TEST CREDENTIALS

### Staff Accounts

**Owner:**
- Phone: `01500000001`
- Password: `owner123`

**Receptionist (Branch 1):**
- Phone: `01511111111`
- Password: `reception123`

**Manager (Branch 1):**
- Phone: `01522222222`
- Password: `manager123`

**Accountant (Branch 1):**
- Phone: `01533333333`
- Password: `accountant123`

### Customer Accounts

**Customer 1:**
- Phone: `01077827638`
- Temp Password: `RX04AF`
- Branch: 1 (Dragon Club)

**Customer 2:**
- Phone: `01022981052`
- Temp Password: `SI19IC`
- Branch: 1 (Dragon Club)

---

## 📊 DATABASE MANAGEMENT

### Backup Database

```bash
cd ~/gym-management-system
cp instance/gym.db instance/gym_backup_$(date +%Y%m%d).db
```

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

```python
from app import create_app, db
from app.models import Customer, User, Subscription

app = create_app()
with app.app_context():
    # Check customers
    print(f"Customers: {Customer.query.count()}")
    
    # Check staff
    print(f"Staff: {User.query.count()}")
    
    # Check subscriptions
    print(f"Subscriptions: {Subscription.query.count()}")
```

---

## 🌐 API BASE URL

After deployment, your API is available at:

```
https://yourusername.pythonanywhere.com
```

Update this in Flutter app:

**File:** `lib/core/config/api_config.dart`

```dart
static const String baseUrl = 'https://yourusername.pythonanywhere.com';
```

---

## ✅ DEPLOYMENT CHECKLIST

Before deploying to production:

- [ ] Update `.env` with production secrets
- [ ] Set `FLASK_ENV=production`
- [ ] Backup database
- [ ] Test all API endpoints
- [ ] Update Flutter app base URL
- [ ] Test Flutter apps with production API

After deployment:

- [ ] Pull latest changes on PythonAnywhere
- [ ] Reload web app
- [ ] Test customer registration
- [ ] Test subscription activation
- [ ] Test check-in
- [ ] Test client app login

---

**END OF GUIDE**

