"""
Flask application factory
"""
from flask import Flask, jsonify
from app.config import config
from app.extensions import init_extensions
from app.routes import register_blueprints
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.exceptions import HTTPException


def create_app(config_name='default'):
    """
    Application factory pattern
    
    Args:
        config_name: Configuration name (development, production, testing)
    
    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    config_class = config[config_name]
    if hasattr(config_class, 'validate'):
        config_class.validate()
    app.config.from_object(config_class)

    # Initialize extensions
    init_extensions(app)

    # Register blueprints. Diagnostic endpoints stay out of production builds.
    register_blueprints(app, include_dev_tools=config_name != 'production')
    
    # Reject tokens belonging to deactivated accounts
    register_active_account_guard(app)

    # Register error handlers
    register_error_handlers(app)
    
    # Register CLI commands
    register_cli_commands(app)
    
    # Run database schema migrations
    _ensure_db_schema(app)
    
    # Health check endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Gym Management System API',
            'version': '1.0.0',
            'status': 'running',
            'docs': '/test',
            'privacy_policy': '/privacy-policy'
        })
    
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy'})
    
    return app


def _ensure_db_schema(app):
    """Ensure database schema matches model definitions (auto-migration)"""
    with app.app_context():
        from sqlalchemy import text, inspect as sa_inspect
        from app.extensions import db

        try:
            # Bootstrap a completely empty database (fresh Postgres/MySQL
            # instance, e.g. a new Railway deploy) with the full schema.
            # create_all() only creates tables that don't already exist, so
            # this is a no-op — and safe to run on every boot — once the
            # schema is in place; the column/index patches below still run
            # after it for databases that predate a given model change.
            #
            # Imported as `from app import models`, not `import app.models`:
            # the latter binds the name `app` in this function's scope, which
            # would shadow the Flask instance passed in as the parameter and
            # turn every `app.logger` call below — including the one in the
            # except handler — into an AttributeError, taking down startup on
            # the first boot that actually has a migration to run.
            from app import models  # noqa: F401 registers every model with db.metadata
            db.create_all()

            inspector = sa_inspect(db.engine)
            existing_tables = inspector.get_table_names()

            # Create gyms table if it doesn't exist (needed for gym scoping)
            if 'gyms' not in existing_tables:
                from app.models.gym import Gym
                Gym.__table__.create(db.engine)
                app.logger.info('Auto-migration: created gyms table')

            # Create device_tokens table if it doesn't exist
            if 'device_tokens' not in existing_tables:
                from app.models.device_token import DeviceToken
                DeviceToken.__table__.create(db.engine)
                app.logger.info('Auto-migration: created device_tokens table')

            # Create the regional manager's branch group table if it doesn't exist.
            #
            # This one is load-bearing for every request, not just the new role:
            # User.managed_branches loads eagerly (selectin), so a missing table
            # fails *any* query that touches a user — including login. Without
            # this the deploy is a full outage rather than one broken feature.
            if 'regional_manager_branches' not in existing_tables:
                from app.models.user import regional_manager_branches
                regional_manager_branches.create(db.engine)
                app.logger.info('Auto-migration: created regional_manager_branches table')

            # Staff-to-staff issues (distinct from member complaints).
            if 'issues' not in existing_tables:
                from app.models.issue import Issue
                Issue.__table__.create(db.engine)
                app.logger.info('Auto-migration: created issues table')

            # Add template_hash to fingerprints if missing. The model has
            # declared it for a while, and create_all() only builds whole
            # tables, so databases that predate the column never got it.
            # (Ported here from the old unauthenticated /api/admin/run-seed
            # endpoint, which has been removed.)
            if 'fingerprints' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('fingerprints')]
                if 'template_hash' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE fingerprints ADD COLUMN template_hash VARCHAR(255)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added template_hash column to fingerprints table')

            # Add gym_id column to users table if missing
            if 'users' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                if 'gym_id' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE users ADD COLUMN gym_id INTEGER REFERENCES gyms(id)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added gym_id column to users table')

            # Add gym_id column to branches table if missing
            if 'branches' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('branches')]
                if 'gym_id' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE branches ADD COLUMN gym_id INTEGER REFERENCES gyms(id)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added gym_id column to branches table')

            # Backfill users.gym_id from the gym their branch belongs to. Runs
            # after both gym_id columns are guaranteed to exist.
            #
            # Branch scope is now resolved through the user's gym (see
            # get_accessible_branch_ids), and that resolution fails closed —
            # so a staff row left with a NULL gym_id by the migration that
            # merely *added* the column would see nothing at all.
            if 'users' in existing_tables and 'branches' in existing_tables:
                backfilled = db.session.execute(text('''
                    UPDATE users
                    SET gym_id = (
                        SELECT b.gym_id FROM branches b
                        WHERE b.id = users.branch_id
                    )
                    WHERE gym_id IS NULL
                      AND branch_id IS NOT NULL
                ''')).rowcount
                db.session.commit()
                if backfilled:
                    app.logger.info(
                        f'Auto-migration: backfilled gym_id for {backfilled} user(s) from their branch'
                    )

            if 'transactions' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('transactions')]
                if 'discount' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE transactions ADD COLUMN discount NUMERIC(10, 2) NOT NULL DEFAULT 0'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added discount column to transactions table')

            # Add preferred_language column to users table if missing
            if 'users' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('users')]
                if 'preferred_language' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE users ADD COLUMN preferred_language VARCHAR(5)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added preferred_language column to users table')

            # Add preferred_language column to customers table if missing
            if 'customers' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('customers')]
                if 'preferred_language' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE customers ADD COLUMN preferred_language VARCHAR(5)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added preferred_language column to customers table')

            # Add created_by to subscriptions if missing.
            #
            # The model has declared it for a while but no migration ever added
            # it, so databases older than that commit raise
            # "no such column: subscriptions.created_by" on every Subscription
            # read. Backfill attributes each subscription to whoever created its
            # earliest transaction — the signup that opened it — which is what
            # lets /reports/employee-performance report a retention rate.
            if 'subscriptions' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('subscriptions')]
                if 'created_by' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE subscriptions ADD COLUMN created_by INTEGER REFERENCES users(id)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added created_by column to subscriptions table')

                    if 'transactions' in existing_tables:
                        db.session.execute(text('''
                            UPDATE subscriptions
                            SET created_by = (
                                SELECT t.created_by FROM transactions t
                                WHERE t.subscription_id = subscriptions.id
                                  AND t.created_by IS NOT NULL
                                ORDER BY t.created_at ASC, t.id ASC
                                LIMIT 1
                            )
                            WHERE created_by IS NULL
                        '''))
                        db.session.commit()
                        app.logger.info('Auto-migration: backfilled subscriptions.created_by from transactions')

            # Normalise expenses.category to the ExpenseCategory value form.
            #
            # It used to be free text. SQLAlchemy only validates enum strings on
            # read, so any stray value already on disk would raise LookupError
            # and take the money page down — for a column whose whole job is to
            # be grouped and filtered. Anything unrecognised is parked in OTHER:
            # the money is real and still has to land somewhere in the P&L.
            if 'expenses' in existing_tables:
                from app.models.expense import ExpenseCategory
                valid = {c.value for c in ExpenseCategory}
                by_name = {c.name: c.value for c in ExpenseCategory}

                stray = [
                    row[0] for row in db.session.execute(text(
                        'SELECT DISTINCT category FROM expenses WHERE category IS NOT NULL'
                    )).fetchall()
                    if row[0] not in valid
                ]

                for value in stray:
                    text_value = str(value).strip()
                    target = (
                        text_value.lower() if text_value.lower() in valid
                        else by_name.get(text_value.upper(), ExpenseCategory.OTHER.value)
                    )
                    db.session.execute(
                        text('UPDATE expenses SET category = :target WHERE category = :old'),
                        {'target': target, 'old': value},
                    )

                if stray:
                    db.session.commit()
                    app.logger.info(
                        f'Auto-migration: normalised {len(stray)} expense category value(s): {stray}'
                    )

            # Backfill indexes the models declare but that existing (already
            # created) tables predate — complaints.customer_id gets scanned
            # by every "this customer's complaints" lookup, and
            # daily_closings.closed_by by every "this staffer's closings" one.
            if 'complaints' in existing_tables:
                indexed_columns = {
                    col for idx in inspector.get_indexes('complaints') for col in idx['column_names']
                }
                if 'customer_id' not in indexed_columns:
                    db.session.execute(text(
                        'CREATE INDEX ix_complaints_customer_id ON complaints (customer_id)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added index on complaints.customer_id')

            if 'daily_closings' in existing_tables:
                indexed_columns = {
                    col for idx in inspector.get_indexes('daily_closings') for col in idx['column_names']
                }
                if 'closed_by' not in indexed_columns:
                    db.session.execute(text(
                        'CREATE INDEX ix_daily_closings_closed_by ON daily_closings (closed_by)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added index on daily_closings.closed_by')
        except Exception as e:
            app.logger.warning(f'Schema migration check: {e}')


def register_active_account_guard(app):
    """Reject any request whose JWT belongs to a deactivated account.

    ``role_required`` checks ``is_active``, but roughly half the routes are
    guarded by a bare ``@jwt_required()`` and read the user through
    ``get_current_user()``, which does not. Deactivating a staff member or a
    customer therefore left their existing token working until it expired —
    up to 12 hours for staff and 7 days for a client. Doing the check here
    covers every route at once, including ones added later.

    Checking ``get_current_user()`` instead would not work: 71 of its 79 call
    sites use the result without a None check, so returning None there turns a
    revoked session into an AttributeError 500 rather than a clean 401.
    """
    from flask import jsonify, request
    from flask_jwt_extended import get_jwt, verify_jwt_in_request
    from app.extensions import db

    @app.before_request
    def _reject_inactive_accounts():
        if request.method == 'OPTIONS':
            return None

        try:
            # optional=True so unauthenticated routes still pass through. A
            # malformed or expired token is left for the route's own decorator
            # to reject, so that (for example) logging in again with a stale
            # token in the header still works.
            if verify_jwt_in_request(optional=True) is None:
                return None
            claims = get_jwt()
        except Exception:
            return None

        # Read the flag as a scalar rather than loading the ORM object.
        # db.session.get() answers from the identity map, so a session that
        # already saw this row earlier would return a stale is_active and wave
        # a revoked account straight through. A column query always issues a
        # SELECT — and it also skips User.managed_branches, which is
        # selectin-eager and would otherwise fire an extra query per request.
        if claims.get('scope') == 'client':
            from app.models.customer import Customer
            customer_id = claims.get('customer_id')
            if customer_id is None:
                return None
            is_active = db.session.query(Customer.is_active).filter(
                Customer.id == customer_id
            ).scalar()
            if is_active is False:
                return jsonify({
                    'success': False,
                    'error': 'This account is no longer active',
                }), 401
            return None

        from app.models.user import User
        try:
            user_id = int(claims.get('sub'))
        except (TypeError, ValueError):
            return None

        is_active = db.session.query(User.is_active).filter(
            User.id == user_id
        ).scalar()
        if is_active is False:
            # 401 rather than 403: the session itself is no longer valid, so
            # the client should log out. The Flutter interceptor force-logs-out
            # on 401 and only shows a "no permission" toast on 403, which would
            # strand a deactivated user in a half-authenticated app.
            return jsonify({
                'success': False,
                'error': 'User account is inactive',
            }), 401
        return None


def register_error_handlers(app):
    """Register error handlers"""
    
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    @app.errorhandler(JWTExtendedException)
    def handle_jwt_exception(error):
        return jsonify({
            'success': False,
            'error': str(error)
        }), 401
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        return jsonify({
            'success': False,
            'error': error.description
        }), error.code
    
    @app.errorhandler(Exception)
    def handle_exception(error):
        app.logger.error(f'Unhandled exception: {str(error)}')
        return jsonify({
            'success': False,
            'error': 'An unexpected error occurred'
        }), 500


def register_cli_commands(app):
    """Register Flask CLI commands"""
    
    @app.cli.command('init-db')
    def init_db():
        """Initialize database"""
        from app.extensions import db
        db.create_all()
        print('✅ Database initialized successfully!')
    
    @app.cli.command('seed-db')
    def seed_db():
        """Seed database with test data"""
        from seed import seed_database
        seed_database()
        print('✅ Database seeded successfully!')
    
    @app.cli.command('reset-db')
    def reset_db():
        """Reset database (drop all tables and recreate)"""
        from app.extensions import db
        
        response = input('⚠️  This will delete all data. Are you sure? (yes/no): ')
        if response.lower() == 'yes':
            db.drop_all()
            db.create_all()
            print('✅ Database reset successfully!')
        else:
            print('❌ Operation cancelled.')
