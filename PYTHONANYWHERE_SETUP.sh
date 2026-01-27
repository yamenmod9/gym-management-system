#!/bin/bash
# PythonAnywhere Setup Script for Gym Management System
# Run this script in PythonAnywhere Bash console

echo "============================================"
echo " Gym Management System - PythonAnywhere Setup"
echo "============================================"

# Step 1: Clone repository
echo "[1/7] Cloning repository from GitHub..."
cd ~
git clone https://github.com/yamenmod9/gym-management-system.git
cd gym-management-system

# Step 2: Create virtual environment
echo "[2/7] Creating virtual environment..."
python3.11 -m venv venv

# Step 3: Activate virtual environment
echo "[3/7] Activating virtual environment..."
source venv/bin/activate

# Step 4: Upgrade pip
echo "[4/7] Upgrading pip..."
pip install --upgrade pip

# Step 5: Install dependencies
echo "[5/7] Installing dependencies..."
pip install -r requirements.txt

# Step 6: Create .env file
echo "[6/7] Creating environment file..."
cat > .env << 'EOF'
FLASK_ENV=production
SECRET_KEY=change-this-to-a-random-secret-key-in-production
JWT_SECRET_KEY=change-this-to-a-random-jwt-secret-key-in-production
DATABASE_URL=sqlite:///gym_management.db
EOF

# Step 7: Initialize database
echo "[7/7] Initializing database..."
python -c "from app import create_app; from app.extensions import db; app = create_app('production'); app.app_context().push(); db.create_all(); print('Database initialized!')"

# Optional: Seed database with test data
read -p "Do you want to seed the database with test data? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Seeding database..."
    python seed.py
fi

echo ""
echo "============================================"
echo " Setup Complete!"
echo "============================================"
echo ""
echo "IMPORTANT: Next Steps"
echo "1. Go to the Web tab in PythonAnywhere"
echo "2. Click 'Add a new web app'"
echo "3. Choose 'Manual configuration' with Python 3.11"
echo "4. Set Virtualenv path to:"
echo "   /home/YOUR_USERNAME/gym-management-system/venv"
echo ""
echo "5. Edit WSGI configuration file with:"
echo "   See wsgi_pythonanywhere.py for the content"
echo ""
echo "6. Replace YOUR_USERNAME with your actual username"
echo "7. Reload your web app"
echo ""
echo "Your project location:"
pwd
echo ""
echo "Your virtualenv location:"
echo "$HOME/gym-management-system/venv"
echo ""
