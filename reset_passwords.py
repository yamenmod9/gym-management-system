"""
Reset user passwords - useful for fixing login issues without clearing database
"""
from app import create_app
from app.extensions import db
from app.models import User, UserRole

def reset_user_passwords():
    """Reset all user passwords to default"""
    app = create_app('development')
    
    with app.app_context():
        print("🔐 Resetting user passwords...")
        print("="*60)
        
        # Define all users with their passwords
        user_passwords = {
            'owner': 'owner123',
            'manager1': 'manager123',
            'manager2': 'manager123',
            'reception1': 'reception123',
            'reception2': 'reception123',
            'reception3': 'reception123',
            'accountant1': 'accountant123',
            'baccountant1': 'accountant123'
        }
        
        updated = 0
        not_found = []
        
        for username, password in user_passwords.items():
            user = User.query.filter_by(username=username).first()
            
            if user:
                user.set_password(password)
                print(f"✅ {username:15} - Password reset to '{password}'")
                updated += 1
            else:
                print(f"❌ {username:15} - User not found")
                not_found.append(username)
        
        db.session.commit()
        
        print("="*60)
        print(f"\n✅ Updated {updated} user passwords")
        
        if not_found:
            print(f"⚠️  Users not found: {', '.join(not_found)}")
            print("\nTo create missing users, run: python seed.py")
        
        print("\n" + "="*60)
        print("📋 Login Credentials:")
        print("="*60)
        print("\n🔐 OWNER:")
        print("  Username: owner | Password: owner123")
        print("\n👔 BRANCH MANAGERS:")
        print("  Username: manager1 | Password: manager123")
        print("  Username: manager2 | Password: manager123")
        print("\n👥 RECEPTIONISTS:")
        print("  Username: reception1 | Password: reception123")
        print("  Username: reception2 | Password: reception123")
        print("  Username: reception3 | Password: reception123")
        print("\n💰 ACCOUNTANTS:")
        print("  Username: accountant1 | Password: accountant123")
        print("  Username: baccountant1 | Password: accountant123")
        print("="*60)

if __name__ == '__main__':
    reset_user_passwords()
