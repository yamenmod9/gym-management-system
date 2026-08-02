"""
Flask extensions initialization
"""
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
cors = CORS()
ma = Marshmallow()


def _rate_limit_key():
    # Railway terminates TLS at its edge and proxies every request to this
    # container, so request.remote_addr is the proxy's address, not the
    # caller's — every client collapses onto the same key (or worse, a
    # rotating pool of edge IPs), and the limit below never actually
    # engages. Reusing geoip_service's X-Forwarded-For parsing (same
    # single-trusted-hop assumption it already documents) fixes that.
    from app.services.geoip_service import get_client_ip
    return get_client_ip(request)


# In-memory storage: counts reset per worker process rather than being
# shared across them, so the effective limit on a 2-worker deploy is closer
# to 2x what's configured below. Still closes off unlimited brute-forcing,
# which is what mattered — a shared store (Redis) is the upgrade if this
# service ever runs enough workers/instances for that gap to matter.
limiter = Limiter(key_func=_rate_limit_key, default_limits=[])


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
    limiter.init_app(app)
