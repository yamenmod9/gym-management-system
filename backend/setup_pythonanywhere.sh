#!/bin/bash
# PythonAnywhere Setup Script
# Run this to install all dependencies and set up the database

echo "=================================="
echo "  PYTHONANYWHERE SETUP SCRIPT"
echo "=================================="

cd ~/gym-management-system/backend

echo ""
echo "Step 1: Installing Python dependencies..."
pip3 install --user -r requirements.txt

echo ""
echo "Step 2: Setting up database..."
python3 seed.py

echo ""
echo "=================================="
echo "  SETUP COMPLETE!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Go to Web tab on PythonAnywhere"
echo "2. Click 'Reload yamenmod91.pythonanywhere.com'"
echo "3. Run tests: python3 test_all_fixes.py https://yamenmod91.pythonanywhere.com"
echo ""
