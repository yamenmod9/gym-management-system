# BACKEND COMPREHENSIVE FIX REQUIREMENTS (FEB 17, 2026)

This document summarizes all backend issues that need to be fixed for the Flutter app to work correctly.

## 1. API Response Issues

### A. Customer List Endpoint (`GET /api/customers`)
- **Missing Field:** `has_active_subscription` (boolean)
  - *Current Behavior:* Frontend has to make extra API calls to check subscription status.
  - *Required Fix:* Include this field for each customer object.
- **Missing Field:** `age` (integer)
  - *Current Behavior:* Returns `date_of_birth` only. Frontend calculates age, but consistent backend calculation is better.

### B. Subscription Model
- **Missing Field:** `display_metric`
  - *Current Behavior:* Client app guesses metric based on type.
  - *Required Fix:* Explicitly return 'coins', 'time', 'sessions', or 'training'.
- **Field Naming Inconsistency:**
  - `remaining_coins` vs `coins`
  - `days_remaining` vs `time_remaining`

## 2. Seed Data Issues
- **Creation Dates:** Seeded customers have old `created_at` dates (e.g. 2023), making "Recent Customers" look old.
  - *Fix:* Use `datetime.now()` for seeded recent customers.
- **BMI Calculation:** Ensure BMI in seed data matches weight/height formulas.

## 3. QR Code & Check-in
- **Validation:** Check-in endpoint rejects valid check-ins sometimes with "branch_id required" even if provided.
- **Subscription Type Handling:** 
  - Coin subscriptions should decrement coins.
  - Time subscriptions should check expiry date.

## 4. Authentication
- **First-time Login:**
  - Ensure `password_changed` flag is correctly set to `false` for new users.
  - Return `temporary_password` only for staff/admin views, never for client self-view (except maybe once).

## 5. Staff App Data
- **Dashboard Stats:**
  - Ensure endpoints return real counts (revenue, active members) instead of 0.

## 6. Deployment
- **CORS:** Ensure CORS is enabled for web access (if applicable).
- **Timezone:** Ensure server timezone matches gym location (e.g. Cairo/Egypt) to avoid "2 hours ago" discrepancies for "Just now" actions.

