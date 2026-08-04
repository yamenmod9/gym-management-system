"""
Utility functions and decorators
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from app.models.user import User, UserRole, BRANCH_GROUP_ROLES
from app.extensions import db


def role_required(*allowed_roles):
    """
    Decorator to check if user has required role
    Usage: @role_required(UserRole.OWNER, UserRole.BRANCH_MANAGER)
           @role_required([UserRole.OWNER, UserRole.BRANCH_MANAGER])  # also supported

    A regional manager inherits every permission a branch manager has (their
    scope — which branches — is enforced separately by the branch filters).
    """
    # Flatten: if caller passed a single list/tuple, unpack it
    if len(allowed_roles) == 1 and isinstance(allowed_roles[0], (list, tuple)):
        allowed_roles = tuple(allowed_roles[0])

    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()

            # A member's token carries a customers.id in the same field a staff
            # token carries a users.id, so without this check int() would
            # happily resolve it against the users table. The request-level
            # guard already rejects client tokens on staff endpoints; this is
            # the second lock, because the cost of the guard ever being bypassed
            # is a member acting as an owner.
            from flask_jwt_extended import get_jwt
            if get_jwt().get('scope') == 'client':
                return jsonify({
                    'success': False,
                    'error': 'Client access is not permitted on this endpoint',
                }), 403

            user_id = int(get_jwt_identity())
            user = db.session.get(User, user_id)

            if not user:
                return jsonify({'success': False, 'error': 'Session expired. Please log in again.'}), 401

            # 401, not 403 — a deactivated account is a dead session, and the
            # clients treat 401 as "log out" but 403 as "wrong permissions".
            if not user.is_active:
                return jsonify({'success': False, 'error': 'User account is inactive'}), 401

            allowed = user.role in allowed_roles
            # Regional roles inherit their tier's branch-level permissions:
            # a regional manager can do anything a branch manager can, a
            # regional accountant anything a branch accountant can. Their
            # scope (which branches) is enforced separately.
            if not allowed and user.role == UserRole.REGIONAL_MANAGER:
                allowed = UserRole.BRANCH_MANAGER in allowed_roles
            if not allowed and user.role == UserRole.REGIONAL_ACCOUNTANT:
                allowed = (UserRole.BRANCH_ACCOUNTANT in allowed_roles
                           or UserRole.ACCOUNTANT in allowed_roles)
            if not allowed:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def branch_access_required(fn):
    """
    Decorator to ensure user has access to the branch they're trying to access
    For branch-specific roles, ensures they can only access their own branch
    Owner and central roles can access all branches
    """
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = int(get_jwt_identity())
        user = db.session.get(User, user_id)
        
        if not user:
            return jsonify({'success': False, 'error': 'Session expired. Please log in again.'}), 401
        
        # Owner, super admin, and central accountant can access all branches
        if user.role in [UserRole.SUPER_ADMIN, UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT]:
            return fn(*args, **kwargs)

        # Branch-group roles can access any branch in their managed group
        if user.role in BRANCH_GROUP_ROLES:
            requested_branch_id = kwargs.get('branch_id')
            if requested_branch_id and requested_branch_id not in user.managed_branch_ids:
                return jsonify({'success': False, 'error': 'Access denied to this branch'}), 403
            return fn(*args, **kwargs)

        # Branch-specific roles must have branch_id
        if not user.branch_id:
            return jsonify({'success': False, 'error': 'User not assigned to any branch'}), 403

        # Check if the requested branch_id matches user's branch
        requested_branch_id = kwargs.get('branch_id')
        if requested_branch_id and requested_branch_id != user.branch_id:
            return jsonify({'success': False, 'error': 'Access denied to this branch'}), 403

        return fn(*args, **kwargs)
    return wrapper


def get_current_user():
    """Get current authenticated user"""
    verify_jwt_in_request()
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)


def get_accessible_branch_ids(user=None):
    """Branch scope for the current user.

    Returns None only for the super admin, who is genuinely unrestricted.
    Everyone else gets an explicit list of branch IDs: every branch in their
    gym for an owner or central accountant, the managed group for a regional
    role, or the single home branch for branch-level roles.

    The owner/central-accountant case used to return None as well, on the
    assumption that "gym scoping still applies elsewhere". It did not: seven
    route modules (customers, complaints, expenses, finance, payments,
    daily closings, and their callers) scope purely by branch and never look
    at gym_id, so None meant no WHERE clause at all and the owner of one gym
    could read every other gym's members, complaints and expenses. Resolving
    the gym to its branch list here fixes all of those call sites at once.
    """
    if user is None:
        user = get_current_user()
    if user.role == UserRole.SUPER_ADMIN:
        return None
    if user.role in BRANCH_GROUP_ROLES:
        return user.managed_branch_ids
    # Gym-wide, but still only their own gym.
    if user.role in (UserRole.OWNER, UserRole.CENTRAL_ACCOUNTANT):
        return _gym_branch_ids(user)
    return [user.branch_id] if user.branch_id else []


def _gym_branch_ids(user):
    """Every branch id belonging to this user's gym.

    Cached per request: gym-wide roles hit this on most queries, and several
    endpoints call it more than once while assembling a response.

    Fails closed — a user whose gym cannot be resolved gets an empty list and
    therefore sees nothing, rather than falling back to "everything".
    """
    from flask import g

    gym_id = get_current_gym_id(user)
    if gym_id is None:
        return []

    cache = getattr(g, '_gym_branch_ids_cache', None)
    if cache is None:
        cache = {}
        g._gym_branch_ids_cache = cache
    if gym_id not in cache:
        from app.models.branch import Branch
        cache[gym_id] = [
            row[0] for row in
            db.session.query(Branch.id).filter(Branch.gym_id == gym_id).all()
        ]
    return cache[gym_id]


def user_can_access_branch(branch, user=None):
    """Whether the user may read/write this specific branch.

    Two gates, both required: the branch must belong to the user's gym, and it
    must fall inside their branch scope. The gym gate is the one that matters —
    without it an owner can address another gym's branch by id, since their own
    branch scope is unrestricted by design.
    """
    if user is None:
        user = get_current_user()
    if user.role == UserRole.SUPER_ADMIN:
        return True

    gym_id = get_current_gym_id(user)
    if gym_id is not None and branch.gym_id != gym_id:
        return False

    ids = get_accessible_branch_ids(user)
    return ids is None or branch.id in ids


def scope_query_to_branches(query, branch_column, user=None, requested_branch_id=None):
    """Apply the user's branch scope to a query.

    Unrestricted users get the requested branch filter (if any); restricted
    users are clamped to their accessible branches, optionally narrowed to a
    single requested branch within that set.
    """
    ids = get_accessible_branch_ids(user)
    if ids is None:
        if requested_branch_id:
            query = query.filter(branch_column == requested_branch_id)
        return query
    if requested_branch_id and requested_branch_id in ids:
        return query.filter(branch_column == requested_branch_id)
    return query.filter(branch_column.in_(ids))


def get_current_gym_id(user=None):
    """Resolve the gym_id for the current user.
    
    - OWNER → gym they own
    - Staff  → their gym_id field (set at creation)
    - SUPER_ADMIN → None (sees everything)
    """
    if user is None:
        user = get_current_user()
    if user.role == UserRole.SUPER_ADMIN:
        return None  # super admin is above gym scope
    if user.role == UserRole.OWNER:
        from app.models.gym import Gym
        gym = Gym.query.filter_by(owner_id=user.id).first()
        return gym.id if gym else None
    return user.gym_id


def paginate(query, page=1, per_page=20):
    """
    Paginate a SQLAlchemy query
    Returns: (items, total, pages, current_page)
    """
    if page < 1:
        page = 1
    if per_page < 1 or per_page > 100:
        per_page = 20
    
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    pages = (total + per_page - 1) // per_page
    
    return items, total, pages, page


def format_pagination_response(items, total, pages, current_page, schema):
    """Format paginated response"""
    return {
        'items': schema.dump(items, many=True),
        'pagination': {
            'total': total,
            'pages': pages,
            'current_page': current_page,
            'per_page': len(items)
        }
    }


def success_response(data=None, message=None, status=200):
    """Standard success response"""
    response = {'success': True}
    if message:
        response['message'] = message
    if data is not None:
        response['data'] = data
    return jsonify(response), status


def error_response(message, status=400, errors=None):
    """Standard error response"""
    response = {'success': False, 'error': message}
    if errors:
        response['errors'] = errors
    return jsonify(response), status
