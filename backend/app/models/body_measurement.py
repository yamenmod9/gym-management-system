"""A member's body composition, as measured on a given day.

Until this table existed there was no history at all. Height, weight, BMI, BMR,
ideal weight and daily calories were single columns on ``customers``,
overwritten every time reception edited the record — so a member who had been
training for a year had exactly one number, today's, and no way to see that it
had moved. Nothing was archived; the previous values were destroyed on write.

Each row here is one weigh-in and is never updated. The customer's own columns
are still maintained as the *latest* values, so every existing screen keeps
working; this is the record of how they got there.
"""
from datetime import datetime

from app.extensions import db
from app.services import body_metrics


class BodyMeasurement(db.Model):
    """One InBody reading."""
    __tablename__ = 'body_measurements'

    id = db.Column(db.Integer, primary_key=True)

    customer_id = db.Column(
        db.Integer, db.ForeignKey('customers.id'), nullable=False, index=True)
    customer = db.relationship(
        'Customer', backref=db.backref('measurements', lazy='dynamic'))

    # Who took it and where. Kept even after the staff member leaves, which is
    # why this is nullable and never cascades.
    recorded_by = db.Column(
        db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    recorder = db.relationship('User', foreign_keys=[recorded_by])
    branch_id = db.Column(
        db.Integer, db.ForeignKey('branches.id'), nullable=True, index=True)

    #: When the member stood on the machine — not when the row was typed in.
    #: Separate from created_at so a reading entered the next morning still
    #: charts on the day it was taken.
    measured_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # ── measured ──────────────────────────────────────────────────────────
    weight_kg = db.Column(db.Float, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    body_fat_percent = db.Column(db.Float, nullable=True)
    skeletal_muscle_mass_kg = db.Column(db.Float, nullable=True)
    body_water_litres = db.Column(db.Float, nullable=True)
    visceral_fat_level = db.Column(db.Integer, nullable=True)
    bone_mineral_kg = db.Column(db.Float, nullable=True)
    inbody_score = db.Column(db.Integer, nullable=True)

    # ── derived, via app/services/body_metrics ────────────────────────────
    bmi = db.Column(db.Float, nullable=True)
    bmi_category = db.Column(db.String(20), nullable=True)
    bmr = db.Column(db.Float, nullable=True)
    ideal_weight = db.Column(db.Float, nullable=True)
    daily_calories = db.Column(db.Integer, nullable=True)
    body_fat_mass_kg = db.Column(db.Float, nullable=True)

    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    #: Every field a caller may set. Anything outside this is either derived or
    #: nobody's business to supply — listing it here means a new column cannot
    #: be silently mass-assigned from a request body.
    MEASURED_FIELDS = (
        'weight_kg', 'height_cm', 'body_fat_percent',
        'skeletal_muscle_mass_kg', 'body_water_litres', 'visceral_fat_level',
        'bone_mineral_kg', 'inbody_score',
    )

    def __repr__(self):
        return f'<BodyMeasurement customer={self.customer_id} at={self.measured_at}>'

    def recompute(self, age_years, gender_value):
        """Fill the derived columns from what was measured."""
        for field, value in body_metrics.derive_all(
            weight_kg=self.weight_kg,
            height_cm=self.height_cm,
            age_years=age_years,
            gender_value=gender_value,
            body_fat_percent=self.body_fat_percent,
        ).items():
            setattr(self, field, value)

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'measured_at': self.measured_at.isoformat() if self.measured_at else None,
            'branch_id': self.branch_id,
            'recorded_by': self.recorded_by,
            'recorded_by_name': self.recorder.full_name if self.recorder else None,
            'weight_kg': self.weight_kg,
            'height_cm': self.height_cm,
            'body_fat_percent': self.body_fat_percent,
            'skeletal_muscle_mass_kg': self.skeletal_muscle_mass_kg,
            'body_water_litres': self.body_water_litres,
            'visceral_fat_level': self.visceral_fat_level,
            'bone_mineral_kg': self.bone_mineral_kg,
            'inbody_score': self.inbody_score,
            'bmi': self.bmi,
            'bmi_category': self.bmi_category,
            'bmr': self.bmr,
            'ideal_weight': self.ideal_weight,
            'daily_calories': self.daily_calories,
            'body_fat_mass_kg': self.body_fat_mass_kg,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
