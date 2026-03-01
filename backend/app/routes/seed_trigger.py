"""
Temporary seed trigger - creates gyms table and records for existing owners.
Remove after initial setup is complete.
"""
from flask import Blueprint
from app.extensions import db
from app.models.gym import Gym
from app.models.user import User, UserRole

seed_trigger_bp = Blueprint('seed_trigger', __name__)


@seed_trigger_bp.route('/api/admin/run-seed', methods=['POST'])
def run_seed():
    """Create gyms table and add gym records for existing owners."""
    try:
        # Create the gyms table if it doesn't exist
        db.create_all()

        # Find owners without gyms
        owners = User.query.filter_by(role=UserRole.OWNER).all()
        created = 0
        for owner in owners:
            existing = Gym.query.filter_by(owner_id=owner.id).first()
            if not existing:
                gym = Gym(
                    name=f"{owner.full_name}'s Gym",
                    owner_id=owner.id,
                    is_setup_complete=False,
                )
                db.session.add(gym)
                created += 1

        db.session.commit()
        return {
            'success': True,
            'message': f'Created {created} gym records for owners',
            'total_owners': len(owners),
        }
    except Exception as e:
        db.session.rollback()
        return {'success': False, 'error': str(e)}, 500
