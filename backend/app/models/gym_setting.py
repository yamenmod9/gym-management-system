"""
GymSetting model - per-gym on/off rules the owner controls.
"""
from datetime import datetime
from app.extensions import db


class GymSetting(db.Model):
    """A single named rule for one gym.

    Key/value rather than a column per rule: these are house rules that differ
    between gyms and accumulate over time, and a new one should not need a
    schema migration to ship. The catalogue of valid keys and their defaults
    lives in ``app.services.gym_rules`` — a row here only ever *overrides* a
    default, so a gym that has never opened the settings screen still behaves
    sensibly.
    """
    __tablename__ = 'gym_settings'
    __table_args__ = (
        db.UniqueConstraint('gym_id', 'key', name='uq_gym_settings_gym_key'),
    )

    id = db.Column(db.Integer, primary_key=True)
    gym_id = db.Column(db.Integer, db.ForeignKey('gyms.id'), nullable=False, index=True)
    key = db.Column(db.String(64), nullable=False, index=True)

    # Stored as text so the same table can hold non-boolean rules later
    # (thresholds, durations) without another migration.
    value = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<GymSetting gym={self.gym_id} {self.key}={self.value}>'
