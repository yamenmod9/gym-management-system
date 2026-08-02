"""
Per-gym house rules the owner can switch on and off.

Every rule is read through :func:`gym_rule`, which falls back to the default in
:data:`RULES` when the gym has never set it. That keeps existing gyms behaving
exactly as they did before a rule was introduced — adding a rule here is a
no-op until an owner deliberately changes it.
"""
from app.extensions import db

#: key -> (default, english label, arabic label)
#:
#: Defaults are chosen so that switching a rule *on* is the change in behaviour.
RULES = {
    'class_attendance_deducts_coin': (
        False,
        'Class attendance deducts a coin',
        'حضور الحصة يخصم كوين',
    ),
    'ask_feedback_after_class': (
        True,
        'Ask members for feedback after a class',
        'طلب تقييم الأعضاء بعد الحصة',
    ),
    'pt_only_members_may_enter': (
        False,
        'Private-training-only members may enter the gym',
        'أعضاء التدريب الخاص فقط يمكنهم دخول الجيم',
    ),
    'allow_multiple_active_subscriptions': (
        True,
        'Members can hold more than one active subscription',
        'يمكن للعضو الاشتراك في أكثر من اشتراك نشط',
    ),
}


def _as_bool(raw):
    return str(raw).strip().lower() in ('1', 'true', 'yes', 'on')


def default_for(key):
    return RULES[key][0]


def gym_rule(gym_id, key):
    """Whether ``key`` is switched on for this gym.

    Cached per request: the door-scan path reads a rule on every check-in, and
    several endpoints consult more than one while assembling a response. Same
    ``flask.g`` approach as ``_gym_branch_ids`` in app/utils/decorators.py.

    Fails to the documented default rather than raising — an unreadable setting
    should never take down a check-in.
    """
    if key not in RULES:
        raise KeyError(f'Unknown gym rule: {key}')
    default = default_for(key)
    if gym_id is None:
        return default

    from flask import g

    cache = getattr(g, '_gym_rules_cache', None)
    if cache is None:
        cache = {}
        g._gym_rules_cache = cache

    if gym_id not in cache:
        from app.models.gym_setting import GymSetting
        try:
            cache[gym_id] = {
                row.key: row.value
                for row in GymSetting.query.filter_by(gym_id=gym_id).all()
            }
        except Exception:
            cache[gym_id] = {}

    raw = cache[gym_id].get(key)
    return default if raw is None else _as_bool(raw)


def all_rules_for(gym_id):
    """Every rule with its current value, for the owner's settings screen."""
    return {
        key: {
            'value': gym_rule(gym_id, key),
            'default': default,
            'label_en': label_en,
            'label_ar': label_ar,
        }
        for key, (default, label_en, label_ar) in RULES.items()
    }


def set_rules(gym_id, updates):
    """Persist a partial map of rule -> bool. Unknown keys are rejected."""
    from flask import g
    from app.models.gym_setting import GymSetting

    unknown = [k for k in updates if k not in RULES]
    if unknown:
        raise KeyError(f"Unknown gym rule(s): {', '.join(sorted(unknown))}")

    for key, value in updates.items():
        row = GymSetting.query.filter_by(gym_id=gym_id, key=key).first()
        if row is None:
            row = GymSetting(gym_id=gym_id, key=key)
            db.session.add(row)
        row.value = 'true' if bool(value) else 'false'

    db.session.commit()
    # The cache was populated before this write; drop it so the same request
    # reads back what it just saved.
    if hasattr(g, '_gym_rules_cache'):
        g._gym_rules_cache.pop(gym_id, None)
