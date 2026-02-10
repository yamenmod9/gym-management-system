"""
Migration script: Add client authentication fields to Customer model

This adds:
- password_hash: Hashed password for client app login
- temp_password: Temporary password (plain text, shown once to client)
- password_changed: Boolean flag to track if client changed their password

Run this script: python add_client_auth_fields.py
"""
from flask import Flask
from app import create_app
from app.extensions import db

def migrate():
    """Add client authentication fields to customers table"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*70)
        print("🔄 DATABASE MIGRATION: Adding Client Authentication Fields")
        print("="*70)
        
        # Check if columns already exist
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('customers')]
        
        if 'password_hash' in columns:
            print("✅ password_hash column already exists")
        else:
            print("➕ Adding password_hash column...")
            db.session.execute(db.text(
                "ALTER TABLE customers ADD COLUMN password_hash VARCHAR(255)"
            ))
        
        if 'temp_password' in columns:
            print("✅ temp_password column already exists")
        else:
            print("➕ Adding temp_password column...")
            db.session.execute(db.text(
                "ALTER TABLE customers ADD COLUMN temp_password VARCHAR(20)"
            ))
        
        if 'password_changed' in columns:
            print("✅ password_changed column already exists")
        else:
            print("➕ Adding password_changed column...")
            db.session.execute(db.text(
                "ALTER TABLE customers ADD COLUMN password_changed BOOLEAN DEFAULT 0 NOT NULL"
            ))
        
        db.session.commit()
        
        print("\n📊 Generating temporary passwords for existing customers...")
        print("   (This allows existing customers to log in to the client app)")
        
        from app.models.customer import Customer
        
        customers = Customer.query.filter(
            db.or_(
                Customer.password_hash == None,
                Customer.password_hash == ''
            )
        ).all()
        
        print(f"\n   Found {len(customers)} customers without passwords")
        
        for customer in customers:
            temp_pass = customer.generate_temp_password()
            print(f"   📱 {customer.phone} ({customer.full_name}): {temp_pass}")
        
        if customers:
            db.session.commit()
            print(f"\n✅ Generated temporary passwords for {len(customers)} customers")
            print("   ⚠️  IMPORTANT: Save these passwords! Give them to the clients.")
        
        print("\n" + "="*70)
        print("✅ Migration completed successfully!")
        print("="*70)
        print("\n📋 NEXT STEPS:")
        print("   1. Restart your Flask app")
        print("   2. Give temporary passwords to existing clients")
        print("   3. Clients can login with: phone + temporary_password")
        print("   4. Clients should change their password after first login")
        print("="*70 + "\n")

if __name__ == '__main__':
    migrate()
