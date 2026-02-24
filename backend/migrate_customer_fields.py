"""
Database Migration - Add QR Code and Health Metrics Fields
Run this script to update your database schema
"""
from app import create_app
from app.extensions import db
import os

def migrate_database():
    """Add new columns to customers table"""
    app = create_app(os.getenv('FLASK_ENV', 'production'))
    
    with app.app_context():
        print("Starting database migration...")
        
        try:
            # Check if columns already exist
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            columns = [col['name'] for col in inspector.get_columns('customers')]
            
            migrations_needed = []
            
            # Check for qr_code column
            if 'qr_code' not in columns:
                # SQLite doesn't support adding UNIQUE constraint directly
                migrations_needed.append("ALTER TABLE customers ADD COLUMN qr_code VARCHAR(50)")
                migrations_needed.append("CREATE UNIQUE INDEX idx_customers_qr_code ON customers(qr_code)")
                print("  ✓ Will add qr_code column with unique index")
            else:
                print("  ✓ qr_code column already exists")
            
            # Check for bmi_category column
            if 'bmi_category' not in columns:
                migrations_needed.append("ALTER TABLE customers ADD COLUMN bmi_category VARCHAR(20)")
                print("  ✓ Will add bmi_category column")
            else:
                print("  ✓ bmi_category column already exists")
            
            # Check for bmr column
            if 'bmr' not in columns:
                migrations_needed.append("ALTER TABLE customers ADD COLUMN bmr FLOAT")
                print("  ✓ Will add bmr column")
            else:
                print("  ✓ bmr column already exists")
            
            # Execute migrations
            if migrations_needed:
                print(f"\n⚠️  Applying {len(migrations_needed)} migrations...")
                with db.engine.connect() as conn:
                    for migration in migrations_needed:
                        print(f"  Executing: {migration}")
                        conn.execute(text(migration))
                        conn.commit()
                
                print("\n✅ Database migration completed successfully!")
                
                # Generate QR codes for existing customers
                print("\nGenerating QR codes for existing customers...")
                from app.models import Customer
                customers_without_qr = Customer.query.filter(
                    (Customer.qr_code == None) | (Customer.qr_code == '')
                ).all()
                
                for customer in customers_without_qr:
                    customer.qr_code = f"GYM-{customer.id}"
                    print(f"  Generated QR code for customer {customer.id}: {customer.qr_code}")
                
                db.session.commit()
                print(f"\n✅ Generated {len(customers_without_qr)} QR codes")
                
                # Recalculate health metrics
                print("\nRecalculating health metrics for existing customers...")
                customers_with_health_data = Customer.query.filter(
                    Customer.height != None,
                    Customer.weight != None
                ).all()
                
                for customer in customers_with_health_data:
                    customer.calculate_health_metrics()
                    print(f"  Updated metrics for customer {customer.id}")
                
                db.session.commit()
                print(f"\n✅ Updated health metrics for {len(customers_with_health_data)} customers")
            else:
                print("\n✅ Database schema is already up to date!")
                
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Migration failed: {str(e)}")
            raise


if __name__ == '__main__':
    migrate_database()
