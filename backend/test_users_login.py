"""
Test script to verify all user accounts can log in
"""
from app import create_app
from app.extensions import db
from app.models import User

app = create_app('development')

with app.app_context():
    print("📋 Testing All User Accounts...\n")
    print("=" * 60)
    
    test_accounts = [
        ('owner', 'owner123', 'OWNER'),
        ('manager1', 'manager123', 'BRANCH_MANAGER'),
        ('manager2', 'manager123', 'BRANCH_MANAGER'),
        ('reception1', 'reception123', 'FRONT_DESK'),
        ('reception2', 'reception123', 'FRONT_DESK'),
        ('reception3', 'reception123', 'FRONT_DESK'),
        ('accountant1', 'accountant123', 'CENTRAL_ACCOUNTANT'),
        ('baccountant1', 'accountant123', 'BRANCH_ACCOUNTANT'),
    ]
    
    failed = []
    passed = []
    
    for username, password, expected_role in test_accounts:
        user = User.query.filter_by(username=username).first()
        
        if not user:
            print(f"❌ {username:15} - USER NOT FOUND")
            failed.append(username)
            continue
        
        if user.check_password(password):
            print(f"✅ {username:15} - Login OK | Role: {user.role.value:20} | Active: {user.is_active}")
            passed.append(username)
        else:
            print(f"❌ {username:15} - PASSWORD INCORRECT")
            failed.append(username)
    
    print("=" * 60)
    print(f"\n✅ Passed: {len(passed)}/{len(test_accounts)}")
    print(f"❌ Failed: {len(failed)}/{len(test_accounts)}")
    
    if failed:
        print(f"\nFailed accounts: {', '.join(failed)}")
    
    # Check branch distribution
    print("\n" + "=" * 60)
    print("📊 Branch Data Distribution")
    print("=" * 60)
    
    from app.models import Branch, Customer, Subscription, Transaction
    
    branches = Branch.query.all()
    for branch in branches:
        customers_count = Customer.query.filter_by(branch_id=branch.id).count()
        subscriptions_count = Subscription.query.filter_by(branch_id=branch.id).count()
        transactions_count = Transaction.query.filter_by(branch_id=branch.id).count()
        staff_count = User.query.filter_by(branch_id=branch.id).count()
        
        print(f"\n{branch.name} (ID: {branch.id}):")
        print(f"  Staff:         {staff_count}")
        print(f"  Customers:     {customers_count}")
        print(f"  Subscriptions: {subscriptions_count}")
        print(f"  Transactions:  {transactions_count}")
    
    print("\n" + "=" * 60)
