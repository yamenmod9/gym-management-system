"""
Cascade deactivation service.

When a branch or a whole gym is switched off, no one attached to it should keep
access. These helpers flip every dependent staff user and client to inactive in
a single UPDATE each, so a closed branch/gym never leaves live accounts behind.

Deliberately one-directional: reactivating a branch/gym does NOT auto-reactivate
its members, because that would silently revive accounts an admin disabled
individually. Reactivation is done per-account.
"""
from app.extensions import db
from app.models.user import User
from app.models.customer import Customer
from app.models.branch import Branch


def deactivate_branch_members(branch_id):
    """Deactivate every staff user and client of a single branch.

    Returns (staff_deactivated, customers_deactivated). Does not commit —
    the caller owns the transaction so the branch flag and the cascade land
    together.
    """
    staff = User.query.filter_by(branch_id=branch_id, is_active=True).update(
        {'is_active': False}, synchronize_session=False
    )
    customers = Customer.query.filter_by(branch_id=branch_id, is_active=True).update(
        {'is_active': False}, synchronize_session=False
    )
    return staff, customers


def deactivate_gym_members(gym_id):
    """Deactivate an entire gym: its branches and everyone attached to them.

    Covers all three populations the gym owns — its branches, its staff (every
    user carrying this gym_id, owner included), and the clients across those
    branches. Returns a summary dict. Does not commit.
    """
    branch_ids = [b.id for b in Branch.query.filter_by(gym_id=gym_id).all()]

    branches = Branch.query.filter_by(gym_id=gym_id, is_active=True).update(
        {'is_active': False}, synchronize_session=False
    )

    customers = 0
    if branch_ids:
        customers = Customer.query.filter(
            Customer.branch_id.in_(branch_ids),
            Customer.is_active == True,  # noqa: E712 (SQL boolean, not Python)
        ).update({'is_active': False}, synchronize_session=False)

    staff = User.query.filter_by(gym_id=gym_id, is_active=True).update(
        {'is_active': False}, synchronize_session=False
    )

    return {'branches': branches, 'staff': staff, 'customers': customers}
