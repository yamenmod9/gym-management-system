"""
Migration: Add subscription type columns and populate them from service data.
Run once: python migrate_subscriptions.py
Safe to re-run (uses ADD COLUMN IF NOT EXISTS pattern via try/except).
"""
import sqlite3
import os

# Find the database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Search common locations
candidates = [
    os.path.join(BASE_DIR, 'instance', 'gym_management.db'),
    os.path.join(BASE_DIR, 'instance', 'gym.db'),
    os.path.join(BASE_DIR, 'gym_management.db'),
    os.path.join(BASE_DIR, 'gym.db'),
]

DB_PATH = None
for c in candidates:
    if os.path.exists(c):
        DB_PATH = c
        break

if DB_PATH is None:
    # Walk and find any .db
    for root, dirs, files in os.walk(BASE_DIR):
        # Skip venv
        dirs[:] = [d for d in dirs if d not in ('venv', '.venv', '__pycache__', '.git')]
        for f in files:
            if f.endswith('.db'):
                DB_PATH = os.path.join(root, f)
                break
        if DB_PATH:
            break

if DB_PATH is None:
    print('ERROR: No SQLite database file found. Exiting.')
    exit(1)

print(f'Using database: {DB_PATH}')

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# ── Step 1: Add missing columns ────────────────────────────────────────────
columns_to_add = [
    ('subscription_type',  'VARCHAR(20)'),
    ('remaining_coins',    'INTEGER'),
    ('total_coins',        'INTEGER'),
    ('remaining_sessions', 'INTEGER'),
    ('total_sessions',     'INTEGER'),
]

print('\n── Step 1: Adding columns ──')
for col_name, col_type in columns_to_add:
    try:
        cur.execute(f'ALTER TABLE subscriptions ADD COLUMN {col_name} {col_type}')
        print(f'  Added column: {col_name}')
    except sqlite3.OperationalError as e:
        if 'duplicate column' in str(e).lower():
            print(f'  Column already exists: {col_name} (skipped)')
        else:
            raise

conn.commit()

# ── Step 2: Verify columns are present ─────────────────────────────────────
cur.execute('PRAGMA table_info(subscriptions)')
existing_cols = {row[1] for row in cur.fetchall()}
print(f'\n  Current subscriptions columns: {sorted(existing_cols)}')

# ── Step 3: Read services to build a lookup ─────────────────────────────────
print('\n── Step 2: Reading services ──')
cur.execute('SELECT id, name, service_type, class_limit FROM services')
services = {}
for row in cur.fetchall():
    sid, name, stype, class_limit = row
    services[sid] = {'name': name, 'service_type': stype, 'class_limit': class_limit}
    print(f'  Service {sid}: {name!r} type={stype} class_limit={class_limit}')

def derive_sub_type(service_type, class_limit):
    """
    Same logic as SubscriptionService._derive_subscription_type.
    service_type may be stored as uppercase enum name (e.g. 'GYM') or
    lowercase value (e.g. 'gym') — handle both.
    """
    st = service_type.upper() if service_type else ''
    if st == 'GYM':
        return 'coins'
    if st == 'KARATE':
        return 'training'
    if st == 'SWIMMING_EDUCATION' or class_limit:
        return 'sessions'
    # SWIMMING_RECREATION, BUNDLE, etc.
    return 'time_based'

# ── Step 4: Populate NULL subscription_type rows ───────────────────────────
print('\n── Step 3: Re-populating ALL subscription types from service data ──')
cur.execute('''
    SELECT id, service_id, status, remaining_classes, classes_attended,
           subscription_type, remaining_coins, total_coins,
           remaining_sessions, total_sessions
    FROM subscriptions
''')
rows = cur.fetchall()
print(f'  Processing {len(rows)} total rows')

updated = 0
for row in rows:
    (sub_id, service_id, status, remaining_classes, classes_attended,
     _, _, _, _, _) = row

    svc = services.get(service_id)
    if not svc:
        print(f'  WARNING: subscription {sub_id} has unknown service_id {service_id}, skipping')
        continue

    sub_type = derive_sub_type(svc['service_type'], svc['class_limit'])
    class_limit = svc['class_limit']

    if sub_type == 'coins':
        # Use existing value if already set, else default to 50
        existing_coins = row[6]  # remaining_coins
        existing_total = row[7]  # total_coins
        coin_amount = existing_total or existing_coins or 50
        remaining = existing_coins if existing_coins is not None else coin_amount
        cur.execute('''
            UPDATE subscriptions
            SET subscription_type=?, remaining_coins=?, total_coins=?
            WHERE id=?
        ''', (sub_type, remaining, coin_amount, sub_id))

    elif sub_type in ('sessions', 'training'):
        total_sess = class_limit or 10
        # Use remaining_classes if set, else derive from classes_attended
        rem = remaining_classes if remaining_classes is not None else max(0, total_sess - (classes_attended or 0))
        cur.execute('''
            UPDATE subscriptions
            SET subscription_type=?, remaining_sessions=?, total_sessions=?
            WHERE id=?
        ''', (sub_type, rem, total_sess, sub_id))

    else:  # time_based
        cur.execute('''
            UPDATE subscriptions
            SET subscription_type=?
            WHERE id=?
        ''', (sub_type, sub_id))

    updated += 1

conn.commit()
print(f'  Updated {updated} subscriptions')

# ── Step 5: Also fix rows that have subscription_type set but coins/sessions NULL
print('\n── Step 4: Fixing rows with type set but counters NULL ──')
fixed = 0

# Fix coins rows with NULL remaining_coins
cur.execute('''
    SELECT id, service_id FROM subscriptions
    WHERE subscription_type = 'coins' AND remaining_coins IS NULL
''')
for sub_id, service_id in cur.fetchall():
    coin_amount = 50
    cur.execute('''
        UPDATE subscriptions SET remaining_coins=?, total_coins=? WHERE id=?
    ''', (coin_amount, coin_amount, sub_id))
    fixed += 1

# Fix sessions/training rows with NULL remaining_sessions
cur.execute('''
    SELECT id, service_id, classes_attended FROM subscriptions
    WHERE subscription_type IN ('sessions', 'training') AND remaining_sessions IS NULL
''')
for sub_id, service_id, classes_attended in cur.fetchall():
    svc = services.get(service_id)
    total_sess = (svc['class_limit'] if svc else None) or 10
    rem = max(0, total_sess - (classes_attended or 0))
    cur.execute('''
        UPDATE subscriptions SET remaining_sessions=?, total_sessions=? WHERE id=?
    ''', (rem, total_sess, sub_id))
    fixed += 1

conn.commit()
print(f'  Fixed {fixed} additional rows')

# ── Step 6: Verification ────────────────────────────────────────────────────
print('\n── Step 5: Verification ──')
cur.execute('SELECT subscription_type, COUNT(*) FROM subscriptions GROUP BY subscription_type')
for row in cur.fetchall():
    print(f'  {row[0]!r}: {row[1]} subscriptions')

cur.execute('SELECT COUNT(*) FROM subscriptions WHERE subscription_type IS NULL')
remaining_nulls = cur.fetchone()[0]
print(f'  Remaining NULLs: {remaining_nulls}')

print('\n── Sample active subscriptions ──')
cur.execute('''
    SELECT s.id, s.customer_id, sv.name, s.subscription_type,
           s.remaining_coins, s.total_coins, s.remaining_sessions, s.total_sessions
    FROM subscriptions s JOIN services sv ON s.service_id = sv.id
    WHERE s.status = 'active'
    LIMIT 10
''')
for row in cur.fetchall():
    print(f'  Sub={row[0]} cust={row[1]} svc={row[2]!r} type={row[3]!r} coins={row[4]}/{row[5]} sess={row[6]}/{row[7]}')

conn.close()
print('\nMigration complete!')





