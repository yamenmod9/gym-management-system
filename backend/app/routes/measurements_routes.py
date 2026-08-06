"""Body composition history — recording it, and the two audiences who read it.

Staff record a weigh-in against a member; the member reads their own history;
a captain reads the history of the members who train privately with them, and
nobody else's. That last rule is the one worth stating twice, because a trainer
is otherwise an ordinary branch-scoped staff member who can see every member at
their branch.
"""
from datetime import datetime

from flask import Blueprint, request
from flask_jwt_extended import jwt_required

from app.extensions import db
from app.models.body_measurement import BodyMeasurement
from app.models.customer import Customer
from app.models.user import UserRole
from app.services.coaching_access import trainer_has_client
from app.utils import (
    success_response, error_response, role_required, get_current_user,
    get_accessible_branch_ids,
)
from app.utils.client_auth import client_token_required, get_current_client

measurements_bp = Blueprint('measurements', __name__, url_prefix='/api')

#: Who may record a weigh-in. Trainers are included but are further narrowed to
#: their own private-training clients below — the roles tuple cannot express
#: "only for some members", so the check is repeated in the handler.
RECORDING_ROLES = (
    UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.REGIONAL_MANAGER,
    UserRole.BRANCH_MANAGER, UserRole.FRONT_DESK, UserRole.TRAINER,
)

#: Who may delete one. A mistyped body-fat percentage otherwise sits on the
#: member's chart forever, but deleting history is not a front-desk power.
DELETION_ROLES = (
    UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.REGIONAL_MANAGER,
    UserRole.BRANCH_MANAGER,
)

#: Sanity bounds. These reject a decimal point in the wrong place, not an
#: unusual member — the point is to catch 1750cm, not to argue with the scale.
_BOUNDS = {
    'weight_kg': (20, 400),
    'height_cm': (80, 260),
    'body_fat_percent': (1, 75),
    'skeletal_muscle_mass_kg': (5, 120),
    'body_water_litres': (5, 100),
    'visceral_fat_level': (1, 60),
    'bone_mineral_kg': (0.5, 10),
    'inbody_score': (1, 100),
}


def _staff_may_read(user, customer):
    """Can this staff member see this member's body composition?

    Branch scope for everyone, and then the extra rule for captains: a trainer
    sees only the members who train privately with them. Body composition is
    health data, and "works at the same branch" is not a reason to hold it.
    """
    accessible = get_accessible_branch_ids(user)
    if accessible is not None and customer.branch_id not in accessible:
        return False
    if user.role == UserRole.TRAINER:
        return trainer_has_client(user.id, customer.id)
    return True


def _load_customer_for_staff(customer_id):
    """Returns (customer, error_response). Same shape for both failures.

    A trainer asking about a member who is not theirs gets 404, not 403: 403
    confirms the member exists at their branch, which is the fact the rule is
    there to withhold.
    """
    user = get_current_user()
    customer = db.session.get(Customer, customer_id)
    if not customer or not _staff_may_read(user, customer):
        return None, error_response('Customer not found', 404)
    return customer, None


def _coerce(field, raw):
    """Parse one measured value, or raise ValueError with a usable message."""
    if raw is None or raw == '':
        return None
    try:
        value = float(raw)
    except (TypeError, ValueError):
        raise ValueError(f'{field} must be a number')

    low, high = _BOUNDS[field]
    if not (low <= value <= high):
        raise ValueError(f'{field} must be between {low} and {high}')

    if field in ('visceral_fat_level', 'inbody_score'):
        return int(round(value))
    return value


# ────────────────────────────── staff ───────────────────────────────────

@measurements_bp.route('/customers/<int:customer_id>/measurements', methods=['POST'])
@jwt_required()
@role_required(*RECORDING_ROLES)
def record_measurement(customer_id):
    """Record a weigh-in.

    Also refreshes the member's current values, so the screens that read
    ``customer.bmi`` keep showing the latest reading rather than drifting
    further out of date with every measurement taken.
    """
    customer, failure = _load_customer_for_staff(customer_id)
    if failure:
        return failure

    data = request.get_json() or {}

    measurement = BodyMeasurement(
        customer_id=customer.id,
        branch_id=customer.branch_id,
        recorded_by=get_current_user().id,
    )

    try:
        for field in BodyMeasurement.MEASURED_FIELDS:
            if field in data:
                setattr(measurement, field, _coerce(field, data[field]))
    except ValueError as e:
        return error_response(str(e), 400)

    # Height rarely changes and the machine may not report it; fall back to
    # what we already hold so BMI can still be derived.
    if measurement.height_cm is None:
        measurement.height_cm = customer.height

    if measurement.weight_kg is None:
        return error_response('weight_kg is required', 400)

    measured_at = data.get('measured_at')
    if measured_at:
        try:
            measurement.measured_at = datetime.fromisoformat(measured_at)
        except ValueError:
            return error_response(
                'measured_at must be an ISO 8601 timestamp', 400)
        if measurement.measured_at > datetime.utcnow():
            return error_response('measured_at cannot be in the future', 400)

    notes = (data.get('notes') or '').strip()
    measurement.notes = notes or None

    measurement.recompute(
        age_years=customer.age,
        gender_value=customer.gender.value if customer.gender else None,
    )

    db.session.add(measurement)

    # Keep the customer row as the latest reading. Guarded on the date so that
    # back-filling an older measurement cannot overwrite today's numbers with
    # last year's.
    latest = customer.measurements.order_by(
        BodyMeasurement.measured_at.desc()).first()
    if latest is None or measurement.measured_at >= latest.measured_at:
        customer.weight = measurement.weight_kg
        customer.height = measurement.height_cm
        customer.bmi = measurement.bmi
        customer.bmi_category = measurement.bmi_category
        customer.bmr = measurement.bmr
        customer.ideal_weight = measurement.ideal_weight
        customer.daily_calories = measurement.daily_calories

    db.session.commit()

    return success_response(measurement.to_dict(), 'Measurement recorded', 201)


@measurements_bp.route('/customers/<int:customer_id>/measurements', methods=['GET'])
@jwt_required()
def list_measurements(customer_id):
    """A member's weigh-ins, newest first."""
    customer, failure = _load_customer_for_staff(customer_id)
    if failure:
        return failure

    limit = min(request.args.get('limit', 100, type=int), 500)
    rows = customer.measurements.order_by(
        BodyMeasurement.measured_at.desc()).limit(limit).all()

    return success_response({
        'customer_id': customer.id,
        'customer_name': customer.full_name,
        'items': [row.to_dict() for row in rows],
        'count': len(rows),
    })


@measurements_bp.route('/measurements/<int:measurement_id>', methods=['DELETE'])
@jwt_required()
@role_required(*DELETION_ROLES)
def delete_measurement(measurement_id):
    """Remove a reading that was entered wrongly."""
    measurement = db.session.get(BodyMeasurement, measurement_id)
    if not measurement:
        return error_response('Measurement not found', 404)

    user = get_current_user()
    accessible = get_accessible_branch_ids(user)
    customer = db.session.get(Customer, measurement.customer_id)
    if accessible is not None and (
        customer is None or customer.branch_id not in accessible
    ):
        return error_response('Measurement not found', 404)

    db.session.delete(measurement)
    db.session.commit()
    return success_response(message='Measurement deleted')


# ────────────────────────────── member ──────────────────────────────────

@measurements_bp.route('/client/measurements', methods=['GET'])
@client_token_required
def my_measurements():
    """The member's own history.

    Members could not see any of this before — body composition was captured at
    registration and shown only to staff.
    """
    customer = get_current_client()
    if not customer:
        return error_response('Customer not found', 404)

    limit = min(request.args.get('limit', 100, type=int), 500)
    rows = customer.measurements.order_by(
        BodyMeasurement.measured_at.desc()).limit(limit).all()

    items = [row.to_dict() for row in rows]

    return success_response({
        'items': items,
        'count': len(items),
        'latest': items[0] if items else None,
        # The oldest in the window, so the app can show "since you started"
        # without a second request.
        'earliest': items[-1] if items else None,
    })
