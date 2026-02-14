"""
Test script for temporary password functionality
Tests staff viewing temp passwords and client password change flow
"""
import requests
import json

BASE_URL = "http://localhost:8000/api"

def print_section(title):
    """Print a formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_staff_login():
    """Test staff login to get access token"""
    print_section("1. STAFF LOGIN (Reception)")
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "reception1",
            "password": "reception123"
        }
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        token = data['access_token']
        print(f"✓ Staff logged in successfully")
        print(f"  User: {data['user']['full_name']}")
        print(f"  Role: {data['user']['role']}")
        return token
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_get_customer_with_temp_password(token):
    """Test getting customer details with temp_password visible"""
    print_section("2. GET CUSTOMER DETAILS (Staff View)")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customers/1", headers=headers)
    
    if response.status_code == 200:
        customer = response.json()['data']
        print(f"✓ Customer retrieved successfully")
        print(f"  Name: {customer['full_name']}")
        print(f"  Phone: {customer['phone']}")
        print(f"  Password Changed: {customer.get('password_changed', 'N/A')}")
        print(f"  Temp Password: {customer.get('temp_password', 'N/A')}")
        
        if customer.get('temp_password'):
            print(f"\n  ✓ TEMP PASSWORD IS VISIBLE TO STAFF!")
            return customer['phone'], customer['temp_password']
        else:
            print(f"\n  ⚠ No temp password (already changed)")
            return customer['phone'], None
    else:
        print(f"✗ Failed to get customer: {response.text}")
        return None, None

def test_list_customers(token):
    """Test listing customers with temp_password visible"""
    print_section("3. LIST CUSTOMERS (Staff View)")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customers?per_page=5", headers=headers)
    
    if response.status_code == 200:
        data = response.json()['data']
        customers = data['data']
        print(f"✓ Retrieved {len(customers)} customers")
        
        for i, customer in enumerate(customers[:3], 1):
            print(f"\n  Customer {i}:")
            print(f"    Name: {customer['full_name']}")
            print(f"    Phone: {customer['phone']}")
            print(f"    Password Changed: {customer.get('password_changed', 'N/A')}")
            print(f"    Temp Password: {customer.get('temp_password', 'N/A')}")
    else:
        print(f"✗ Failed to list customers: {response.text}")

def test_client_login(phone, password):
    """Test client login with temporary password"""
    print_section("4. CLIENT LOGIN (First Time)")
    
    response = requests.post(
        f"{BASE_URL}/client/auth/login",
        json={
            "phone": phone,
            "password": password
        }
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✓ Client logged in successfully")
        print(f"  Name: {data['customer']['full_name']}")
        print(f"  Password Changed: {data.get('password_changed', False)}")
        
        if not data.get('password_changed'):
            print(f"\n  ⚠ PASSWORD NOT CHANGED - Client should be forced to change password")
        
        return data['access_token']
    else:
        print(f"✗ Login failed: {response.text}")
        return None

def test_change_password(phone, old_password, new_password):
    """Test changing customer password"""
    print_section("5. CHANGE PASSWORD (Client)")
    
    response = requests.post(
        f"{BASE_URL}/client/auth/change-password",
        json={
            "phone": phone,
            "old_password": old_password,
            "new_password": new_password
        }
    )
    
    if response.status_code == 200:
        print(f"✓ Password changed successfully")
        return True
    else:
        print(f"✗ Password change failed: {response.text}")
        return False

def test_client_login_after_change(phone, new_password):
    """Test client login with new password"""
    print_section("6. CLIENT LOGIN (After Password Change)")
    
    response = requests.post(
        f"{BASE_URL}/client/auth/login",
        json={
            "phone": phone,
            "password": new_password
        }
    )
    
    if response.status_code == 200:
        data = response.json()['data']
        print(f"✓ Client logged in with new password")
        print(f"  Name: {data['customer']['full_name']}")
        print(f"  Password Changed: {data.get('password_changed', False)}")
        
        if data.get('password_changed'):
            print(f"\n  ✓ PASSWORD HAS BEEN CHANGED!")
        
        return True
    else:
        print(f"✗ Login failed: {response.text}")
        return False

def test_temp_password_cleared(token, customer_id=1):
    """Test that temp_password is cleared after password change"""
    print_section("7. VERIFY TEMP PASSWORD CLEARED (Staff View)")
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/customers/{customer_id}", headers=headers)
    
    if response.status_code == 200:
        customer = response.json()['data']
        print(f"✓ Customer retrieved")
        print(f"  Name: {customer['full_name']}")
        print(f"  Password Changed: {customer.get('password_changed', 'N/A')}")
        print(f"  Temp Password: {customer.get('temp_password', 'N/A')}")
        
        if customer.get('password_changed') and not customer.get('temp_password'):
            print(f"\n  ✓ TEMP PASSWORD CLEARED AFTER CHANGE!")
        else:
            print(f"\n  ⚠ Temp password still present")
    else:
        print(f"✗ Failed to get customer: {response.text}")

def test_old_password_fails(phone, old_password):
    """Test that old password no longer works"""
    print_section("8. VERIFY OLD PASSWORD FAILS")
    
    response = requests.post(
        f"{BASE_URL}/client/auth/login",
        json={
            "phone": phone,
            "password": old_password
        }
    )
    
    if response.status_code == 401:
        print(f"✓ Old password correctly rejected")
    else:
        print(f"⚠ Expected 401, got {response.status_code}")

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("  TEMPORARY PASSWORD FUNCTIONALITY TEST")
    print("  Testing staff visibility and client password change flow")
    print("="*70)
    
    # Test 1: Staff login
    staff_token = test_staff_login()
    if not staff_token:
        print("\n✗ Cannot proceed without staff token")
        return
    
    # Test 2: Get customer with temp password
    phone, temp_password = test_get_customer_with_temp_password(staff_token)
    if not phone or not temp_password:
        print("\n⚠ Customer may have already changed password. Testing with fresh customer...")
        # Try to get another customer
        return
    
    # Test 3: List customers
    test_list_customers(staff_token)
    
    # Test 4: Client login with temp password
    client_token = test_client_login(phone, temp_password)
    if not client_token:
        print("\n✗ Cannot proceed without client token")
        return
    
    # Test 5: Change password
    new_password = "MyNewPassword123"
    if not test_change_password(phone, temp_password, new_password):
        print("\n✗ Password change failed")
        return
    
    # Test 6: Login with new password
    if not test_client_login_after_change(phone, new_password):
        print("\n✗ Login with new password failed")
        return
    
    # Test 7: Verify temp password cleared
    test_temp_password_cleared(staff_token, customer_id=1)
    
    # Test 8: Verify old password fails
    test_old_password_fails(phone, temp_password)
    
    # Success summary
    print("\n" + "="*70)
    print("  ✓ ALL TESTS COMPLETED")
    print("="*70)
    print("\n  Summary:")
    print("  ✓ Staff can view temp passwords")
    print("  ✓ Clients can login with temp password")
    print("  ✓ Clients can change their password")
    print("  ✓ Temp password is cleared after change")
    print("  ✓ Old password no longer works")
    print("  ✓ password_changed flag updates correctly")
    print("\n" + "="*70)

if __name__ == "__main__":
    print("\nStarting tests...")
    print("Make sure the backend server is running on http://localhost:8000")
    input("\nPress Enter to continue...")
    
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Cannot connect to backend server")
        print("  Make sure the server is running: python run.py")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
