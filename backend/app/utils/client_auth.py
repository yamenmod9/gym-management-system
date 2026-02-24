"""
Client authentication utilities - JWT helpers for client tokens
"""
from functools import wraps
from flask import request
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.utils import error_response
from app.models import Customer
from app.extensions import db


def client_token_required(fn):
    """
    Decorator to require client JWT token
    Only allows tokens with scope='client'
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT is present
        verify_jwt_in_request()
        
        # Get JWT claims
        claims = get_jwt()
        
        # Verify this is a client token
        if claims.get('scope') != 'client':
            return error_response('Client access required', 403)
        
        # Verify customer_id is present
        if 'customer_id' not in claims:
            return error_response('Invalid client token', 403)
        
        return fn(*args, **kwargs)
    
    return wrapper


def get_current_client():
    """
    Get current authenticated client (customer)
    Must be called within client_token_required context
    
    Returns:
        Customer: Current customer object
    """
    claims = get_jwt()
    customer_id = claims.get('customer_id')
    
    if not customer_id:
        return None
    
    return db.session.get(Customer, customer_id)


def create_client_token(customer_id: int, expires_delta=None):
    """
    Create JWT token for client authentication
    
    Args:
        customer_id: Customer ID
        expires_delta: Token expiry time delta (default 7 days)
    
    Returns:
        str: JWT access token
    """
    from flask_jwt_extended import create_access_token
    from datetime import timedelta
    
    if expires_delta is None:
        expires_delta = timedelta(days=7)  # Client tokens last longer
    
    # Create token with client scope
    additional_claims = {
        'scope': 'client',
        'customer_id': customer_id
    }
    
    token = create_access_token(
        identity=str(customer_id),
        additional_claims=additional_claims,
        expires_delta=expires_delta
    )
    
    return token


def staff_token_required(fn):
    """
    Decorator to require staff JWT token
    Only allows tokens with scope='staff' or no scope (legacy)
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        # Verify JWT is present
        verify_jwt_in_request()
        
        # Get JWT claims
        claims = get_jwt()
        
        # Check scope - allow staff or no scope (backward compatibility)
        scope = claims.get('scope')
        if scope and scope != 'staff':
            return error_response('Staff access required', 403)
        
        return fn(*args, **kwargs)
    
    return wrapper
