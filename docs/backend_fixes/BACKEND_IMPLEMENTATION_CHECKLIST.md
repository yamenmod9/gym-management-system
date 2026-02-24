# Backend Implementation Verification Prompt

Please review and implement the following backend requirements to support the Gym Client App features:

## 1. 🔍 Profile & Subscription API (`/api/client/me` or `/api/client/profile`)
**Requirement:** The profile endpoint must return detailed active subscription data.
**Status:** Partially working, but check field names.

**Expected JSON Structure:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "full_name": "John Doe",
    "qr_code": "GYM-001",
    "is_active": true,
    "subscription_status": "active", // IMPORTANT: Add this explicit field for easier mapping
    "active_subscription": {
      "status": "active",
      "start_date": "2024-01-01",
      "end_date": "2024-12-31",
      "remaining_coins": 20,
      "days_remaining": 300,
      "subscription_type": "coins", // or "standard"
      "allowed_services": ["Gym", "Sauna"],
      "freeze_history": []
    }
  }
}
```

## 2. 📖 Entry History API (`/api/client/entry-history`)
**Requirement:** Endpoint to list past gym visits/entries.
**Status:** ❌ Missing (Returns 404).

**Implementation Guide:**
- **Endpoint:** `GET /api/client/entry-history`
- **Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 101,
      "branch_name": "Dragon Club Main",
      "service_name": "Gym Access",
      "entry_time": "2024-02-14T10:00:00",
      "coins_used": 1
    }
  ]
}
```

## 3. 📷 QR Scan & Entry Logging
**Requirement:** Backend logic to handle QR scans by staff.
**Status:** Verify implementation.

**Logic Needed:**
1. Staff scans user QR.
2. Backend validates subscription (Active? Not expired? Enough coins?).
3. **Action:** Deduct coin (if applicable) AND create an **Entry Log** record.
4. The Entry Log record is what `/api/client/entry-history` should return.

## 4. ⚙️ Settings & Profile Update
- Ensure endpoints exist for updating profile (phone, email) if "Settings" screen allows editing.

## 🧪 Testing Checklist
1. Create a user with an active subscription.
2. Call `/api/client/me` -> Verify `active_subscription` is present and `status` is "active".
3. Simulate an entry (via staff scan or manual database entry).
4. Call `/api/client/entry-history` -> Verify the entry appears.

