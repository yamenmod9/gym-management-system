"""The gym's business day.

Timestamps are stored in UTC, which is right. The mistake was *reporting* on
them in UTC: `date.today()` on a server running in UTC, and day boundaries at
UTC midnight. A gym in Cairo (UTC+2, or +3 over summer) trading until 01:00
therefore had its last hours of takings dated to the following day and counted
in a reconciliation that had not happened yet — a till that balanced on the
night looked short in the morning.

Everything here converts between the two: store UTC, ask questions in the
gym's local day.
"""
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

#: Where these gyms are. Overridable per gym via the `timezone` gym setting,
#: so a chain that opens elsewhere does not need a code change.
DEFAULT_TIMEZONE = 'Africa/Cairo'


def gym_timezone(gym_id):
    """The gym's ZoneInfo, falling back to the default.

    Never raises: an unreadable or nonsense setting must not be able to take
    down a daily closing, so a bad value degrades to the default.
    """
    name = DEFAULT_TIMEZONE
    if gym_id is not None:
        try:
            from app.models.gym_setting import GymSetting
            row = GymSetting.query.filter_by(gym_id=gym_id, key='timezone').first()
            if row and row.value:
                name = row.value.strip()
        except Exception:
            name = DEFAULT_TIMEZONE

    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        return ZoneInfo(DEFAULT_TIMEZONE)


def gym_today(gym_id):
    """Today's date as the gym experiences it, not as UTC does."""
    return datetime.now(gym_timezone(gym_id)).date()


def day_bounds_utc(gym_id, day):
    """The UTC half-open interval [start, end) covering one local day.

    Half-open on purpose: `<= 23:59:59` silently drops anything in the final
    second, and with sub-second timestamps that is a real, if rare, miss.
    """
    tz = gym_timezone(gym_id)
    local_start = datetime.combine(day, time.min, tzinfo=tz)
    local_end = local_start + timedelta(days=1)
    return (
        local_start.astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
        local_end.astimezone(ZoneInfo('UTC')).replace(tzinfo=None),
    )


def gym_id_for_branch(branch_id):
    """The gym a branch belongs to, or None."""
    if branch_id is None:
        return None
    from app.models.branch import Branch
    from app.extensions import db
    return db.session.query(Branch.gym_id).filter(Branch.id == branch_id).scalar()
