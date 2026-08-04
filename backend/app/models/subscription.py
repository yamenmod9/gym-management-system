"""
Subscription model - Customer subscriptions to services
"""
from datetime import datetime, timedelta
from app.extensions import db
import enum


class SubscriptionStatus(enum.Enum):
    """Subscription status"""
    ACTIVE = 'active'
    FROZEN = 'frozen'
    STOPPED = 'stopped'
    EXPIRED = 'expired'


class Subscription(db.Model):
    """Subscription model - links customers to services"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    
    # References
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship('Customer', back_populates='subscriptions')
    
    service_id = db.Column(db.Integer, db.ForeignKey('services.id'), nullable=False, index=True)
    service = db.relationship('Service', back_populates='subscriptions')
    
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'), nullable=False, index=True)
    branch = db.relationship('Branch', back_populates='subscriptions')
    
    # Dates
    start_date = db.Column(db.Date, nullable=False, index=True)
    end_date = db.Column(db.Date, nullable=False, index=True)
    
    # Status
    status = db.Column(db.Enum(SubscriptionStatus), default=SubscriptionStatus.ACTIVE, nullable=False, index=True)
    
    # Freeze tracking
    freeze_count = db.Column(db.Integer, default=0)
    total_frozen_days = db.Column(db.Integer, default=0)
    
    # Stop information
    stop_reason = db.Column(db.Text, nullable=True)
    stopped_at = db.Column(db.DateTime, nullable=True)
    
    # Classes tracking (for education programs)
    classes_attended = db.Column(db.Integer, default=0)
    
    # Visit/Class tracking (for entry system)
    remaining_visits = db.Column(db.Integer, nullable=True)  # For unlimited or visit-based subscriptions
    remaining_classes = db.Column(db.Integer, nullable=True)  # For class-based subscriptions
    
    # Subscription type and display tracking
    subscription_type = db.Column(db.String(20), nullable=True)  # coins, time_based, sessions, training
    remaining_coins = db.Column(db.Integer, nullable=True)  # For coin-based subscriptions
    total_coins = db.Column(db.Integer, nullable=True)  # Original coin count
    remaining_sessions = db.Column(db.Integer, nullable=True)  # For session/training subscriptions
    total_sessions = db.Column(db.Integer, nullable=True)  # Original session count

    # Who created this subscription (staff member)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)

    # The captain on a private-training subscription; NULL for everything else.
    # Distinct from created_by: reception creates the subscription, the trainer
    # named here is who the member actually trains with.
    trainer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    trainer = db.relationship('User', foreign_keys=[trainer_id])

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    freeze_history = db.relationship('FreezeHistory', back_populates='subscription', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Subscription {self.id} - {self.customer.full_name} - {self.service.name}>'

    # Names for schema serialisation. SubscriptionSchema declared all of these
    # and the model exposed none of them, so the list endpoint returned bare
    # ids — no member, no service, no branch — while the single-record endpoint
    # (which goes through to_dict) returned them in full.

    @property
    def customer_name(self):
        return self.customer.full_name if self.customer else None

    @property
    def customer_phone(self):
        return self.customer.phone if self.customer else None

    @property
    def service_name(self):
        return self.service.name if self.service else None

    @property
    def service_type(self):
        return self.service.service_type.value if self.service else None

    @property
    def branch_name(self):
        return self.branch.name if self.branch else None

    # ── Lookups ──────────────────────────────────────────────────────────
    #
    # A member may hold several subscriptions at once (gym entry, private
    # training with a captain, a combined package). Every caller that used to
    # ask for "the" subscription with .first() was really asking one of two
    # different questions, and answering the wrong one silently drains the
    # wrong package — a door scan deducting a coin from someone's training
    # sessions. The two helpers below are those two questions, named.

    @staticmethod
    def entry_query(customer_id, allow_non_entry=False, statuses=None):
        """Base query for the subscriptions that open the door for this member.

        The single definition of "grants entry". Every door path narrows this
        rather than rebuilding the join, so the rule cannot drift between the
        turnstile, the QR scan and the fingerprint reader.
        """
        from app.models.service import Service

        if statuses is None:
            statuses = [SubscriptionStatus.ACTIVE, SubscriptionStatus.FROZEN]

        query = Subscription.query.join(Service, Subscription.service_id == Service.id).filter(
            Subscription.customer_id == customer_id,
            Subscription.status.in_(statuses),
        )
        if not allow_non_entry:
            query = query.filter(Service.grants_gym_entry.is_(True))
        return query

    @staticmethod
    def entry_subscription_for(customer_id, allow_non_entry=False):
        """The subscription that should open the door for this member, if any.

        Only subscriptions whose service grants gym entry qualify, so a member
        holding private training alone is turned away — unless the gym has
        switched on the rule that lets them in, which is what
        ``allow_non_entry`` carries.

        Active is preferred over frozen so the caller can still distinguish
        "no subscription" from "frozen" and report the freeze reason; returning
        a frozen one first would make that branch unreachable.
        """
        candidates = Subscription.entry_query(customer_id, allow_non_entry).order_by(
            (Subscription.status == SubscriptionStatus.ACTIVE).desc(),
            Subscription.end_date.desc(),
        ).all()

        # A freeze that has run its course must not still bar the door. Settled
        # here, on the read that cares, because nothing else will do it.
        if any(s.settle_expired_freeze() for s in candidates):
            candidates.sort(
                key=lambda s: (s.status != SubscriptionStatus.ACTIVE, -s.end_date.toordinal())
            )

        return candidates[0] if candidates else None

    @staticmethod
    def active_for(customer_id):
        """Every active subscription this member holds, newest expiry first.

        For display: the member's app and their profile should show the whole
        picture, not whichever row the database happened to return first.
        """
        return Subscription.query.filter(
            Subscription.customer_id == customer_id,
            Subscription.status == SubscriptionStatus.ACTIVE,
        ).order_by(Subscription.end_date.desc()).all()

    def is_expired(self):
        """Check if subscription is expired"""
        if self.status == SubscriptionStatus.EXPIRED:
            return True
        if self.end_date < datetime.utcnow().date():
            self.status = SubscriptionStatus.EXPIRED
            db.session.commit()
            return True
        return False

    def can_access(self):
        """Check if customer can access facility"""
        return self.status == SubscriptionStatus.ACTIVE and not self.is_expired()
    
    @property
    def remaining_days(self):
        """Calculate remaining days for time-based subscriptions"""
        if self.subscription_type == 'coins':
            return None  # Coins don't expire by days
        if self.end_date:
            delta = self.end_date - datetime.utcnow().date()
            return max(0, delta.days)
        return 0

    def freeze(self, days, reason=None):
        """Freeze subscription"""
        if self.status != SubscriptionStatus.ACTIVE:
            return False, "Subscription is not active"
        
        if self.freeze_count >= self.service.freeze_count_limit:
            return False, "Freeze limit reached"
        
        if self.total_frozen_days + days > self.service.freeze_max_days:
            return False, "Total freeze days exceeded"
        
        self.status = SubscriptionStatus.FROZEN
        self.freeze_count += 1
        self.total_frozen_days += days
        
        # Extend end date
        self.end_date += timedelta(days=days)
        
        return True, "Subscription frozen successfully"

    def unfreeze(self):
        """Unfreeze subscription"""
        if self.status == SubscriptionStatus.FROZEN:
            self.status = SubscriptionStatus.ACTIVE
            return True, "Subscription unfrozen successfully"
        return False, "Subscription is not frozen"

    def settle_expired_freeze(self):
        """End a freeze whose agreed period has already passed.

        Freezing set the status to FROZEN, extended end_date by the agreed days
        and recorded a FreezeHistory row with the date the freeze was meant to
        end — and then nothing ever ended it. Only the manual unfreeze endpoint
        could, so a member who froze for a week was still refused at the door a
        month later, having already been charged for the extension.

        Derived on read rather than scheduled, for the same reason the private
        session auto-confirm is: this deployment has no worker process, so a
        status that depended on one would sit stale forever.

        Returns True if a freeze was ended.
        """
        if self.status != SubscriptionStatus.FROZEN:
            return False

        from app.models.freeze_history import FreezeHistory

        active_freeze = FreezeHistory.query.filter_by(
            subscription_id=self.id, is_active=True
        ).order_by(FreezeHistory.freeze_end.desc()).first()

        # No record of when it should end means it can only be ended by hand.
        if active_freeze is None or active_freeze.freeze_end is None:
            return False
        if active_freeze.freeze_end >= datetime.utcnow().date():
            return False

        self.status = SubscriptionStatus.ACTIVE
        active_freeze.is_active = False
        active_freeze.unfrozen_at = datetime.utcnow()

        # The freeze deactivated their fingerprints; ending it restores them.
        from app.models.fingerprint import Fingerprint
        for fp in Fingerprint.query.filter_by(customer_id=self.customer_id).all():
            fp.is_active = True
            fp.deactivation_reason = None

        db.session.commit()
        return True

    def stop(self, reason):
        """Stop subscription"""
        if self.status == SubscriptionStatus.STOPPED:
            return False, "Subscription is already stopped"
        
        self.status = SubscriptionStatus.STOPPED
        self.stop_reason = reason
        self.stopped_at = datetime.utcnow()
        return True, "Subscription stopped successfully"
    
    @property
    def display_metric(self):
        """Get display metric type for client app"""
        if self.subscription_type == 'coins':
            return 'coins'
        elif self.subscription_type == 'time_based':
            return 'time'
        elif self.subscription_type == 'sessions':
            return 'sessions'
        elif self.subscription_type == 'training':
            return 'training'
        else:
            return 'time'  # Default to time-based
    
    @property
    def display_value(self):
        """Get display value for client app"""
        if self.subscription_type == 'coins':
            return self.remaining_coins or 0
        elif self.subscription_type == 'time_based':
            days = (self.end_date - datetime.now().date()).days
            return days if days > 0 else 0
        elif self.subscription_type in ['sessions', 'training']:
            return self.remaining_sessions or 0
        else:
            # Default to time-based calculation
            days = (self.end_date - datetime.now().date()).days
            return days if days > 0 else 0
    
    @property
    def display_label(self):
        """Get formatted display label for client app"""
        if self.subscription_type == 'coins':
            coins = self.remaining_coins or 0
            return f"{coins} Coins" if coins != 1 else "1 Coin"
        elif self.subscription_type == 'time_based':
            days = (self.end_date - datetime.now().date()).days
            if days <= 0:
                return "Expired"
            months = days // 30
            remaining_days = days % 30
            if months > 0:
                return f"{months} month{'s' if months != 1 else ''}, {remaining_days} day{'s' if remaining_days != 1 else ''}"
            return f"{days} day{'s' if days != 1 else ''}"
        elif self.subscription_type == 'sessions':
            sessions = self.remaining_sessions or 0
            return f"{sessions} Sessions" if sessions != 1 else "1 Session"
        elif self.subscription_type == 'training':
            sessions = self.remaining_sessions or 0
            return f"{sessions} Training Sessions" if sessions != 1 else "1 Training Session"
        else:
            # Default to time-based
            days = (self.end_date - datetime.now().date()).days
            if days <= 0:
                return "Expired"
            return f"{days} day{'s' if days != 1 else ''}"

    def to_dict(self):
        """Convert to dictionary"""
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': self.customer.full_name,
            'customer_phone': self.customer.phone,
            'service_id': self.service_id,
            'service_name': self.service.name,
            'service_type': self.service.service_type.value,
            'grants_gym_entry': self.service.grants_gym_entry,
            'trainer_id': self.trainer_id,
            'trainer_name': self.trainer.full_name if self.trainer else None,
            'branch_id': self.branch_id,
            'branch_name': self.branch.name,
            'start_date': self.start_date.isoformat(),
            'end_date': self.end_date.isoformat(),
            'status': self.status.value,
            'freeze_count': self.freeze_count,
            'total_frozen_days': self.total_frozen_days,
            'stop_reason': self.stop_reason,
            'stopped_at': self.stopped_at.isoformat() if self.stopped_at else None,
            'classes_attended': self.classes_attended,
            'created_at': self.created_at.isoformat(),
            'is_expired': self.is_expired(),
            'can_access': self.can_access(),
            # Display fields for client app
            'subscription_type': self.subscription_type,
            'remaining_coins': self.remaining_coins,
            'total_coins': self.total_coins,
            'remaining_sessions': self.remaining_sessions,
            'total_sessions': self.total_sessions,
            'remaining_days': self.remaining_days,
            'display_metric': self.display_metric,
            'display_value': self.display_value,
            'display_label': self.display_label
        }
