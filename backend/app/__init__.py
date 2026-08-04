"""
Flask application factory
"""
import os
from flask import Flask, jsonify
from app.config import config
from app.extensions import init_extensions
from app.routes import register_blueprints
from flask_jwt_extended.exceptions import JWTExtendedException
from werkzeug.exceptions import HTTPException


def _init_sentry(environment):
    """Report unhandled exceptions to Sentry, if configured.

    A no-op without SENTRY_DSN set, so dev/test never touch a Sentry
    project and nothing changes here until the env var is added.
    """
    dsn = os.environ.get('SENTRY_DSN')
    if not dsn:
        return
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
    sentry_sdk.init(
        dsn=dsn,
        integrations=[FlaskIntegration()],
        environment=environment,
        traces_sample_rate=0.1,
    )


def create_app(config_name='default'):
    """
    Application factory pattern

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Flask application instance
    """
    _init_sentry(config_name)
    app = Flask(__name__)

    # Load configuration
    config_class = config[config_name]
    if hasattr(config_class, 'validate'):
        config_class.validate()
    app.config.from_object(config_class)

    # Config classes read DATABASE_URL when the module is first imported, which
    # is whenever something first touches `app.config` — often before a caller
    # has had a chance to set it. Re-reading it here binds the value that is
    # actually in the environment at boot, so import order cannot silently
    # point the app at the wrong database.
    database_url = os.environ.get('DATABASE_URL')
    if database_url:
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url

    # Initialize extensions
    init_extensions(app)

    # Register blueprints. Diagnostic endpoints stay out of production builds.
    register_blueprints(app, include_dev_tools=config_name != 'production')
    
    # Reject tokens belonging to deactivated accounts
    register_active_account_guard(app)

    # Register error handlers
    register_error_handlers(app)

    # Attach baseline security headers to every response
    register_security_headers(app)

    # Per-request caches must not outlive the request
    register_request_cache_reset(app)
    
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


#: Caches that hold for exactly one request. Each lives on ``flask.g`` and is
#: keyed by gym id, so a stale entry is a stale *value*, not another tenant's
#: data — an owner flipping a gym rule would otherwise keep seeing the old one.
_PER_REQUEST_CACHES = ('_gym_rules_cache', '_gym_branch_ids_cache')


def register_request_cache_reset(app):
    """Clear the per-request caches at the start of every request.

    ``flask.g`` is normally per request already, so this is belt-and-braces —
    but only *normally*: an app context that is pushed and left on the stack
    gets reused by subsequent requests, and then `g` (and everything cached on
    it) silently outlives the request it was built for. Clearing here makes the
    lifetime true by construction instead of by assumption.
    """
    @app.before_request
    def _reset_per_request_caches():
        from flask import g

        for attr in _PER_REQUEST_CACHES:
            if hasattr(g, attr):
                delattr(g, attr)


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

            _sync_enum_values(app)

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

            # Does holding this service open the door? Defaults true so every
            # service that predates the column behaves exactly as before —
            # only a personal-training package opts out.
            if 'services' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('services')]
                if 'grants_gym_entry' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE services ADD COLUMN grants_gym_entry BOOLEAN NOT NULL DEFAULT 1'
                        if db.engine.dialect.name == 'sqlite' else
                        'ALTER TABLE services ADD COLUMN grants_gym_entry BOOLEAN NOT NULL DEFAULT TRUE'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added grants_gym_entry column to services table')

            # The captain a member trains with, on private-training subscriptions.
            if 'subscriptions' in existing_tables:
                columns = [col['name'] for col in inspector.get_columns('subscriptions')]
                if 'trainer_id' not in columns:
                    db.session.execute(text(
                        'ALTER TABLE subscriptions ADD COLUMN trainer_id INTEGER REFERENCES users(id)'
                    ))
                    db.session.commit()
                    app.logger.info('Auto-migration: added trainer_id column to subscriptions table')

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

                # One closing per branch per day. Both writers check for an
                # existing row and then insert, which two tills closing at the
                # same moment can both pass — double-counting that day's revenue
                # and leaving two contradictory cash differences. A unique index
                # rather than ALTER TABLE ADD CONSTRAINT so the same statement
                # works on SQLite as well as Postgres.
                unique_index_names = {
                    idx['name'] for idx in inspector.get_indexes('daily_closings')
                    if idx.get('unique')
                }
                existing_constraints = set()
                try:
                    existing_constraints = {
                        c['name'] for c in
                        inspector.get_unique_constraints('daily_closings')
                    }
                except Exception:
                    pass

                if 'uq_daily_closing_branch_date' not in (
                        unique_index_names | existing_constraints):
                    db.session.execute(text(
                        'CREATE UNIQUE INDEX uq_daily_closing_branch_date '
                        'ON daily_closings (branch_id, closing_date)'
                    ))
                    db.session.commit()
                    app.logger.info(
                        'Auto-migration: added unique index on '
                        'daily_closings(branch_id, closing_date)'
                    )
        except Exception as e:
            app.logger.warning(f'Schema migration check: {e}')


def _sync_enum_values(app):
    """Add enum values the models declare but the database's enum types lack.

    Postgres builds each enum type once, when create_all() first creates the
    table using it, and never revisits it. Adding a member to a Python enum
    (a new UserRole, say) therefore leaves the database type behind, and every
    insert or read of the new value dies with InvalidTextRepresentation —
    at runtime, on a deploy that looked completely clean.

    Only Postgres needs this. SQLite stores these columns as VARCHAR, so a new
    member needs no DDL there.
    """
    from sqlalchemy import Enum as SAEnum, text
    from app.extensions import db

    if db.engine.dialect.name != 'postgresql':
        return

    # What the models say each named enum type should contain. SQLAlchemy
    # persists PEP-435 enums by member *name*, so .enums is the name list.
    declared = {}
    for table in db.metadata.tables.values():
        for column in table.columns:
            if isinstance(column.type, SAEnum) and column.type.name:
                declared.setdefault(column.type.name, set()).update(column.type.enums)
    if not declared:
        return

    existing = {}
    for typname, label in db.session.execute(text(
        'SELECT t.typname, e.enumlabel FROM pg_type t '
        'JOIN pg_enum e ON e.enumtypid = t.oid'
    )).fetchall():
        existing.setdefault(typname, set()).add(label)

    for type_name, labels in declared.items():
        # A type absent here doesn't exist yet; create_all() builds those with
        # the full member set already, so there is nothing to patch.
        if type_name not in existing:
            continue
        missing = sorted(labels - existing[type_name])
        if not missing:
            continue
        # ALTER TYPE ... ADD VALUE takes a literal, not a bind parameter, and
        # the value cannot be used by the same transaction that adds it —
        # hence a dedicated AUTOCOMMIT connection. Every label interpolated
        # here comes from our own model definitions, never from a request.
        with db.engine.connect().execution_options(isolation_level='AUTOCOMMIT') as conn:
            for label in missing:
                conn.execute(text(
                    f"ALTER TYPE {type_name} ADD VALUE IF NOT EXISTS '{label}'"
                ))
        app.logger.info(
            f'Auto-migration: added {missing} to enum type {type_name}'
        )


#: Blueprints whose routes authenticate from the request body (phone plus
#: password, or an activation code) rather than from a token. A member's app
#: may still send a stale Authorization header to them, and rejecting that
#: would break logging in or changing a password.
_CLIENT_CREDENTIAL_BLUEPRINTS = frozenset({'client_auth', 'client_compat'})


def _endpoint_allows_client_token(app):
    """Whether the endpoint being served accepts a member's token.

    True for anything wrapped in ``client_token_required`` (which tags itself)
    and for the credential-based client auth routes. Everything else is staff
    surface, where a client token must not be honoured.
    """
    from flask import request

    if request.blueprint in _CLIENT_CREDENTIAL_BLUEPRINTS:
        return True

    view = app.view_functions.get(request.endpoint)
    return bool(getattr(view, '_allows_client_token', False))


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

            # A member's token must not be usable as a staff account.
            #
            # Both token kinds are signed with the same secret and carry a bare
            # numeric identity: a staff token's is a users.id, a client token's
            # is a customers.id. The two id spaces start at 1 and count up
            # independently, so they collide constantly — and nothing on the
            # staff side looked at `scope`. get_current_user() called int() on
            # the identity and loaded that row out of `users`, so a member
            # holding customer id 7 was served as staff user 7, with whatever
            # role that user has.
            #
            # Enforced here rather than inside get_current_user() because 71 of
            # its 79 call sites use the result without a None check, and because
            # running before the view means no route-level `except Exception`
            # can turn the rejection into a 500 that still executed.
            if not _endpoint_allows_client_token(app):
                return jsonify({
                    'success': False,
                    'error': 'Client access is not permitted on this endpoint',
                }), 403

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


def register_security_headers(app):
    """Attach baseline security headers to every response.

    Railway terminates TLS in front of this app, so HSTS is always safe to
    send here — there's no self-redirect-loop risk from checking
    request.is_secure the way there would be running behind a proxy that
    doesn't forward HTTPS. The API returns JSON (plus a handful of static
    logo images); it never renders third-party-embeddable HTML, so a strict
    CSP has no legitimate response to relax it for.
    """
    @app.after_request
    def _add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'none'; frame-ancestors 'none'"
        return response


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
