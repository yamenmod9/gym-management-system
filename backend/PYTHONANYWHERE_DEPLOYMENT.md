# PythonAnywhere Deployment - Quick Fix

## Issue
`ModuleNotFoundError: No module named 'flask_jwt_extended'`

This means dependencies need to be installed on PythonAnywhere.

## Solution

Run these commands in your PythonAnywhere Bash console:

```bash
# Navigate to project directory
cd ~/gym-management-system/backend

# Option 1: If using virtual environment (RECOMMENDED)
source ~/virtualenvs/{your-venv-name}/bin/activate
pip install -r requirements.txt

# Option 2: If no virtual environment
pip3 install --user -r requirements.txt

# After installation, run migration
python3 migrate_customer_fields.py

# Then reload your web app from the Web tab
```

## Finding Your Virtual Environment

If you're not sure of your virtualenv name:

```bash
# List all virtualenvs
ls ~/virtualenvs/

# Or check your WSGI config file
cat /var/www/yamenmod91_pythonanywhere_com_wsgi.py | grep virtualenv
```

Common virtualenv names:
- `gym-venv`
- `mysite-virtualenv`
- `venv`
- `env`

## Complete Step-by-Step

1. **Open Bash Console** on PythonAnywhere

2. **Navigate to backend folder:**
   ```bash
   cd ~/gym-management-system/backend
   ```

3. **Activate virtual environment:**
   ```bash
   # Replace 'your-venv-name' with actual name
   source ~/virtualenvs/your-venv-name/bin/activate
   ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   
   Expected packages installed:
   - Flask==3.0.0
   - Flask-SQLAlchemy==3.1.1
   - Flask-JWT-Extended==4.7.1
   - Flask-Marshmallow==1.2.1
   - marshmallow-sqlalchemy==1.1.0
   - python-dotenv==1.0.1
   - gunicorn==21.2.0

5. **Run database migration:**
   ```bash
   python migrate_customer_fields.py
   ```
   
   You should see:
   ```
   ✓ Will add qr_code column with unique index
   ✓ Will add bmi_category column
   ✓ Will add bmr column
   ✅ Generated 150 QR codes
   ✅ Updated health metrics for 150 customers
   ```

6. **Reload web app:**
   - Go to **Web** tab in PythonAnywhere dashboard
   - Click green **"Reload yamenmod91.pythonanywhere.com"** button

7. **Test the endpoint:**
   ```bash
   # From Flutter app or use curl:
   curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/register \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"full_name":"Test","phone":"01999999999","gender":"male","age":25,"branch_id":1}'
   ```

## Troubleshooting

### If virtual environment not found:
```bash
# Check WSGI file to see how it's configured
cat /var/www/yamenmod91_pythonanywhere_com_wsgi.py
```

### If pip install fails with permissions:
```bash
# Install with --user flag
pip3 install --user -r requirements.txt
```

### If migration fails:
```bash
# Check Python version
python3 --version

# Make sure you're in the backend directory
pwd  # Should show: /home/yamenmod91/gym-management-system/backend

# Try with full path
python3 ~/gym-management-system/backend/migrate_customer_fields.py
```

## Quick Commands Summary

```bash
cd ~/gym-management-system/backend
source ~/virtualenvs/your-venv-name/bin/activate
pip install -r requirements.txt
python migrate_customer_fields.py
# Then reload web app from dashboard
```

---

**After completing these steps, your Flutter app should work!**
