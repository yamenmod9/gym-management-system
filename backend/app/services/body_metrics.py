"""Body composition arithmetic, in one place.

These formulas had one implementation on ``Customer.calculate_health_metrics``
and another in Dart (``HealthHelper``). Adding a third for measurement history
is how you end up with the app showing 1,847 daily calories and the printout
saying 1,851, with no way to tell which is wrong. Everything derived from a
weigh-in is computed here and imported by both callers.

Pure functions on purpose: no model imports, no session, nothing to mock.
"""

#: BMI thresholds, in ascending order of (upper bound, label). The final label
#: has no upper bound.
_BMI_BANDS = ((18.5, 'Underweight'), (25, 'Normal'), (30, 'Overweight'))
_BMI_ABOVE_ALL = 'Obese'

#: Multiplier applied to BMR for a moderately active member. The gym has no
#: activity-level field, so this is the assumption the existing code already
#: made — kept identical rather than quietly improved.
MODERATE_ACTIVITY_FACTOR = 1.55


def bmi(weight_kg, height_cm):
    """Body mass index, or None if either input is missing."""
    if not weight_kg or not height_cm:
        return None
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 2)


def bmi_category(bmi_value):
    if bmi_value is None:
        return None
    for upper, label in _BMI_BANDS:
        if bmi_value < upper:
            return label
    return _BMI_ABOVE_ALL


def ideal_weight(height_cm, gender_value):
    """Devine formula. ``gender_value`` is the string 'male' or 'female'.

    Takes the string rather than the Gender enum so this module stays free of
    model imports — the enum's ``.value`` is what both callers already hold.
    """
    if not height_cm or gender_value not in ('male', 'female'):
        return None
    height_in = height_cm / 2.54
    base = 50 if gender_value == 'male' else 45.5
    return round(base + 2.3 * (height_in - 60), 2)


def bmr(weight_kg, height_cm, age_years, gender_value):
    """Basal metabolic rate, Harris-Benedict."""
    if not weight_kg or not height_cm or age_years is None:
        return None
    if gender_value == 'male':
        value = 88.362 + (13.397 * weight_kg) + (4.799 * height_cm) - (5.677 * age_years)
    elif gender_value == 'female':
        value = 447.593 + (9.247 * weight_kg) + (3.098 * height_cm) - (4.330 * age_years)
    else:
        return None
    return round(value, 2)


def daily_calories(bmr_value, activity_factor=MODERATE_ACTIVITY_FACTOR):
    if bmr_value is None:
        return None
    return round(bmr_value * activity_factor)


def body_fat_mass(weight_kg, body_fat_percent):
    """Kilograms of fat — what a member actually asks about when they ask
    whether the percentage moving means anything."""
    if not weight_kg or body_fat_percent is None:
        return None
    return round(weight_kg * body_fat_percent / 100, 2)


def derive_all(weight_kg, height_cm, age_years, gender_value, body_fat_percent=None):
    """Every derived figure for one weigh-in, as a dict.

    Missing inputs give None for whatever depends on them rather than raising:
    a member with no date of birth still gets a BMI, they just get no BMR.
    """
    bmi_value = bmi(weight_kg, height_cm)
    bmr_value = bmr(weight_kg, height_cm, age_years, gender_value)
    return {
        'bmi': bmi_value,
        'bmi_category': bmi_category(bmi_value),
        'bmr': bmr_value,
        'ideal_weight': ideal_weight(height_cm, gender_value),
        'daily_calories': daily_calories(bmr_value),
        'body_fat_mass_kg': body_fat_mass(weight_kg, body_fat_percent),
    }
