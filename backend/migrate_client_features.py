"""
Database migration script for client activation and entry logging
Run this to add the new tables
"""
from app import create_app
from app.extensions import db
from sqlalchemy import text, inspect
import os
from datetime import datetime, timedelta


def migrate_database():
    """Add activation_codes and entry_logs tables, and update subscriptions table"""
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        print("Starting client features migration...")
        
        try:
            inspector = inspect(db.engine)
            existing_tables = inspector.get_table_names()
            
            migrations_needed = []
            
            # Check if activation_codes table exists
            if 'activation_codes' not in existing_tables:
                migrations_needed.append('activation_codes')
                print("  ✓ Will create activation_codes table")
            else:
                print("  ✓ activation_codes table already exists")
            
            # Check if entry_logs table exists
            if 'entry_logs' not in existing_tables:
                migrations_needed.append('entry_logs')
                print("  ✓ Will create entry_logs table")
            else:
                print("  ✓ entry_logs table already exists")
            
            # Check if subscriptions table needs new columns
            if 'subscriptions' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('subscriptions')]
                if 'remaining_visits' not in columns or 'remaining_classes' not in columns:
                    migrations_needed.append('subscription_columns')
                    print("  ✓ Will add remaining_visits and remaining_classes columns to subscriptions")
                else:
                    print("  ✓ Subscriptions table already has visit/class tracking columns")
            
            # Create tables and add columns
            if migrations_needed:
                print(f"\n⚠️  Applying {len(migrations_needed)} migration(s)...")
                
                # Import models to ensure they're registered
                from app.models import ActivationCode, EntryLog, Subscription
                
                # Add columns to subscriptions table if needed
                if 'subscription_columns' in migrations_needed:
                    print("  Adding columns to subscriptions table...")
                    with db.engine.connect() as conn:
                        conn.execute(text('ALTER TABLE subscriptions ADD COLUMN remaining_visits INTEGER'))
                        conn.execute(text('ALTER TABLE subscriptions ADD COLUMN remaining_classes INTEGER'))
                        conn.commit()
                    print("  ✓ Columns added successfully")
                    
                    # Initialize values for existing subscriptions
                    print("  Initializing values for existing subscriptions...")
                    _initialize_subscription_values()
                
                # Create all tables (only new ones will be created)
                db.create_all()
                
                print("\n✅ Database schema updated successfully!")
                
                # Generate sample data
                print("\nGenerating sample activation codes...")
                _generate_sample_codes()
                
                print("\nGenerating sample entry logs...")
                _generate_sample_entries()
                
                db.session.commit()
                print("\n✅ Sample data created successfully!")
                
            else:
                print("\n✅ Database schema is already up to date!")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise


def _initialize_subscription_values():
    """Initialize remaining_visits and remaining_classes for existing subscriptions"""
    from app.models import Subscription
    
    subscriptions = Subscription.query.all()
    for sub in subscriptions:
        # If service has class limit, set remaining_classes
        if sub.service.class_limit:
            sub.remaining_classes = max(0, sub.service.class_limit - sub.classes_attended)
            sub.remaining_visits = None
        else:
            # Unlimited visits service - set a reasonable default (30 visits)
            sub.remaining_visits = 30
            sub.remaining_classes = None
    
    db.session.commit()
    print(f"  ✓ Initialized {len(subscriptions)} subscription(s)")


def _generate_sample_codes():
    """Generate sample activation codes for testing"""
    from app.models import Customer, ActivationCode, ActivationCodeType
    
    # Get first 5 active customers
    customers = Customer.query.filter_by(is_active=True).limit(5).all()
    
    for customer in customers:
        # Create a sample activation code (already used)
        code, plain_code = ActivationCode.create_code(
            customer_id=customer.id,
            delivery_method='sms' if customer.phone else 'email',
            delivery_target=customer.phone or customer.email,
            code_type=ActivationCodeType.LOGIN,
            expiry_minutes=15
        )
        
        # Mark as used
        code.is_used = True
        code.attempts = 1
        
        print(f"  Created activation code for customer {customer.id} ({customer.full_name})")


def _generate_sample_entries():
    """Generate sample entry logs for testing"""
    from app.models import Customer, Subscription, EntryLog, EntryType, SubscriptionStatus
    from datetime import datetime, timedelta
    import random
    
    # Get customers with active subscriptions
    customers = Customer.query.join(Subscription).filter(
        Subscription.status == SubscriptionStatus.ACTIVE,
        Customer.is_active == True
    ).limit(10).all()
    
    for customer in customers:
        # Get their active subscription
        subscription = Subscription.query.filter_by(
            customer_id=customer.id,
            status=SubscriptionStatus.ACTIVE
        ).first()
        
        if not subscription:
            continue
        
        # Create 3-5 entry logs over the past week
        num_entries = random.randint(3, 5)
        
        for i in range(num_entries):
            # Random day in the past week
            days_ago = random.randint(0, 7)
            entry_time = datetime.now() - timedelta(days=days_ago, hours=random.randint(6, 22))
            
            # Random entry type
            entry_type = random.choice([EntryType.QR_SCAN, EntryType.BARCODE, EntryType.FINGERPRINT])
            
            # Determine coins to deduct based on service type
            coins = 1 if (subscription.remaining_visits is not None or subscription.remaining_classes is not None) else 0
            
            entry = EntryLog.create_entry(
                customer_id=customer.id,
                branch_id=customer.branch_id,
                entry_type=entry_type,
                subscription_id=subscription.id,
                coins_deducted=coins
            )
            entry.entry_time = entry_time
            
        print(f"  Created {num_entries} entry logs for customer {customer.id} ({customer.full_name})")


if __name__ == '__main__':
    migrate_database()
