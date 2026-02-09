"""
Activation Code model - For client activation
"""
from datetime import datetime, timedelta
from app.extensions import db
import enum
import hashlib
import secrets


class ActivationCodeType(enum.Enum):
    """Activation code types"""
    REGISTRATION = 'registration'
    LOGIN = 'login'
    PASSWORD_RESET = 'password_reset'


class ActivationCode(db.Model):
    """Activation code for client authentication"""
    __tablename__ = 'activation_codes'

    id = db.Column(db.Integer, primary_key=True)
    
    # Code details
    code_hash = db.Column(db.String(64), nullable=False, index=True)
    code_type = db.Column(db.Enum(ActivationCodeType), nullable=False, default=ActivationCodeType.LOGIN)
    
    # Association
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer', backref=db.backref('activation_codes', lazy='dynamic'))
    
    # Delivery
    delivery_method = db.Column(db.String(20), nullable=False)  # 'sms', 'email'
    delivery_target = db.Column(db.String(120), nullable=False)  # phone or email
    
    # Status
    is_used = db.Column(db.Boolean, default=False, nullable=False)
    attempts = db.Column(db.Integer, default=0, nullable=False)
    max_attempts = db.Column(db.Integer, default=3, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    used_at = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<ActivationCode {self.id} for Customer {self.customer_id}>'

    @staticmethod
    def generate_code():
        """Generate a 6-digit activation code"""
        return ''.join([str(secrets.randbelow(10)) for _ in range(6)])

    @staticmethod
    def hash_code(code):
        """Hash the activation code using SHA-256"""
        return hashlib.sha256(code.encode()).hexdigest()

    @classmethod
    def create_code(cls, customer_id, delivery_method, delivery_target, 
                    code_type=ActivationCodeType.LOGIN, expiry_minutes=15):
        """
        Create a new activation code
        
        Args:
            customer_id: Customer ID
            delivery_method: 'sms' or 'email'
            delivery_target: Phone number or email address
            code_type: Type of activation code
            expiry_minutes: Code validity in minutes (default 15)
        
        Returns:
            tuple: (ActivationCode object, plain_code string)
        """
        # Generate plain code
        plain_code = cls.generate_code()
        
        # Create activation code record
        activation_code = cls(
            customer_id=customer_id,
            code_hash=cls.hash_code(plain_code),
            code_type=code_type,
            delivery_method=delivery_method,
            delivery_target=delivery_target,
            expires_at=datetime.utcnow() + timedelta(minutes=expiry_minutes)
        )
        
        db.session.add(activation_code)
        
        return activation_code, plain_code

    def verify_code(self, code):
        """
        Verify if provided code matches
        
        Args:
            code: Plain text code to verify
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Check if already used
        if self.is_used:
            return False
        
        # Check if expired
        if datetime.utcnow() > self.expires_at:
            return False
        
        # Check max attempts
        if self.attempts >= self.max_attempts:
            return False
        
        # Increment attempts
        self.attempts += 1
        
        # Verify hash
        if self.code_hash == self.hash_code(code):
            self.is_used = True
            self.used_at = datetime.utcnow()
            return True
        
        return False

    def is_valid(self):
        """Check if code is still valid (not used, not expired, attempts left)"""
        if self.is_used:
            return False
        if datetime.utcnow() > self.expires_at:
            return False
        if self.attempts >= self.max_attempts:
            return False
        return True

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'code_type': self.code_type.value,
            'delivery_method': self.delivery_method,
            'delivery_target': self.delivery_target,
            'is_used': self.is_used,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat(),
            'used_at': self.used_at.isoformat() if self.used_at else None
        }
