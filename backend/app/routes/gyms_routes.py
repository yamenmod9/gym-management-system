"""
Gym routes - Setup and management of gym branding/settings
"""
import uuid
import requests
from flask import Blueprint, request, current_app
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename
from app.extensions import db
from app.models.gym import Gym
from app.models.user import UserRole
from app.utils import success_response, error_response, get_current_user, role_required

gyms_bp = Blueprint('gyms', __name__, url_prefix='/api/gyms')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
_CONTENT_TYPES = {
    'png': 'image/png', 'jpg': 'image/jpeg', 'jpeg': 'image/jpeg',
    'gif': 'image/gif', 'webp': 'image/webp',
}
# Logos used to be saved to local disk (static/uploads/), which Railway wipes
# on every redeploy — every uploaded logo vanished the next time the service
# rebuilt. Supabase Storage is the actual persistent home for them now.
_STORAGE_BUCKET = 'gym-logos'


def _allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _storage_object_url(path):
    return f"{current_app.config['SUPABASE_URL']}/storage/v1/object/{_STORAGE_BUCKET}/{path}"


def _storage_public_url(path):
    return f"{current_app.config['SUPABASE_URL']}/storage/v1/object/public/{_STORAGE_BUCKET}/{path}"


def _storage_auth_headers():
    # Supabase's newer sb_secret_... key format needs both headers: `apikey`
    # identifies the project/key pair, `Authorization` is what Storage
    # actually authorizes against. Sending only one gets a 400
    # "Invalid Compact JWS" — Storage tries to parse a bare Bearer token as
    # a legacy JWT service-role key and fails on the new format.
    key = current_app.config['SUPABASE_SERVICE_ROLE_KEY']
    return {'Authorization': f'Bearer {key}', 'apikey': key}


def _storage_upload(path, data, content_type):
    """Upload bytes to the public gym-logos bucket. Raises on failure."""
    headers = {**_storage_auth_headers(), 'Content-Type': content_type}
    resp = requests.post(_storage_object_url(path), headers=headers, data=data, timeout=15)
    resp.raise_for_status()


def _storage_delete(path):
    """Best-effort delete — a missing old file isn't worth failing the request over."""
    url = f"{current_app.config['SUPABASE_URL']}/storage/v1/object/{_STORAGE_BUCKET}"
    try:
        requests.delete(url, headers=_storage_auth_headers(), json={'prefixes': [path]}, timeout=10)
    except requests.RequestException:
        pass


@gyms_bp.route('/my-gym', methods=['GET'])
@jwt_required()
def get_my_gym():
    """Return the gym associated with the current owner.
    For non-owner roles, return the gym owned by their branch owner (future).
    """
    user = get_current_user()
    if not user:
        return error_response("Session expired. Please log in again.", 401)

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
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER)
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
        return error_response("Session expired. Please log in again.", 401)

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


@gyms_bp.route('/upload-logo', methods=['POST'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN, UserRole.OWNER)
def upload_logo():
    """Upload a gym logo image.

    Expects a multipart/form-data request with a 'logo' file field.
    Returns the public URL of the uploaded image.
    """
    user = get_current_user()
    if not user:
        return error_response("Session expired. Please log in again.", 401)

    if 'logo' not in request.files:
        return error_response("No file uploaded. Send a 'logo' field.", 400)

    file = request.files['logo']
    if file.filename == '':
        return error_response("Empty filename", 400)

    if not _allowed_file(file.filename):
        return error_response(
            f"File type not allowed. Use: {', '.join(ALLOWED_EXTENSIONS)}", 400
        )

    # Generate a unique filename to avoid collisions
    ext = file.filename.rsplit('.', 1)[1].lower()
    safe_name = secure_filename(f"gym_{user.id}_{uuid.uuid4().hex[:8]}.{ext}")

    try:
        _storage_upload(safe_name, file.read(), _CONTENT_TYPES[ext])
    except requests.RequestException as e:
        current_app.logger.error(f'Logo upload to Supabase Storage failed: {e}')
        return error_response("Logo upload failed. Please try again.", 502)

    logo_url = _storage_public_url(safe_name)

    # Also update the gym record
    gym = Gym.query.filter_by(owner_id=user.id).first()
    if gym:
        # Delete the old logo object if it exists
        prefix = _storage_public_url('')
        if gym.logo_url and gym.logo_url.startswith(prefix):
            _storage_delete(gym.logo_url[len(prefix):])

        gym.logo_url = logo_url
        db.session.commit()

    return success_response({
        'logo_url': logo_url,
        'filename': safe_name,
    }, "Logo uploaded successfully")


@gyms_bp.route('', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN)
def list_gyms():
    """List all gyms with headline stats (super admin only)."""
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.user import User

    gyms = Gym.query.all()
    result = []
    for g in gyms:
        d = g.to_dict()
        branch_ids = [b.id for b in Branch.query.filter_by(gym_id=g.id).all()]
        d['branch_count'] = len(branch_ids)
        if branch_ids:
            d['customer_count'] = Customer.query.filter(Customer.branch_id.in_(branch_ids)).count()
        else:
            d['customer_count'] = 0
        d['staff_count'] = User.query.filter_by(gym_id=g.id).count()
        result.append(d)
    return success_response(result)


@gyms_bp.route('/<int:gym_id>', methods=['PUT', 'PATCH'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN)
def update_gym(gym_id):
    """Update any gym's settings (super admin only)."""
    gym = db.session.get(Gym, gym_id)
    if not gym:
        return error_response("Gym not found", 404)

    data = request.json or {}
    for field in ('name', 'primary_color', 'secondary_color', 'logo_url'):
        if field in data:
            setattr(gym, field, data[field])
    if 'is_active' in data:
        new_active = bool(data['is_active'])
        # Switching a gym off shuts down everything under it: its branches and
        # every staff member and client attached to them.
        if gym.is_active and not new_active:
            from app.services.cascade_service import deactivate_gym_members
            deactivate_gym_members(gym.id)
        gym.is_active = new_active
    if 'is_setup_complete' in data:
        gym.is_setup_complete = bool(data['is_setup_complete'])

    db.session.commit()
    return success_response(gym.to_dict(), "Gym updated successfully")


@gyms_bp.route('/<int:gym_id>/branches', methods=['GET'])
@jwt_required()
@role_required(UserRole.SUPER_ADMIN)
def gym_branches(gym_id):
    """List a gym's branches with stats (super admin drill-down)."""
    from app.models.branch import Branch
    from app.models.customer import Customer
    from app.models.user import User
    from app.models.subscription import SubscriptionStatus

    gym = db.session.get(Gym, gym_id)
    if not gym:
        return error_response("Gym not found", 404)

    branches = Branch.query.filter_by(gym_id=gym_id).all()
    result = []
    for b in branches:
        d = b.to_dict()
        d['customers_count'] = Customer.query.filter_by(branch_id=b.id).count()
        d['staff_count'] = User.query.filter_by(branch_id=b.id).count()
        d['active_subscriptions'] = b.subscriptions.filter_by(
            status=SubscriptionStatus.ACTIVE
        ).count()
        result.append(d)
    return success_response(result)
