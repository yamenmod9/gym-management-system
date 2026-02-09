"""
Notification Service - Abstract interface for sending codes
Supports SMS and Email delivery without hardcoding providers
"""
from abc import ABC, abstractmethod
from typing import Optional


class NotificationProvider(ABC):
    """Abstract base class for notification providers"""
    
    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        """
        Send SMS message
        
        Args:
            phone: Phone number
            message: Message content
        
        Returns:
            bool: True if sent successfully
        """
        pass
    
    @abstractmethod
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """
        Send email message
        
        Args:
            email: Email address
            subject: Email subject
            body: Email body
        
        Returns:
            bool: True if sent successfully
        """
        pass


class ConsoleNotificationProvider(NotificationProvider):
    """Console notification provider for development/testing"""
    
    def send_sms(self, phone: str, message: str) -> bool:
        """Print SMS to console"""
        print(f"\n{'='*60}")
        print(f"📱 SMS to {phone}")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        return True
    
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """Print email to console"""
        print(f"\n{'='*60}")
        print(f"📧 Email to {email}")
        print(f"Subject: {subject}")
        print(f"{'='*60}")
        print(body)
        print(f"{'='*60}\n")
        return True


class TwilioNotificationProvider(NotificationProvider):
    """Twilio SMS provider (stub for future implementation)"""
    
    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        # TODO: Initialize Twilio client
    
    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS via Twilio"""
        # TODO: Implement Twilio SMS
        print(f"[Twilio] Would send SMS to {phone}: {message}")
        return True
    
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """Twilio doesn't support email"""
        raise NotImplementedError("Twilio provider doesn't support email")


class SMTPNotificationProvider(NotificationProvider):
    """SMTP email provider (stub for future implementation)"""
    
    def __init__(self, smtp_host: str, smtp_port: int, username: str, password: str):
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        # TODO: Initialize SMTP connection
    
    def send_sms(self, phone: str, message: str) -> bool:
        """SMTP doesn't support SMS"""
        raise NotImplementedError("SMTP provider doesn't support SMS")
    
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """Send email via SMTP"""
        # TODO: Implement SMTP email
        print(f"[SMTP] Would send email to {email}: {subject}")
        return True


class NotificationService:
    """
    Notification service for sending activation codes
    Manages provider selection and message formatting
    """
    
    def __init__(self, provider: Optional[NotificationProvider] = None):
        """
        Initialize notification service
        
        Args:
            provider: Notification provider (defaults to ConsoleProvider)
        """
        self.provider = provider or ConsoleNotificationProvider()
    
    def send_activation_code(self, delivery_method: str, target: str, 
                            code: str, customer_name: str) -> bool:
        """
        Send activation code via specified method
        
        Args:
            delivery_method: 'sms' or 'email'
            target: Phone number or email address
            code: 6-digit activation code
            customer_name: Customer name for personalization
        
        Returns:
            bool: True if sent successfully
        """
        if delivery_method == 'sms':
            message = self._format_sms_message(code, customer_name)
            return self.provider.send_sms(target, message)
        elif delivery_method == 'email':
            subject, body = self._format_email_message(code, customer_name)
            return self.provider.send_email(target, subject, body)
        else:
            raise ValueError(f"Unknown delivery method: {delivery_method}")
    
    def _format_sms_message(self, code: str, customer_name: str) -> str:
        """Format SMS message"""
        return (
            f"Hello {customer_name},\n\n"
            f"Your gym activation code is: {code}\n\n"
            f"This code expires in 15 minutes.\n"
            f"Do not share this code with anyone.\n\n"
            f"- Dragon Gym"
        )
    
    def _format_email_message(self, code: str, customer_name: str) -> tuple:
        """Format email message (subject, body)"""
        subject = "Your Gym Activation Code"
        body = f"""
Hello {customer_name},

Your gym activation code is: {code}

This code will expire in 15 minutes.
For your security, please do not share this code with anyone.

If you did not request this code, please contact us immediately.

Best regards,
Dragon Gym Team
        """
        return subject, body.strip()
    
    def set_provider(self, provider: NotificationProvider):
        """Change notification provider"""
        self.provider = provider


# Global notification service instance
_notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get the global notification service instance"""
    return _notification_service


def configure_notification_service(provider: NotificationProvider):
    """Configure the global notification service with a specific provider"""
    _notification_service.set_provider(provider)
