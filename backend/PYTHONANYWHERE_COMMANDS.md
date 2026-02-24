# Quick PythonAnywhere Deployment Commands

## Copy and paste these commands into PythonAnywhere Bash console:

### One-Line Setup (Automated):
```bash
cd ~ && git clone https://github.com/yamenmod9/gym-management-system.git && cd gym-management-system && python3.11 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt && cp .env.example .env && python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Database initialized!')"
```

### OR Step-by-Step Commands:

```bash
# 1. Clone repository
cd ~
git clone https://github.com/yamenmod9/gym-management-system.git
cd gym-management-system

# 2. Create virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
nano .env
# Edit the SECRET_KEY and JWT_SECRET_KEY, then press CTRL+X, Y, ENTER

# 5. Initialize database
python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Database initialized!')"

# 6. (Optional) Seed with test data
python seed.py
```

## WSGI Configuration

After running the commands above:

1. Go to **Web tab** → Click **"Add a new web app"**
2. Choose **"Manual configuration"** → Select **Python 3.11**
3. In **Virtualenv** section, enter:
   ```
   /home/YOUR_USERNAME/gym-management-system/venv
   ```
   (Replace YOUR_USERNAME with your actual PythonAnywhere username)

4. Click on **WSGI configuration file** link and replace ALL content with:

```python
import sys
import os

# Add your project directory to the sys.path
# REPLACE 'YOUR_USERNAME' WITH YOUR ACTUAL USERNAME!
project_home = '/home/YOUR_USERNAME/gym-management-system'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(project_home, '.env')
load_dotenv(env_path)

os.environ['FLASK_ENV'] = 'production'

# Import Flask application
from app import create_app
application = create_app('production')
```

5. **IMPORTANT:** Replace `YOUR_USERNAME` in the WSGI file with your actual PythonAnywhere username!

6. Click **Reload** button (green button at top of Web tab)

## Your API will be live at:
```
https://YOUR_USERNAME.pythonanywhere.com
```

## Test Page:
```
https://YOUR_USERNAME.pythonanywhere.com/test
```

## Important Paths (Replace YOUR_USERNAME):
- **Project Location:** `/home/YOUR_USERNAME/gym-management-system`
- **Virtual Environment:** `/home/YOUR_USERNAME/gym-management-system/venv`
- **Database:** `/home/YOUR_USERNAME/gym-management-system/instance/gym_management.db`

## Troubleshooting

### If you see "Something went wrong" error:
1. Check the **Error log** in the Web tab
2. Make sure you replaced YOUR_USERNAME in the WSGI file
3. Verify the virtualenv path is correct

### To view logs:
```bash
# Error log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# Server log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.server.log
```

### To update your deployment:
```bash
cd ~/gym-management-system
git pull origin main
source venv/bin/activate
pip install -r requirements.txt  # if dependencies changed
# Then reload web app from Web tab
```

## Generate Secure Keys

Before going to production, generate secure keys:

```bash
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_hex(32))"
python3 -c "import secrets; print('JWT_SECRET_KEY=' + secrets.token_hex(32))"
```

Copy these into your `.env` file using:
```bash
nano .env
```
