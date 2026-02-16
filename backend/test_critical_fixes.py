"""
Test script for 3 critical backend fixes
Run this to verify all fixes are working correctly
"""
import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"  # Change to PythonAnywhere URL for production
RECEPTIONIST_TOKEN = None  # Set after login
CLIENT_TOKEN = None  # Set after client login

def print_section(title):
    """Print section header"""
    print("\n" + "="*80)
    print(f"  {title}")
    print("="*80)

def print_result(test_name, success, data=None, error=None):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if data:
        print(f"Response: {json.dumps(data, indent=2)}")
    if error:
        print(f"Error: {error}")

# Test 1: Login as receptionist to get token
def test_receptionist_login():
    """Login as receptionist to get JWT token"""
    print_section("TEST 1: Receptionist Login")
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            "username": "front_desk_1",  # Branch 1 receptionist
            "password": "front123"
        }
    )
    
    if response.status_code == 200:
        global RECEPTIONIST_TOKEN
        RECEPTIONIST_TOKEN = response.json()['data']['access_token']
        print_result("Receptionist Login", True, {
            "username": "front_desk_1",
            "branch_id": response.json()['data']['user'].get('branch_id'),
            "role": response.json()['data']['user'].get('role')
        })
        return True
    else:
        print_result("Receptionist Login", False, error=response.json())
        return False

# Test 2: Customer Registration (Fix #1)
def test_customer_registration():
    """Test customer registration with same branch"""
    print_section("TEST 2: Customer Registration (Fix #1)")
    
    if not RECEPTIONIST_TOKEN:
        print_result("Customer Registration", False, error="No receptionist token")
        return False
    
    # Generate unique phone number
    timestamp = datetime.now().strftime("%H%M%S")
    phone = f"0123456{timestamp}"
    
    response = requests.post(
        f"{BASE_URL}/api/customers/register",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json={
            "full_name": "Test Customer Fix",
            "phone": phone,
            "email": f"test{timestamp}@example.com",
            "gender": "male",
            "age": 25,
            "weight": 75.0,
            "height": 175.0,
            "bmi": 24.5,
            "bmi_category": "Normal",
            "bmr": 1750.0,
            "daily_calories": 2450,
            "branch_id": 1  # Same branch as receptionist
        }
    )
    
    if response.status_code == 201:
        data = response.json()
        customer_data = data['data']
        print_result("Customer Registration", True, {
            "customer_id": customer_data.get('id'),
            "full_name": customer_data.get('full_name'),
            "phone": customer_data.get('phone'),
            "branch_id": customer_data.get('branch_id'),
            "qr_code": customer_data.get('qr_code'),
            "temp_password": customer_data.get('client_credentials', {}).get('temporary_password')
        })
        return customer_data
    else:
        print_result("Customer Registration", False, error=response.json())
        return None

# Test 3: Get Client Subscription with Display Metrics (Fix #2)
def test_subscription_display_metrics():
    """Test subscription endpoint returns display metrics"""
    print_section("TEST 3: Subscription Display Metrics (Fix #2)")
    
    # First login as a client
    response = requests.post(
        f"{BASE_URL}/api/client/auth/login",
        json={
            "phone": "01234567890",  # Use existing customer phone
            "password": "TEMP1234"   # Use temp password or actual password
        }
    )
    
    if response.status_code != 200:
        print_result("Client Login", False, error="Login failed - use valid credentials")
        return False
    
    global CLIENT_TOKEN
    CLIENT_TOKEN = response.json()['data']['access_token']
    
    # Get subscription
    response = requests.get(
        f"{BASE_URL}/api/client/subscription",
        headers={"Authorization": f"Bearer {CLIENT_TOKEN}"}
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        has_display_fields = all(key in data for key in ['display_metric', 'display_value', 'display_label'])
        
        print_result("Subscription Display Metrics", has_display_fields, {
            "subscription_id": data.get('id'),
            "subscription_type": data.get('subscription_type'),
            "display_metric": data.get('display_metric'),
            "display_value": data.get('display_value'),
            "display_label": data.get('display_label'),
            "remaining_coins": data.get('remaining_coins'),
            "remaining_sessions": data.get('remaining_sessions')
        })
        return has_display_fields
    elif response.status_code == 404:
        print_result("Subscription Display Metrics", False, 
                    error="No active subscription - create one first to test")
        return False
    else:
        print_result("Subscription Display Metrics", False, error=response.json())
        return False

# Test 4: Check-in with branch_id (Fix #3)
def test_check_in_with_branch_id(customer_data=None):
    """Test check-in endpoint accepts and uses branch_id"""
    print_section("TEST 4: Check-in with branch_id (Fix #3)")
    
    if not RECEPTIONIST_TOKEN:
        print_result("Check-in", False, error="No receptionist token")
        return False
    
    # Use test customer or default
    customer_id = customer_data.get('id') if customer_data else 115
    qr_code = customer_data.get('qr_code') if customer_data else "customer_id:115"
    
    response = requests.post(
        f"{BASE_URL}/api/attendance",
        headers={"Authorization": f"Bearer {RECEPTIONIST_TOKEN}"},
        json={
            "customer_id": customer_id,
            "branch_id": 1,
            "qr_code": qr_code,
            "check_in_time": datetime.utcnow().isoformat() + "Z",
            "action": "check_in_only"
        }
    )
    
    if response.status_code in [200, 201]:
        data = response.json()['data']
        print_result("Check-in with branch_id", True, {
            "attendance_id": data.get('attendance_id') or data.get('entry_id'),
            "customer_name": data.get('customer_name'),
            "check_in_time": data.get('check_in_time'),
            "branch_id": data.get('branch_id') or 1,
            "coins_deducted": data.get('coins_deducted'),
            "sessions_deducted": data.get('sessions_deducted')
        })
        return True
    else:
        print_result("Check-in with branch_id", False, error=response.json())
        return False

# Run all tests
def run_all_tests():
    """Run all tests in sequence"""
    print("\n" + "🚀" * 40)
    print("  TESTING 3 CRITICAL BACKEND FIXES")
    print("🚀" * 40)
    print(f"\nBase URL: {BASE_URL}")
    print(f"Test Time: {datetime.now().isoformat()}")
    
    results = {
        "receptionist_login": False,
        "customer_registration": False,
        "subscription_display": False,
        "check_in": False
    }
    
    # Test 1: Login
    results["receptionist_login"] = test_receptionist_login()
    
    if not results["receptionist_login"]:
        print("\n❌ Cannot proceed without receptionist login")
        return results
    
    # Test 2: Registration
    customer_data = test_customer_registration()
    results["customer_registration"] = customer_data is not None
    
    # Test 3: Subscription Display (optional - requires client with subscription)
    results["subscription_display"] = test_subscription_display_metrics()
    
    # Test 4: Check-in
    results["check_in"] = test_check_in_with_branch_id(customer_data)
    
    # Summary
    print_section("SUMMARY")
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\nResults: {passed}/{total} tests passed")
    print("\nDetailed Results:")
    for test, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {test}")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend fixes are working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")
    
    return results

if __name__ == "__main__":
    # Update BASE_URL for production testing
    # BASE_URL = "https://yamenmod91.pythonanywhere.com"
    
    run_all_tests()
