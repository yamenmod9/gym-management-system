"""
Flask extensions initialization
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()


def init_extensions(app):
    """Initialize Flask extensions with app instance"""
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    origins = app.config['CORS_ORIGINS']
    # `Access-Control-Allow-Origin: *` and credentialed requests are mutually
    # exclusive per the CORS spec — asking for both makes flask-cors reflect
    # whatever Origin the caller sent, which is strictly weaker than the
    # wildcard it looks like. Auth here is a bearer header, not a cookie, so
    # credentials are only needed once an explicit allowlist is configured.
    allow_credentials = origins != '*'
    cors.init_app(app, resources={
        r"/*": {
            "origins": origins,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
            "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
            "expose_headers": ["Content-Type", "Authorization"],
            "supports_credentials": allow_credentials,
            "max_age": 3600
        }
    })
    ma.init_app(app)
