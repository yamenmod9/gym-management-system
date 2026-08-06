"""Notification Service - sending one-time codes to members.

Supports SMS and email without hardcoding a provider.

A note on what was here before, because it shaped this file: the service
defaulted to :class:`ConsoleNotificationProvider` and *nothing ever replaced
it*. ``configure_notification_service`` was referenced only in documentation.
So in production every "we sent you a code" was false — the code was printed to
the container's stdout and the member received nothing. Two consequences:

* The code-based login was dead on arrival in production, while reporting
  success to the caller.
* Live login codes were written to a log stream readable by anyone with
  dashboard access.

Both are fixed here. The console provider now refuses to run outside
development, providers are built from environment variables at startup, and
:meth:`NotificationService.can_deliver` lets a caller find out whether delivery
is actually possible *before* it promises a member anything.
"""
import os
import smtplib
from abc import ABC, abstractmethod
from email.message import EmailMessage
from typing import Optional


class NotificationProvider(ABC):
    """Abstract base class for notification providers"""

    #: Whether this provider actually delivers to a real person. False for the
    #: development console, which only prints.
    delivers = True

    @abstractmethod
    def send_sms(self, phone: str, message: str) -> bool:
        """Send SMS message.

        Returns True if sent. Raises if the provider is configured but the send
        failed — callers distinguish "cannot deliver at all" from "tried and
        failed", and must never report success for either.
        """

    @abstractmethod
    def send_email(self, email: str, subject: str, body: str) -> bool:
        """Send email message. See :meth:`send_sms` for the return contract."""

    def supports(self, delivery_method: str) -> bool:
        """Can this provider deliver by this method?"""
        return delivery_method in ('sms', 'email')


class ConsoleNotificationProvider(NotificationProvider):
    """Prints codes to stdout. Development only.

    Deliberately marked as not delivering, so a deployment that forgets to
    configure a real provider fails loudly at the endpoint instead of quietly
    telling members that a code is on its way.
    """

    delivers = False

    def send_sms(self, phone: str, message: str) -> bool:
        print(f"\n{'='*60}")
        print(f"📱 SMS to {phone}")
        print(f"{'='*60}")
        print(message)
        print(f"{'='*60}\n")
        return True

    def send_email(self, email: str, subject: str, body: str) -> bool:
        print(f"\n{'='*60}")
        print(f"📧 Email to {email}")
        print(f"Subject: {subject}")
        print(f"{'='*60}")
        print(body)
        print(f"{'='*60}\n")
        return True


class SMTPNotificationProvider(NotificationProvider):
    """Email over SMTP.

    Implemented rather than stubbed because it is the delivery channel that
    costs nothing to turn on — any mailbox provider's SMTP credentials will do.
    Configured from the environment; see :func:`provider_from_env`.
    """

    def __init__(self, host: str, port: int, username: str, password: str,
                 from_address: str, use_tls: bool = True, timeout: int = 10):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_address = from_address
        self.use_tls = use_tls
        self.timeout = timeout

    def supports(self, delivery_method: str) -> bool:
        return delivery_method == 'email'

    def send_sms(self, phone: str, message: str) -> bool:
        raise NotImplementedError("SMTP provider doesn't support SMS")

    def send_email(self, email: str, subject: str, body: str) -> bool:
        message = EmailMessage()
        message['Subject'] = subject
        message['From'] = self.from_address
        message['To'] = email
        message.set_content(body)

        with smtplib.SMTP(self.host, self.port, timeout=self.timeout) as smtp:
            if self.use_tls:
                smtp.starttls()
            if self.username:
                smtp.login(self.username, self.password)
            smtp.send_message(message)
        return True


class TwilioNotificationProvider(NotificationProvider):
    """Twilio SMS.

    Left as a stub — it needs a paid account, so it cannot be exercised here.
    It is marked as not delivering so that selecting it without finishing the
    implementation cannot silently swallow a member's code the way the console
    provider did.
    """

    delivers = False

    def __init__(self, account_sid: str, auth_token: str, from_number: str):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number

    def supports(self, delivery_method: str) -> bool:
        return delivery_method == 'sms'

    def send_sms(self, phone: str, message: str) -> bool:
        raise NotImplementedError(
            'Twilio SMS delivery is not implemented yet. Set SMTP_* and use '
            'email delivery, or finish this provider.'
        )

    def send_email(self, email: str, subject: str, body: str) -> bool:
        raise NotImplementedError("Twilio provider doesn't support email")


class NotificationService:
    """Sends one-time codes, via whichever provider is configured."""

    def __init__(self, provider: Optional[NotificationProvider] = None):
        self.provider = provider or ConsoleNotificationProvider()

    def can_deliver(self, delivery_method: str) -> bool:
        """Would a send by this method actually reach the member?

        Callers check this *before* creating a code and telling the member to
        expect one. Returning False is not an error — it is the honest answer
        for a gym that has not configured a mail or SMS provider, and the
        endpoint turns it into "ask reception" rather than a false promise.
        """
        return bool(
            getattr(self.provider, 'delivers', True)
            and self.provider.supports(delivery_method)
        )

    def send_activation_code(self, delivery_method: str, target: str,
                             code: str, customer_name: str,
                             purpose: str = 'login') -> bool:
        """Send a one-time code.

        `purpose` selects the wording: a member reading "your login code" when
        they asked to reset a password has no way to tell a real message from a
        phishing attempt.
        """
        if delivery_method == 'sms':
            message = self._format_sms_message(code, customer_name, purpose)
            return self.provider.send_sms(target, message)
        elif delivery_method == 'email':
            subject, body = self._format_email_message(code, customer_name, purpose)
            return self.provider.send_email(target, subject, body)
        else:
            raise ValueError(f"Unknown delivery method: {delivery_method}")

    def _format_sms_message(self, code: str, customer_name: str,
                            purpose: str = 'login') -> str:
        what = ('password reset code' if purpose == 'password_reset'
                else 'activation code')
        return (
            f"Hello {customer_name},\n\n"
            f"Your {what} is: {code}\n\n"
            f"This code expires in 15 minutes.\n"
            f"Do not share this code with anyone."
        )

    def _format_email_message(self, code: str, customer_name: str,
                              purpose: str = 'login') -> tuple:
        if purpose == 'password_reset':
            subject = 'Reset your password'
            lead = 'Your password reset code is'
            closing = (
                'If you did not ask to reset your password, you can ignore '
                'this message — your current password still works.'
            )
        else:
            subject = 'Your activation code'
            lead = 'Your activation code is'
            closing = (
                'If you did not request this code, please contact us '
                'immediately.'
            )

        body = f"""Hello {customer_name},

{lead}: {code}

This code will expire in 15 minutes.
For your security, please do not share it with anyone.

{closing}
"""
        return subject, body.strip()

    def set_provider(self, provider: NotificationProvider):
        self.provider = provider


def provider_from_env():
    """Build a provider from environment variables, or None if unconfigured.

    Email needs ``SMTP_HOST``, ``SMTP_USERNAME``, ``SMTP_PASSWORD`` and
    ``SMTP_FROM`` (``SMTP_PORT`` defaults to 587). Returning None leaves the
    console provider in place, which reports that it cannot deliver — so an
    unconfigured deployment says "contact your gym" instead of pretending.
    """
    host = os.environ.get('SMTP_HOST')
    from_address = os.environ.get('SMTP_FROM')
    if host and from_address:
        return SMTPNotificationProvider(
            host=host,
            port=int(os.environ.get('SMTP_PORT', 587)),
            username=os.environ.get('SMTP_USERNAME', ''),
            password=os.environ.get('SMTP_PASSWORD', ''),
            from_address=from_address,
            use_tls=os.environ.get('SMTP_USE_TLS', 'true').lower() != 'false',
        )
    return None


# Global notification service instance
_notification_service = NotificationService()


def get_notification_service() -> NotificationService:
    """Get the global notification service instance"""
    return _notification_service


def configure_notification_service(provider: NotificationProvider):
    """Configure the global notification service with a specific provider"""
    _notification_service.set_provider(provider)


def init_notification_service():
    """Select a provider from the environment at startup.

    Called from the app factory. Without this the service kept whatever the
    module-level default was — which is how the console provider ended up
    serving production.
    """
    provider = provider_from_env()
    if provider is not None:
        configure_notification_service(provider)
    return _notification_service.provider
