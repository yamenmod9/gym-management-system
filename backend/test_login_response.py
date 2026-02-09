"""
Test login responses for all user roles
This helps debug frontend issues by showing exact response format
"""
from app import create_app
from app.models import User

app = create_app('development')

with app.app_context():
    print("\n" + "="*70)
    print("🔐 LOGIN RESPONSE EXAMPLES FOR ALL ROLES")
    print("="*70 + "\n")
    
    test_users = [
        ('owner', 'owner123'),
        ('manager1', 'manager123'),
        ('reception1', 'reception123'),
        ('accountant1', 'accountant123'),
        ('baccountant1', 'accountant123'),
    ]
    
    for username, password in test_users:
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            print(f"✅ {username} ({user.role.value}):")
            user_dict = user.to_dict()
            print(f"   Role: {user_dict['role']}")
            print(f"   Branch ID: {user_dict['branch_id']}")
            print(f"   Branch Name: {user_dict['branch_name']}")
            print(f"   Full Response: {user_dict}")
            print()
        else:
            print(f"❌ {username}: FAILED")
            print()
    
    print("="*70)
    print("📋 ROLE VALUES YOUR FLUTTER APP MUST HANDLE:")
    print("="*70)
    print("- 'owner' (no branch_id)")
    print("- 'branch_manager' (has branch_id)")
    print("- 'front_desk' (has branch_id)")
    print("- 'central_accountant' (no branch_id)")
    print("- 'branch_accountant' (has branch_id)")
    print("="*70 + "\n")
