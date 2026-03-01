"""
Gym routes - Setup and management of gym branding/settings
"""
from flask import Blueprint, request
from flask_jwt_extended import jwt_required
from app.extensions import db
from app.models.gym import Gym
from app.models.user import UserRole
from app.utils import success_response, error_response, get_current_user, role_required

gyms_bp = Blueprint('gyms', __name__, url_prefix='/api/gyms')


@gyms_bp.route('/my-gym', methods=['GET'])
@jwt_required()
def get_my_gym():
    """Return the gym associated with the current owner.
    For non-owner roles, return the gym owned by their branch owner (future).
    """
    user = get_current_user()
    if not user:
        return error_response("User not found", 404)

    gym = None
    if user.role == UserRole.OWNER:
        gym = Gym.query.filter_by(owner_id=user.id).first()
    # For other roles, try to find the gym through the branch owner
    # (not yet implemented — they share the owner's gym)

    if not gym:
        return error_response("No gym found for this user", 404)

    return success_response(gym.to_dict())


@gyms_bp.route('/setup', methods=['PUT'])
@jwt_required()
@role_required(UserRole.OWNER)
def setup_gym():
    """Complete (or update) the gym setup wizard.
    
    Expected JSON body:
    {
        "name": "Body Art Fitness",
        "primary_color": "#3B82F6",
        "secondary_color": "#6366F1",
        "logo_url": "https://...",           (optional)
        "is_setup_complete": true
    }
    """
    user = get_current_user()
    if not user:
        return error_response("User not found", 404)

    gym = Gym.query.filter_by(owner_id=user.id).first()
    if not gym:
        # Auto-create if somehow missing
        gym = Gym(owner_id=user.id)
        db.session.add(gym)

    data = request.json or {}

    if 'name' in data:
        gym.name = data['name']
    if 'primary_color' in data:
        gym.primary_color = data['primary_color']
    if 'secondary_color' in data:
        gym.secondary_color = data['secondary_color']
    if 'logo_url' in data:
        gym.logo_url = data['logo_url']
    if data.get('is_setup_complete') is not None:
        gym.is_setup_complete = bool(data['is_setup_complete'])

    db.session.commit()

    return success_response(gym.to_dict(), "Gym setup saved successfully")


@gyms_bp.route('', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN)
def list_gyms():
    """List all gyms (super admin only)."""
    gyms = Gym.query.all()
    return success_response([g.to_dict() for g in gyms])
