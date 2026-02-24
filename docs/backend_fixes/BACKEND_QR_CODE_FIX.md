# 🔧 BACKEND FIX REQUIRED - QR CODE REGENERATION ENDPOINT

**Date:** February 15, 2026  
**Priority:** HIGH  
**Status:** ⚠️ BACKEND NEEDS IMPLEMENTATION

---

## 🎯 ISSUE SUMMARY

The Flutter staff app has a "Regenerate QR Code" feature for customers, but the backend endpoint **does not exist** (404 error).

### Current Problem
```
❌ POST /api/customers/{customer_id}/regenerate-qr
Response: 404 Not Found
```

### What Was Fixed in Flutter
✅ QR code format now matches scanner expectations: `customer_id:123`  
✅ Frontend UI has regenerate button  
✅ Frontend properly calls the endpoint  
⚠️ **Backend endpoint missing** - needs implementation

---

## 📝 BACKEND ENDPOINT REQUIRED

### Endpoint Details

**Method:** `POST`  
**URL:** `/api/customers/{customer_id}/regenerate-qr`  
**Authentication:** Required (Staff only: Receptionist, Manager, Accountant, Owner)

### Request Format
```http
POST /api/customers/115/regenerate-qr
Content-Type: application/json
Authorization: Bearer <staff_token>

{}
```

*Note: Request body is empty or can contain optional parameters*

### Response Format - SUCCESS (200 OK)
```json
{
  "success": true,
  "message": "QR code regenerated successfully",
  "qr_code": "customer_id:115",
  "data": {
    "customer_id": 115,
    "qr_code": "customer_id:115",
    "generated_at": "2026-02-15T10:30:00Z"
  }
}
```

### Response Format - ERROR (404)
```json
{
  "success": false,
  "error": "Customer not found"
}
```

### Response Format - ERROR (403)
```json
{
  "success": false,
  "error": "Unauthorized - staff access only"
}
```

---

## 🏗️ IMPLEMENTATION GUIDE

### Python/Flask Implementation

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from models import db, Customer, Staff
from decorators import staff_only

customer_bp = Blueprint('customers', __name__)

@customer_bp.route('/api/customers/<int:customer_id>/regenerate-qr', methods=['POST'])
@jwt_required()
@staff_only()
def regenerate_qr_code(customer_id):
    """
    Regenerate QR code for a customer
    Staff only - Receptionist, Manager, Accountant, Owner
    """
    try:
        # Get authenticated staff user
        current_user_id = get_jwt_identity()
        staff = Staff.query.get(current_user_id)
        
        if not staff:
            return jsonify({
                'success': False,
                'error': 'Unauthorized'
            }), 403
        
        # Find customer
        customer = Customer.query.get(customer_id)
        
        if not customer:
            return jsonify({
                'success': False,
                'error': 'Customer not found'
            }), 404
        
        # Generate new QR code
        # Format: customer_id:{id}
        new_qr_code = f"customer_id:{customer_id}"
        
        # Update customer record
        customer.qr_code = new_qr_code
        customer.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Log the action (optional but recommended)
        log_activity(
            staff_id=staff.id,
            action='QR_CODE_REGENERATED',
            customer_id=customer_id,
            details=f"QR code regenerated for customer {customer.full_name}"
        )
        
        return jsonify({
            'success': True,
            'message': 'QR code regenerated successfully',
            'qr_code': new_qr_code,
            'data': {
                'customer_id': customer_id,
                'qr_code': new_qr_code,
                'generated_at': datetime.utcnow().isoformat()
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }), 500
```

### Alternative: Django Implementation

```python
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime
from .models import Customer, Staff
from .permissions import IsStaff

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsStaff])
def regenerate_qr_code(request, customer_id):
    """
    Regenerate QR code for a customer
    """
    try:
        # Get customer
        customer = Customer.objects.get(id=customer_id)
        
        # Generate new QR code
        new_qr_code = f"customer_id:{customer_id}"
        
        # Update customer
        customer.qr_code = new_qr_code
        customer.updated_at = datetime.now()
        customer.save()
        
        return JsonResponse({
            'success': True,
            'message': 'QR code regenerated successfully',
            'qr_code': new_qr_code,
            'data': {
                'customer_id': customer_id,
                'qr_code': new_qr_code,
                'generated_at': datetime.now().isoformat()
            }
        }, status=200)
        
    except Customer.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Customer not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Internal server error: {str(e)}'
        }, status=500)
```

---

## 🔐 SECURITY CONSIDERATIONS

### Access Control
- ✅ Only authenticated staff members can regenerate QR codes
- ✅ Customer users cannot regenerate their own QR codes
- ✅ Branch isolation: Staff can only regenerate QR codes for customers in their branch (optional)

### Implementation
```python
# Optional: Branch-level access control
if staff.branch_id != customer.branch_id:
    return jsonify({
        'success': False,
        'error': 'Cannot regenerate QR code for customer in another branch'
    }), 403
```

### Rate Limiting (Recommended)
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: get_jwt_identity()
)

@customer_bp.route('/api/customers/<int:customer_id>/regenerate-qr', methods=['POST'])
@jwt_required()
@staff_only()
@limiter.limit("10 per minute")  # Prevent abuse
def regenerate_qr_code(customer_id):
    # ... implementation
```

---

## 🧪 TESTING

### Test 1: Successful Regeneration
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/115/regenerate-qr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <staff_token>" \
  -d '{}'
```

**Expected Response:** 200 OK with new QR code

### Test 2: Customer Not Found
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/99999/regenerate-qr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <staff_token>" \
  -d '{}'
```

**Expected Response:** 404 Not Found

### Test 3: Unauthorized Access (Client Token)
```bash
curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/115/regenerate-qr \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <client_token>" \
  -d '{}'
```

**Expected Response:** 403 Forbidden

---

## 📊 DATABASE SCHEMA

### Customer Table Requirements

The `customers` table must have a `qr_code` column:

```sql
-- Check if column exists
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'customers' 
  AND column_name = 'qr_code';

-- Add column if missing
ALTER TABLE customers 
ADD COLUMN qr_code VARCHAR(255) UNIQUE;

-- Create index for faster lookups
CREATE INDEX idx_customers_qr_code ON customers(qr_code);
```

### QR Code Format

**Standard Format:** `customer_id:{id}`  
**Examples:**
- `customer_id:1`
- `customer_id:115`
- `customer_id:999`

**Why this format?**
1. ✅ Matches QR scanner parsing logic
2. ✅ Easy to validate and extract customer ID
3. ✅ Human-readable for debugging
4. ✅ Unique per customer

---

## 🔄 QR CODE SCANNER COMPATIBILITY

The QR scanner expects one of these formats:

1. `customer_id:123` ✅ Preferred
2. `123` ✅ Also works (plain ID)

The scanner code:
```dart
// Parse QR code - expected format: "customer_id:12345" or just "12345"
String customerId = qrCode;
if (qrCode.contains(':')) {
  customerId = qrCode.split(':').last;
}
```

**DO NOT USE:** `GYM-123` or `GYM_CUSTOMER_123` ❌ (old formats, won't work)

---

## 📝 BACKEND CHECKLIST

Before marking this as complete, ensure:

- [ ] Endpoint `/api/customers/{id}/regenerate-qr` is implemented
- [ ] POST method is used
- [ ] Staff authentication is enforced
- [ ] Customer existence is validated (404 if not found)
- [ ] QR code format is `customer_id:{id}`
- [ ] Database `qr_code` column is updated
- [ ] Success response returns new QR code
- [ ] Error handling for all edge cases
- [ ] (Optional) Branch-level access control
- [ ] (Optional) Rate limiting to prevent abuse
- [ ] Tested with Postman/curl
- [ ] Works with Flutter app

---

## 🚀 DEPLOYMENT

After implementing the endpoint:

1. **Deploy to PythonAnywhere**
   ```bash
   git add .
   git commit -m "Add QR code regeneration endpoint"
   git push origin main
   ```

2. **Reload Web App**
   - Go to PythonAnywhere dashboard
   - Click "Reload" on your web app

3. **Test the Endpoint**
   ```bash
   curl -X POST https://yamenmod91.pythonanywhere.com/api/customers/115/regenerate-qr \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_STAFF_TOKEN" \
     -d '{}'
   ```

4. **Verify in Flutter App**
   - Open staff app
   - Go to customer detail
   - Click "Regenerate" button
   - Should see: "QR code regenerated successfully" ✅

---

## 🐛 TROUBLESHOOTING

### Error: 404 Not Found
**Cause:** Endpoint not implemented or URL mismatch  
**Fix:** Verify the route is registered in your Flask/Django app

### Error: 500 Internal Server Error
**Cause:** Database error or missing column  
**Fix:** Check backend logs, verify `qr_code` column exists

### QR Code Not Updating in UI
**Cause:** Frontend caching issue  
**Fix:** Already handled - frontend uses state to update QR code immediately

### Scanner Still Can't Read QR Code
**Cause:** Wrong format generated  
**Fix:** Ensure format is exactly `customer_id:123` (no spaces, lowercase)

---

## 📞 SUPPORT

If you encounter issues:

1. Check backend logs for errors
2. Verify database has `qr_code` column
3. Test endpoint with curl/Postman first
4. Confirm staff token is valid
5. Check Flutter app console logs

---

**Status:** ⏳ **WAITING FOR BACKEND IMPLEMENTATION**  
**Next Step:** Implement the endpoint in the backend, then test with Flutter app

---

*Last Updated: February 15, 2026*  
*Created By: AI Assistant*

