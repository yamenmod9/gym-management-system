"""
Quick migration script for PythonAnywhere
Add password fields to customers table

Upload this file to PythonAnywhere and run:
python migrate_passwords_pythonanywhere.py
"""

import sqlite3
import secrets
import string
from passlib.hash import pbkdf2_sha256

# Database path on PythonAnywhere (adjust if needed)
DB_PATH = '/home/yamenmod91/gym-management-system/backend/instance/gym.db'

def generate_temp_password(length=8):
    """Generate random alphanumeric password"""
    chars = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(chars) for _ in range(length))

def main():
    print("="*70)
    print("🔄 Adding password fields to customers table")
    print("="*70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check if columns exist
    cursor.execute("PRAGMA table_info(customers)")
    columns = [col[1] for col in cursor.fetchall()]
    
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
