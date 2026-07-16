"""
Region-aware pricing config and lookup.

Data-driven by design: adding a new fully-priced region (e.g. Saudi
Arabia in SAR) means adding one entry to REGION_PRICING below — no new
branching logic anywhere else in this file or in the route that serves it.

Only Egypt (EG) is finalized right now — those are real business pricing
decisions, not a currency conversion. Every other mapped country gets its
own currency converted from the EG numbers via a manually-maintained
exchange rate in CURRENCIES (see USD_TO_EGP_RATE and CURRENCIES below —
deliberately NOT a live FX API, since several of these currencies are
volatile and prices shown to a visitor shouldn't drift with the market
between page loads). A country with no entry in COUNTRY_CURRENCY falls
back to DEFAULT_REGION (USD).
"""

# ─── Manually maintained exchange rates ─────────────────────────────────
# Update these by hand periodically (e.g. quarterly, or after a large
# move). They only affect the computed non-EGP regions — they never touch
# the EG numbers, which are fixed business pricing, not a conversion.
USD_TO_EGP_RATE = 50.0  # placeholder as of 2026-07 — verify against a live rate before go-live

TRIAL_DAYS = 14
ANNUAL_DISCOUNT_PERCENT = 15

# Tiers eligible for the free trial (Pro and Enterprise are sales-assisted
# / higher-touch, so no self-serve trial).
TRIAL_ELIGIBLE_TIERS = {'starter', 'growth'}


def _round_to_x9(value):
    """Round to the nearest whole number ending in 9 (…19, 29, 59…) — the
    classic SaaS 'clean psychological price' look, never a cents value.

    Below 10, skip the "ends in 9" treatment and just round to the
    nearest whole unit instead: with a couple of high-value currencies
    (BHD, OMR, KWD — worth roughly $2.60–$3.75 each) the $19/$29/$59
    tiers convert to single-digit amounts, and forcing all of them to
    round to the tens digit would collapse distinct tiers onto the same
    "9" price."""
    if value <= 0:
        return 9
    if value < 10:
        return max(1, round(value))
    return max(9, round((value + 1) / 10) * 10 - 1)


# ─── Fully-specified regions ─────────────────────────────────────────────
# Only put a region here once its pricing is a deliberate business
# decision, not a currency conversion. Everything else is derived below.
REGION_PRICING = {
    'EG': {
        'currency': 'EGP',
        'symbol': 'ج.م',
        'symbol_position': 'after',  # "749 ج.م", not "ج.م 749"
        'is_finalized': True,
        'starter': 749,
        'growth': 1499,
        'pro': 2999,
        'enterprise_per_branch': 750,
    },
}

# ─── Currency definitions ────────────────────────────────────────────────
# rate_per_usd: how many units of that currency equal 1 USD — a manually
# maintained snapshot, not a live rate (see USD_TO_EGP_RATE above for why).
# Snapshot taken 2026-07 — verify against a live rate before go-live,
# especially the ones flagged below as actively managed/volatile.
CURRENCIES = {
    'USD': {'symbol': '$', 'symbol_position': 'before', 'rate_per_usd': 1.0},
    'EUR': {'symbol': '€', 'symbol_position': 'before', 'rate_per_usd': 0.876},
    # GCC — pegged to USD, essentially fixed for years/decades.
    'SAR': {'symbol': 'ر.س', 'symbol_position': 'after', 'rate_per_usd': 3.75},
    'AED': {'symbol': 'د.إ', 'symbol_position': 'after', 'rate_per_usd': 3.6725},
    'QAR': {'symbol': 'ر.ق', 'symbol_position': 'after', 'rate_per_usd': 3.64},
    'BHD': {'symbol': 'د.ب', 'symbol_position': 'after', 'rate_per_usd': 0.376},
    'OMR': {'symbol': 'ر.ع.', 'symbol_position': 'after', 'rate_per_usd': 0.3845},
    'KWD': {'symbol': 'د.ك', 'symbol_position': 'after', 'rate_per_usd': 0.3098},
    # Levant / Iraq.
    'JOD': {'symbol': 'د.أ', 'symbol_position': 'after', 'rate_per_usd': 0.709},
    'IQD': {'symbol': 'د.ع', 'symbol_position': 'after', 'rate_per_usd': 1310.0},
    # LBP and SYP are managed/freshly re-based rates, not free-floating —
    # double-check these are still current before go-live. SYP reflects
    # the Jan-2026 redenomination (100 old SYP = 1 new SYP).
    'LBP': {'symbol': 'ل.ل', 'symbol_position': 'after', 'rate_per_usd': 89500.0},
    'SYP': {'symbol': 'ل.س', 'symbol_position': 'after', 'rate_per_usd': 122.0},
    # YER: Yemen effectively has two markets (government- vs Houthi-
    # controlled areas) with very different rates — this is the
    # government-area rate; treat as a rough estimate.
    'YER': {'symbol': 'ر.ي', 'symbol_position': 'after', 'rate_per_usd': 238.6},
    # Maghreb.
    'MAD': {'symbol': 'د.م.', 'symbol_position': 'after', 'rate_per_usd': 9.33},
    'TND': {'symbol': 'د.ت', 'symbol_position': 'after', 'rate_per_usd': 2.96},
    'DZD': {'symbol': 'د.ج', 'symbol_position': 'after', 'rate_per_usd': 133.2},
    'LYD': {'symbol': 'د.ل', 'symbol_position': 'after', 'rate_per_usd': 6.37},
    # Horn of Africa / Mauritania.
    'SDG': {'symbol': 'ج.س', 'symbol_position': 'after', 'rate_per_usd': 601.5},
    'SOS': {'symbol': 'S', 'symbol_position': 'after', 'rate_per_usd': 571.0},
    'DJF': {'symbol': 'Fdj', 'symbol_position': 'after', 'rate_per_usd': 177.7},
    'KMF': {'symbol': 'CF', 'symbol_position': 'after', 'rate_per_usd': 431.0},
    'MRU': {'symbol': 'أ.م', 'symbol_position': 'after', 'rate_per_usd': 39.9},
}

# Country → currency. Every Arab League member with its own national
# currency, plus the Eurozone for EUR. A country not listed here falls
# back to DEFAULT_REGION (USD). Palestine (PS) is deliberately omitted —
# it has no currency of its own (ILS and JOD both circulate), so any
# single mapping here would be a guess; the USD fallback is the honest
# default.
COUNTRY_CURRENCY = {
    # Arab League.
    'SA': 'SAR', 'AE': 'AED', 'QA': 'QAR', 'BH': 'BHD', 'OM': 'OMR', 'KW': 'KWD',
    'JO': 'JOD', 'IQ': 'IQD', 'LB': 'LBP', 'SY': 'SYP', 'YE': 'YER',
    'MA': 'MAD', 'TN': 'TND', 'DZ': 'DZD', 'LY': 'LYD',
    'SD': 'SDG', 'SO': 'SOS', 'DJ': 'DJF', 'KM': 'KMF', 'MR': 'MRU',
    # Eurozone.
    'AT': 'EUR', 'BE': 'EUR', 'HR': 'EUR', 'CY': 'EUR', 'EE': 'EUR', 'FI': 'EUR',
    'FR': 'EUR', 'DE': 'EUR', 'GR': 'EUR', 'IE': 'EUR', 'IT': 'EUR', 'LV': 'EUR',
    'LT': 'EUR', 'LU': 'EUR', 'MT': 'EUR', 'NL': 'EUR', 'PT': 'EUR', 'SK': 'EUR',
    'SI': 'EUR', 'ES': 'EUR',
}


def _build_region_for_currency(currency_code):
    """Compute this currency's tier prices from the EG numbers via USD,
    rounded to clean sticker prices. Recomputed at import time so editing
    a rate in CURRENCIES takes effect on the next deploy with no other
    code changes."""
    eg = REGION_PRICING['EG']
    cur = CURRENCIES[currency_code]
    rate = cur['rate_per_usd']

    def convert(egp_amount):
        usd_amount = egp_amount / USD_TO_EGP_RATE
        return _round_to_x9(usd_amount * rate)

    return {
        'currency': currency_code,
        'symbol': cur['symbol'],
        'symbol_position': cur['symbol_position'],
        'is_finalized': False,
        'starter': convert(eg['starter']),
        'growth': convert(eg['growth']),
        'pro': convert(eg['pro']),
        'enterprise_per_branch': convert(eg['enterprise_per_branch']),
    }


DEFAULT_REGION = _build_region_for_currency('USD')

# Pre-computed at import time for every mapped currency — cheap (small
# fixed set) and keeps get_region_pricing() a simple dict lookup.
_CONVERTED_REGIONS = {
    code: _build_region_for_currency(code) for code in CURRENCIES if code != 'USD'
}

DISCLAIMER_NON_FINALIZED = (
    'Prices are an estimated conversion — contact us to confirm pricing in your currency'
)


def get_region_pricing(country_code):
    """Look up the pricing region for a country code (or None), always
    returning a usable dict — never raises, never returns None. Unknown
    or missing country codes fall back to DEFAULT_REGION (USD)."""
    if country_code:
        code = country_code.upper()
        if code in REGION_PRICING:
            return dict(REGION_PRICING[code])
        currency_code = COUNTRY_CURRENCY.get(code)
        if currency_code:
            return dict(_CONVERTED_REGIONS[currency_code])
    return dict(DEFAULT_REGION)


def build_pricing_response(country_code, resolved_by):
    """Assemble the full /api/pricing payload for a resolved country.

    `resolved_by` is one of 'override' | 'geoip' | 'default' — purely
    informational, so the frontend can show e.g. "Detected: Egypt" vs
    "Showing: Egypt (your choice)" if it wants to.
    """
    region = get_region_pricing(country_code)
    discount_factor = 1 - (ANNUAL_DISCOUNT_PERCENT / 100)

    tiers = {}
    for tier in ('starter', 'growth', 'pro'):
        monthly = region[tier]
        tiers[tier] = {
            'monthly': monthly,
            'annual_monthly_equivalent': round(monthly * discount_factor),
            'annual_total': round(monthly * 12 * discount_factor),
            'trial_eligible': tier in TRIAL_ELIGIBLE_TIERS,
        }

    return {
        'success': True,
        # None only when the visitor is on a public IP we genuinely
        # couldn't resolve (GeoIP unavailable/failed) — currency still
        # correctly falls back to DEFAULT_REGION (USD) via get_region_pricing.
        'country': country_code,
        'resolved_by': resolved_by,
        'currency': region['currency'],
        'symbol': region['symbol'],
        'symbol_position': region['symbol_position'],
        'is_finalized': region['is_finalized'],
        'trial_days': TRIAL_DAYS,
        'annual_discount_percent': ANNUAL_DISCOUNT_PERCENT,
        'tiers': tiers,
        'enterprise': {
            'contact_sales': True,
            'per_branch_from': region['enterprise_per_branch'],
        },
        'disclaimer': None if region['is_finalized'] else DISCLAIMER_NON_FINALIZED,
    }
