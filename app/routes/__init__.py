"""
Routes initialization - Register all blueprints
"""
from .auth_routes import auth_bp
from .users_routes import users_bp
from .branches_routes import branches_bp
from .customers_routes import customers_bp
from .services_routes import services_bp
from .subscriptions_routes import subscriptions_bp
from .transactions_routes import transactions_bp
from .expenses_routes import expenses_bp
from .complaints_routes import complaints_bp
from .fingerprints_routes import fingerprints_bp
from .dashboards_routes import dashboards_bp
from .test_routes import test_bp


def register_blueprints(app):
    """Register all application blueprints"""
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(branches_bp)
    app.register_blueprint(customers_bp)
    app.register_blueprint(services_bp)
    app.register_blueprint(subscriptions_bp)
    app.register_blueprint(transactions_bp)
    app.register_blueprint(expenses_bp)
    app.register_blueprint(complaints_bp)
    app.register_blueprint(fingerprints_bp)
    app.register_blueprint(dashboards_bp)
    app.register_blueprint(test_bp)
