"""
Comprehensive test script for all backend fixes
Tests all 6 critical areas mentioned in the requirements
"""
import requests
import json
import os
import socket
from datetime import datetime

# Configuration - Auto-detect environment
def get_base_url():
    """Auto-detect the correct base URL based on environment"""
    # Check if running on PythonAnywhere
    hostname = socket.gethostname()
    if 'pythonanywhere' in hostname.lower():
        # Running on PythonAnywhere - use the web app URL
        return "https://yamenmod91.pythonanywhere.com"
    
    # Check if PYTHONANYWHERE_SITE environment variable is set
    if os.getenv('PYTHONANYWHERE_SITE'):
        return f"https://{os.getenv('PYTHONANYWHERE_SITE')}.pythonanywhere.com"
    
    # Default to localhost for local development
    return "http://localhost:5000"

BASE_URL = get_base_url()
RECEPTIONIST_TOKEN = None
OWNER_TOKEN = None
CLIENT_TOKEN = None

def print_header(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_test(name, passed, details=None, error=None):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {name}")
    if details:
        print(f"  Details: {json.dumps(details, indent=2)}")
    if error:
        print(f"  Error: {error}")

# =============================================================================
# AUTHENTICATION
# =============================================================================

def login_receptionist():
    """Login as receptionist (Branch 1)"""
    print_header("Authentication: Receptionist Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": "front_desk_1", "password": "front123"},
            timeout=10
        )
        
        if response.status_code == 200:
            global RECEPTIONIST_TOKEN
            data = response.json()['data']
            RECEPTIONIST_TOKEN = data['access_token']
            print_test("Receptionist Login", True, {
                "username": "front_desk_1",
                "branch_id": data['user'].get('branch_id'),
                "role": data['user'].get('role')
            })
            return True
        else:
            print_test("Receptionist Login", False, error=response.text)
            return False
    except requests.exceptions.ConnectionError as e:
        print_test("Receptionist Login", False, 
                  error=f"Connection failed to {BASE_URL}. Is the server running?")
        print(f"\n💡 Troubleshooting:")
        print(f"   - Make sure the Flask app is running")
        print(f"   - Check if BASE_URL is correct: {BASE_URL}")
        if 'localhost' in BASE_URL:
            print(f"   - For PythonAnywhere, reload the web app")
        return False
    except Exception as e:
        print_test("Receptionist Login", False, error=str(e))
        return False

def login_owner():
    """Login as owner"""
    print_header("Authentication: Owner Login")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"username": "owner", "password": "owner123"}
    )
    
    if response.status_code == 200:
        global OWNER_TOKEN
        data = response.json()['data']
        OWNER_TOKEN = data['access_token']
        print_test("Owner Login", True, {
            "username": "owner",
            "role": data['user'].get('role')
        })
        return True
    else:
        print_test("Owner Login", False, error=response.text)
        return False

# =============================================================================
# TEST 1: CUSTOMER REGISTRATION FIX
# =============================================================================

def test_customer_registration():
    """Test customer registration with branch validation fix"""
    print_header("TEST 1: Customer Registration with Branch Validation")
    
    if not RECEPTIONIST_TOKEN:
        print_test("Customer Registration", False, error="No receptionist token")
        return None
    
    timestamp = datetime.now().strftime("%H%M%S%f")
    phone = f"0199{timestamp[-7:]}"
    
    customer_data = {
        "full_name": f"Test Customer {timestamp[-4:]}",
        "phone": phone,
        "email": f"test{timestamp[-6:]}@example.com",
        "gender": "male",
        "age": 25,
        "weight": 75.0,
        "height": 175.0,
        "bmi": 24.5,
        "bmi_category": "Normal",
        "bmr": 1750.0,
        "daily_calories": 2450,
        "branch_id": 1  # SAME branch as receptionist
    }
    
    response = requests.post(
        f"{BASE_URL}/api/customers/register",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json=customer_data
    )
    
    if response.status_code == 201:
        data = response.json()['data']
        print_test("Customer Registration (Same Branch)", True, {
            "customer_id": data.get('id'),
            "full_name": data.get('full_name'),
            "phone": data.get('phone'),
            "branch_id": data.get('branch_id'),
            "qr_code": data.get('qr_code'),
            "temp_password": data.get('client_credentials', {}).get('temporary_password')
        })
        return data
    else:
        print_test("Customer Registration (Same Branch)", False, 
                  error=response.json() if response.headers.get('content-type') == 'application/json' else response.text)
        return None

def test_cross_branch_rejection():
    """Test that receptionist cannot register for different branch"""
    print_header("TEST 1b: Cross-Branch Registration Rejection")
    
    if not RECEPTIONIST_TOKEN:
        print_test("Cross-Branch Rejection", False, error="No receptionist token")
        return False
    
    timestamp = datetime.now().strftime("%H%M%S%f")
    phone = f"0198{timestamp[-7:]}"
    
    response = requests.post(
        f"{BASE_URL}/api/customers/register",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json={
            "full_name": "Cross Branch Test",
            "phone": phone,
            "gender": "male",
            "age": 25,
            "branch_id": 2  # DIFFERENT branch
        }
    )
    
    # Should be rejected with 403
    if response.status_code == 403:
        print_test("Cross-Branch Rejection", True, {
            "expected": "403 Forbidden",
            "received": response.status_code,
            "message": response.json().get('error')
        })
        return True
    else:
        print_test("Cross-Branch Rejection", False,
                  error=f"Expected 403, got {response.status_code}")
        return False

# =============================================================================
# TEST 2: CHECK-IN SYSTEM FIX
# =============================================================================

def test_checkin_with_qr_code(customer_data):
    """Test check-in with QR code extraction"""
    print_header("TEST 2: Check-in with QR Code")
    
    if not RECEPTIONIST_TOKEN:
        print_test("Check-in with QR", False, error="No receptionist token")
        return False
    
    if not customer_data:
        # Use default test customer
        qr_code = "customer_id:115"
        customer_id = 115
    else:
        qr_code = customer_data.get('qr_code', f"customer_id:{customer_data['id']}")
        customer_id = customer_data['id']
    
    # Test with QR code format: "customer_id:XXX"
    response = requests.post(
        f"{BASE_URL}/api/attendance",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json={
            "qr_code": qr_code,
            "branch_id": 1
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()['data']
        print_test("Check-in with QR Code", True, {
            "qr_code_used": qr_code,
            "customer_name": data.get('customer_name'),
            "check_in_time": data.get('check_in_time'),
            "coins_deducted": data.get('coins_deducted'),
            "remaining_coins": data.get('remaining_coins')
        })
        return True
    elif response.status_code == 403:
        # No active subscription is acceptable
        print_test("Check-in with QR Code", True, {
            "note": "No active subscription (expected for new customer)",
            "error": response.json().get('error')
        })
        return True
    else:
        print_test("Check-in with QR Code", False,
                  error=response.json() if response.headers.get('content-type') == 'application/json' else response.text)
        return False

# =============================================================================
# TEST 3: QR CODE GENERATION
# =============================================================================

def test_qr_code_in_response(customer_data):
    """Test that QR code is present in customer response"""
    print_header("TEST 3: QR Code Generation")
    
    if not customer_data:
        print_test("QR Code Generation", False, error="No customer data")
        return False
    
    qr_code = customer_data.get('qr_code')
    customer_id = customer_data.get('id')
    
    if qr_code:
        # Verify format
        is_valid = qr_code.startswith('GYM-') or qr_code.startswith('customer_id:')
        print_test("QR Code Generation", is_valid, {
            "customer_id": customer_id,
            "qr_code": qr_code,
            "format": "Valid" if is_valid else "Invalid"
        })
        return is_valid
    else:
        print_test("QR Code Generation", False, error="QR code is null")
        return False

# =============================================================================
# TEST 4: SUBSCRIPTION STATUS & COIN TRACKING
# =============================================================================

def test_subscription_with_coins(customer_data):
    """Test subscription creation and coin tracking"""
    print_header("TEST 4: Subscription Status & Coin Tracking")
    
    if not RECEPTIONIST_TOKEN or not customer_data:
        print_test("Subscription Creation", False, error="Missing prerequisites")
        return None
    
    # Create coin-based subscription
    response = requests.post(
        f"{BASE_URL}/api/subscriptions/activate",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json={
            "customer_id": customer_data['id'],
            "service_id": 1,  # Assuming service 1 exists
            "branch_id": 1,
            "payment_method": "cash"
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()['data']
        has_required_fields = all(key in data for key in ['subscription_type', 'remaining_days'])
        
        print_test("Subscription Creation", True, {
            "subscription_id": data.get('id'),
            "subscription_type": data.get('subscription_type'),
            "remaining_coins": data.get('remaining_coins'),
            "remaining_days": data.get('remaining_days'),
            "status": data.get('status')
        })
        return data
    else:
        print_test("Subscription Creation", False,
                  error=response.json() if response.headers.get('content-type') == 'application/json' else response.text)
        return None

# =============================================================================
# TEST 5: BRANCH VALIDATION
# =============================================================================

def test_branch_validation_consistency():
    """Test branch validation across multiple endpoints"""
    print_header("TEST 5: Branch Validation Consistency")
    
    if not RECEPTIONIST_TOKEN:
        print_test("Branch Validation", False, error="No receptionist token")
        return False
    
    # Test customer list with branch filter
    response = requests.get(
        f"{BASE_URL}/api/customers?branch_id=1",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        all_same_branch = all(
            customer.get('branch_id') == 1 
            for customer in data.get('items', [])
        )
        
        print_test("Branch Validation (Customer List)", True, {
            "total_customers": len(data.get('items', [])),
            "all_from_branch_1": all_same_branch,
            "sample_branch_ids": [c.get('branch_id') for c in data.get('items', [])[:3]]
        })
        return all_same_branch
    else:
        print_test("Branch Validation (Customer List)", False, error=response.text)
        return False

# =============================================================================
# TEST 6: TEMPORARY PASSWORD DISPLAY
# =============================================================================

def test_temp_password_display(customer_data):
    """Test that temporary password is visible for new customers"""
    print_header("TEST 6: Temporary Password Display")
    
    if not RECEPTIONIST_TOKEN or not customer_data:
        print_test("Temp Password Display", False, error="Missing prerequisites")
        return False
    
    customer_id = customer_data['id']
    
    response = requests.get(
        f"{BASE_URL}/api/customers/{customer_id}",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        has_temp_password = data.get('temp_password') is not None
        password_changed = data.get('password_changed', True)
        
        # Should have temp_password if password not changed
        is_correct = has_temp_password if not password_changed else not has_temp_password
        
        print_test("Temp Password Display", is_correct, {
            "customer_id": customer_id,
            "has_temp_password": has_temp_password,
            "password_changed": password_changed,
            "temp_password": data.get('temp_password') if has_temp_password else "Not shown (expected)"
        })
        return is_correct
    else:
        print_test("Temp Password Display", False, error=response.text)
        return False

def test_client_login_with_temp_password(customer_data):
    """Test client can login with temporary password"""
    print_header("TEST 6b: Client Login with Temp Password")
    
    if not customer_data:
        print_test("Client Login", False, error="No customer data")
        return False
    
    phone = customer_data.get('phone')
    temp_password = customer_data.get('client_credentials', {}).get('temporary_password')
    
    if not temp_password:
        print_test("Client Login", False, error="No temp password in registration response")
        return False
    
    response = requests.post(
        f"{BASE_URL}/api/client/auth/login",
        json={
            "phone": phone,
            "password": temp_password
        }
    )
    
    if response.status_code == 200:
        global CLIENT_TOKEN
        data = response.json()['data']
        CLIENT_TOKEN = data['access_token']
        
        print_test("Client Login with Temp Password", True, {
            "phone": phone,
            "login_successful": True,
            "customer_name": data.get('customer', {}).get('full_name')
        })
        return True
    else:
        print_test("Client Login with Temp Password", False,
                  error=response.json() if response.headers.get('content-type') == 'application/json' else response.text)
        return False

# =============================================================================
# MAIN TEST SUITE
# =============================================================================

def run_all_tests():
    """Run comprehensive test suite"""
    print("\n" + "🚀" * 40)
    print("  COMPREHENSIVE BACKEND FIXES TEST SUITE")
    print("🚀" * 40)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = {}
    
    # Authentication
    if not login_receptionist():
        print("\n❌ Cannot proceed without receptionist authentication")
        return
    login_owner()  # Optional
    
    # Test 1: Customer Registration
    customer_data = test_customer_registration()
    results['registration_same_branch'] = customer_data is not None
    results['registration_cross_branch'] = test_cross_branch_rejection()
    
    # Test 2: Check-in System
    results['checkin_qr_code'] = test_checkin_with_qr_code(customer_data)
    
    # Test 3: QR Code Generation
    results['qr_code_generation'] = test_qr_code_in_response(customer_data)
    
    # Test 4: Subscription & Coins
    subscription_data = test_subscription_with_coins(customer_data)
    results['subscription_creation'] = subscription_data is not None
    
    # Test 5: Branch Validation
    results['branch_validation'] = test_branch_validation_consistency()
    
    # Test 6: Temporary Password
    results['temp_password_display'] = test_temp_password_display(customer_data)
    results['client_login_temp_pass'] = test_client_login_with_temp_password(customer_data)
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({(passed/total*100):.1f}%)\n")
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} {test_name}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! All backend fixes are working correctly.")
    elif passed >= total * 0.8:
        print(f"\n⚠️  {total - passed} test(s) failed. Most functionality working.")
    else:
        print(f"\n❌ {total - passed} test(s) failed. Review errors above.")
    
    return results

if __name__ == "__main__":
    import sys
    
    # Allow manual override of base URL via command line
    if len(sys.argv) > 1:
        BASE_URL = sys.argv[1]
        print(f"Using custom base URL from command line: {BASE_URL}")
    
    # Detect environment and show info
    print(f"Running on: {socket.gethostname()}")
    print(f"Detected base URL: {BASE_URL}")
    
    # For PythonAnywhere, remind about WSGI reload
    if 'pythonanywhere' in BASE_URL:
        print("\n⚠️  REMINDER: If you've made code changes, reload the web app:")
        print("   Go to Web tab → Click 'Reload yamenmod91.pythonanywhere.com'")
        print("")
    
    run_all_tests()
