"""
Check what users exist in the database
Run this to see available usernames and their roles
"""
from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    users = User.query.all()
    
    print("\n" + "="*80)
    print("  DATABASE USERS")
    print("="*80)
    
    if not users:
        print("\n❌ No users found in database!")
        print("\nYou need to run: python seed.py")
    else:
        print(f"\nFound {len(users)} users:\n")
        
        for user in users:
            print(f"Username: {user.username:20s} | Role: {user.role.value:20s} | Branch: {user.branch_id}")
        
        print("\n" + "="*80)
        print("  DEFAULT PASSWORDS FROM SEED DATA")
        print("="*80)
        print("\nOwner:          owner / owner123")
        print("Branch Manager: manager_1 / manager123")
        print("Receptionist:   front_desk_1 / front123")
        print("Accountant:     accountant_1 / accountant123")
        print("\nNote: These are default passwords from seed.py")
        print("If passwords were changed, these won't work.")
        print("="*80)
