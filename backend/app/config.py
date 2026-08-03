import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()


class ConfigError(RuntimeError):
    """Raised at import time when a required production setting is missing."""


#: Settings that have no safe default outside development. Checked by
#: ``ProductionConfig.validate()`` at app-creation time rather than at import
#: time, so that importing this module in dev/test never explodes.
REQUIRED_IN_PRODUCTION = ('SECRET_KEY', 'JWT_SECRET_KEY')


def _parse_origins(raw, default):
    """Turn a comma-separated CORS_ORIGINS env var into a list.

    '*' stays a bare string because flask-cors treats the wildcard specially.
    """
    if not raw:
        return default
    origins = [origin.strip() for origin in raw.split(',') if origin.strip()]
    if not origins or origins == ['*']:
        return '*'
    return origins


def _normalize_database_url(url):
    """Railway/Heroku-style Postgres addons hand out `postgres://` URLs, but
    SQLAlchemy 1.4+ only recognizes the `postgresql://` dialect prefix and
    raises NoSuchModuleError on the old one."""
    if url and url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql://', 1)
    return url


class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.getenv('DATABASE_URL', 'sqlite:///gym_management.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # pool_pre_ping pings each connection before reuse so a connection the DB
    # server already dropped (MySQL's wait_timeout, common on shared hosting
    # like PythonAnywhere) gets silently replaced instead of surfacing as a
    # 500 on the next request. pool_recycle forces a refresh before that
    # timeout is hit at all.
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 280,
    }
    
    # JWT Configuration
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=12)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    JWT_TOKEN_LOCATION = ['headers']
    JWT_HEADER_NAME = 'Authorization'
    JWT_HEADER_TYPE = 'Bearer'
    
    # Pagination
    ITEMS_PER_PAGE = 20
    MAX_ITEMS_PER_PAGE = 100
    
    # File Upload (for future expansion)
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # CORS Configuration
    # Allow all origins for development. Restrict in production.
    CORS_ORIGINS = _parse_origins(os.getenv('CORS_ORIGINS'), default='*')

    # Supabase Storage (gym logo uploads). Not in REQUIRED_IN_PRODUCTION:
    # unlike SECRET_KEY/JWT_SECRET_KEY, missing these only fails logo
    # uploads specifically (a clear 502), not the whole app's security model.
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    # Override with environment variables in production
    SQLALCHEMY_DATABASE_URI = _normalize_database_url(
        os.getenv('DATABASE_URL', 'sqlite:///gym_management.db')
    )

    # Set CORS_ORIGINS to a comma-separated allowlist of the front-end origins
    # (e.g. "https://app.example.com,https://admin.example.com"). Left unset it
    # stays permissive so existing deploys keep working.
    CORS_ORIGINS = _parse_origins(os.getenv('CORS_ORIGINS'), default='*')

    @staticmethod
    def validate():
        """Refuse to boot on the committed development secrets.

        JWT_SECRET_KEY signs every access token, so a production deploy that
        silently fell back to the default in ``Config`` would let anyone who
        has read this file mint a valid owner/super-admin token.
        """
        missing = [name for name in REQUIRED_IN_PRODUCTION if not os.getenv(name)]
        if missing:
            raise ConfigError(
                'Refusing to start in production without: '
                + ', '.join(missing)
                + '. Set them in the deployment environment.'
            )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    # Honour DATABASE_URL so a test module can point at its own throwaway file.
    # The fixed fallback is a real file on disk and therefore survives between
    # runs — a fixture that seeds into it hits unique-constraint errors on the
    # second run rather than starting clean.
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///test_gym.db')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # The suite logs in far more often than a human would, from a single
    # client address; leaving the limiter on just throttles the tests and
    # turns unrelated assertions into 429s.
    RATELIMIT_ENABLED = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
