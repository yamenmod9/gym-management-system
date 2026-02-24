"""
Quick migration script for PythonAnywhere
Add password fields to customers table

Usage:
    python migrate_passwords_pythonanywhere.py [database_path]

If no path provided, will search common locations.
"""

import sqlite3
import secrets
import string
import sys
import os
from pathlib import Path

try:
    from passlib.hash import pbkdf2_sha256
except ImportError:
    print("❌ passlib not installed. Installing...")
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'passlib'])
    from passlib.hash import pbkdf2_sha256

def find_database():
    """Find the database file in common locations"""
    possible_paths = [
        # From command line argument
        sys.argv[1] if len(sys.argv) > 1 else None,
        # Common PythonAnywhere locations
        '/home/yamenmod91/gym-management-system/backend/instance/gym.db',
        '/home/yamenmod91/gym-management-system/instance/gym.db',
        '/home/yamenmod91/instance/gym.db',
        '/home/yamenmod91/gym.db',
        # Relative paths
        'instance/gym.db',
        'gym.db',
    ]
    
    for path in possible_paths:
        if path and os.path.exists(path):
            return path
    
    # Search in home directory
    home = Path.home()
    for db_file in home.rglob('gym.db'):
        return str(db_file)
    
    return None

DB_PATH = find_database()

def generate_temp_password(length=8):
    """Generate random alphanumeric password"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    print("="*70)
    print("🔄 Adding password fields to customers table")
    print("="*70)
    
    if not DB_PATH:
        print("❌ Database not found!")
        print("\nSearched locations:")
        print("  - /home/yamenmod91/gym-management-system/backend/instance/gym.db")
        print("  - /home/yamenmod91/gym-management-system/instance/gym.db")
        print("  - ~/instance/gym.db")
        print("\n💡 SOLUTION:")
        print("1. Find your database file:")
        print("   find ~ -name 'gym.db' 2>/dev/null")
        print("\n2. Run this script with the path:")
        print("   python migrate_passwords_pythonanywhere.py /path/to/your/gym.db")
        print("\n3. Or check your Flask config:")
        print("   cat ~/gym-management-system/backend/app/config.py")
        print("="*70)
        return
    
    print(f"📁 Using database: {DB_PATH}\n")
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database file does not exist: {DB_PATH}")
        return
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(customers)")
    columns_info = cursor.fetchall()
    
    if not columns_info:
        print("❌ Table 'customers' not found in database!")
        print("\n📋 Available tables:")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for table in tables:
            print(f"  - {table[0]}")
        print("\n💡 This might not be the correct database file.")
        print("   Check your Flask app config for the correct DATABASE_URI")
        conn.close()
        return
    
    columns = [col[1] for col in columns_info]
    print(f"✅ Found customers table with {len(columns)} columns\n")
    
    # Add columns if they don't exist
    if 'password_hash' not in columns:
        print("➕ Adding password_hash column...")
        cursor.execute("ALTER TABLE customers ADD COLUMN password_hash VARCHAR(255)")
    else:
        print("✅ password_hash already exists")
    
    if 'temp_password' not in columns:
        print("➕ Adding temp_password column...")
        cursor.execute("ALTER TABLE customers ADD COLUMN temp_password VARCHAR(20)")
    else:
        print("✅ temp_password already exists")
    
    if 'password_changed' not in columns:
        print("➕ Adding password_changed column...")
        cursor.execute("ALTER TABLE customers ADD COLUMN password_changed BOOLEAN DEFAULT 0 NOT NULL")
    else:
        print("✅ password_changed already exists")
    
    conn.commit()
    
    # Generate temp passwords for existing customers
    print("\n📊 Generating temporary passwords...")
    cursor.execute("""
        SELECT id, phone, full_name 
        FROM customers 
        WHERE password_hash IS NULL OR password_hash = ''
    """)
    
    customers = cursor.fetchall()
    print(f"Found {len(customers)} customers without passwords\n")
    
    for customer_id, phone, full_name in customers:
        temp_pass = generate_temp_password()
        password_hash = pbkdf2_sha256.hash(temp_pass)
        
        cursor.execute("""
            UPDATE customers 
            SET password_hash = ?, temp_password = ?, password_changed = 0
            WHERE id = ?
        """, (password_hash, temp_pass, customer_id))
        
        print(f"📱 {phone} ({full_name}): {temp_pass}")
    
    conn.commit()
    conn.close()
    
    print(f"\n✅ Migration completed! Generated {len(customers)} passwords")
    print("⚠️  SAVE THESE PASSWORDS - Give them to your clients")
    print("="*70)

if __name__ == '__main__':
    main()
