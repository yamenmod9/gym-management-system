"""
Example API usage for client features
Python examples using requests library
"""
import requests
import json

BASE_URL = "http://localhost:5000/api"
# Or for production: BASE_URL = "https://yamenmod91.pythonanywhere.com/api"


# ============================================
# EXAMPLE 1: Client Authentication Flow
# ============================================

def example_client_login():
    """Example: Client login with OTP"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Client Authentication")
    print("="*60)
    
    # Use customer with active subscription: Samir El-Sayed (has Gym + Swimming Bundle with 30 visits)
    test_phone = "01092097999"
    
    # Step 1: Request activation code
    print(f"\n1. Requesting activation code for {test_phone}...")
    print(f"   URL: {BASE_URL}/client/auth/request-code")
    response = requests.post(
        f"{BASE_URL}/client/auth/request-code",
        json={
            "identifier": test_phone,
            "delivery_method": "sms"
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code != 200:
        print("\n❌ Failed to request code")
        return
    
    # In development mode, code is included in response
    code_from_response = result.get('data', {}).get('code')
    
    if code_from_response:
        print(f"\n✅ Got activation code from API: {code_from_response}")
        use_api_code = input(f"Use this code ({code_from_response})? [Y/n]: ").strip().lower()
        if use_api_code != 'n':
            activation_code = code_from_response
        else:
            activation_code = input("Enter activation code manually: ")
    else:
        print("\n⚠️  CHECK YOUR FLASK SERVER CONSOLE FOR THE 6-DIGIT CODE!")
        print("    Look for: 'Your gym activation code is: XXXXXX'")
        activation_code = input("\nEnter activation code from console: ")
    
    # Step 2: Verify code and get JWT
    
    print("\n2. Verifying activation code...")
    response = requests.post(
        f"{BASE_URL}/client/auth/verify-code",
        json={
            "identifier": test_phone,
            "code": activation_code
        }
    )
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code == 200:
        client_token = result['data']['access_token']
        print(f"\n✅ Login successful! Token: {client_token[:50]}...")
        return client_token
    else:
        print("\n❌ Login failed!")
        return None


# ============================================
# EXAMPLE 2: Get Client Profile
# ============================================

def example_get_profile(client_token):
    """Example: Get client profile"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Get Client Profile")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/client/me",
        headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================
# EXAMPLE 3: Generate QR Code
# ============================================

def example_generate_qr(client_token):
    """Example: Generate QR code for gym entry"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Generate QR Code")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/client/qr",
        headers={
            "Authorization": f"Bearer {client_token}"
        },
        params={
            "expiry_minutes": 5
        }
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code == 200:
        qr_token = result['data']['qr_token']
        print(f"\n✅ QR code generated!")
        print(f"Token: {qr_token[:50]}...")
        print(f"Expires in: {result['data']['expires_in']} seconds")
        return qr_token
    else:
        print("\n❌ QR generation failed!")
        return None


# ============================================
# EXAMPLE 4: Staff Login
# ============================================

def example_staff_login():
    """Example: Staff login (existing endpoint)"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Staff Login")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": "reception1",
            "password": "reception123"
        }
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    print(json.dumps(result, indent=2))
    
    if response.status_code == 200:
        staff_token = result['data']['access_token']
        print(f"\n✅ Staff login successful!")
        return staff_token
    else:
        print("\n❌ Staff login failed!")
        return None


# ============================================
# EXAMPLE 5: Validate QR Code (Staff)
# ============================================

def example_validate_qr(staff_token, qr_token):
    """Example: Staff validates client's QR code"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Validate QR Code (Staff)")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/validation/qr",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        json={
            "qr_token": qr_token,
            "branch_id": 1
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    
    if response.status_code == 200:
        print("\n✅ Entry approved! Gate can open.")
    else:
        print("\n❌ Entry denied!")


# ============================================
# EXAMPLE 6: Validate Barcode (Staff)
# ============================================

def example_validate_barcode(staff_token):
    """Example: Staff validates static barcode"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Validate Barcode (Staff)")
    print("="*60)
    
    barcode = input("Enter customer barcode (e.g., GYM-151): ")
    
    response = requests.post(
        f"{BASE_URL}/validation/barcode",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        json={
            "barcode": barcode,
            "branch_id": 1
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================
# EXAMPLE 7: Get Entry History (Client)
# ============================================

def example_get_history(client_token):
    """Example: Client views entry history"""
    print("\n" + "="*60)
    print("EXAMPLE 7: Get Entry History (Client)")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/client/history",
        headers={
            "Authorization": f"Bearer {client_token}"
        },
        params={
            "page": 1,
            "per_page": 10
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================
# EXAMPLE 8: Get Client Stats
# ============================================

def example_get_stats(client_token):
    """Example: Get client statistics"""
    print("\n" + "="*60)
    print("EXAMPLE 8: Get Client Statistics")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/client/stats",
        headers={
            "Authorization": f"Bearer {client_token}"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================
# EXAMPLE 9: Get Entry Logs (Staff)
# ============================================

def example_get_entry_logs(staff_token):
    """Example: Staff views all entry logs"""
    print("\n" + "="*60)
    print("EXAMPLE 9: Get Entry Logs (Staff)")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/validation/entry-logs",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        params={
            "page": 1,
            "per_page": 20,
            "status": "approved"  # Filter by status
        }
    )
    
    print(f"Status: {response.status_code}")
    result = response.json()
    
    if response.status_code == 200:
        entries = result['data']['entries']
        print(f"\nFound {len(entries)} entries:")
        for entry in entries[:5]:  # Show first 5
            print(f"  - {entry['customer_name']} at {entry['entry_time']} ({entry['entry_type']})")
    else:
        print(json.dumps(result, indent=2))


# ============================================
# EXAMPLE 10: Manual Entry (Staff)
# ============================================

def example_manual_entry(staff_token):
    """Example: Staff processes manual entry"""
    print("\n" + "="*60)
    print("EXAMPLE 10: Manual Entry (Staff)")
    print("="*60)
    
    customer_id = int(input("Enter customer ID: "))
    
    response = requests.post(
        f"{BASE_URL}/validation/manual",
        headers={
            "Authorization": f"Bearer {staff_token}"
        },
        json={
            "customer_id": customer_id,
            "branch_id": 1,
            "notes": "QR scanner not working"
        }
    )
    
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))


# ============================================
# FULL WORKFLOW EXAMPLE
# ============================================

def full_workflow_example():
    """Complete workflow: Client login -> Generate QR -> Staff validates"""
    print("\n" + "="*70)
    print("COMPLETE WORKFLOW: Client Login → QR Generation → Staff Validation")
    print("="*70)
    
    # Step 1: Client logs in
    client_token = example_client_login()
    if not client_token:
        return
    
    # Step 2: Client gets profile
    example_get_profile(client_token)
    
    # Step 3: Client generates QR code
    qr_token = example_generate_qr(client_token)
    if not qr_token:
        return
    
    # Step 4: Staff logs in
    staff_token = example_staff_login()
    if not staff_token:
        return
    
    # Step 5: Staff validates QR code
    input("\nPress Enter when ready to simulate staff scanning QR...")
    example_validate_qr(staff_token, qr_token)
    
    # Step 6: Client views history
    example_get_history(client_token)
    
    # Step 7: Client views stats
    example_get_stats(client_token)
    
    print("\n" + "="*70)
    print("✅ Complete workflow finished!")
    print("="*70)


# ============================================
# MAIN MENU
# ============================================

def main():
    """Interactive menu for testing"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║         Client Features API - Example Usage                  ║
║         Base URL: {}           ║
╚══════════════════════════════════════════════════════════════╝
    """.format(BASE_URL))
    
    client_token = None
    staff_token = None
    qr_token = None
    
    while True:
        print("\n" + "="*60)
        print("MENU")
        print("="*60)
        print("Client Authentication:")
        print("  1. Client Login (Request + Verify Code)")
        print("  2. Get Client Profile")
        print("  3. Generate QR Code")
        print("  4. Get Entry History")
        print("  5. Get Client Stats")
        print("\nStaff Operations:")
        print("  6. Staff Login")
        print("  7. Validate QR Code")
        print("  8. Validate Barcode")
        print("  9. Manual Entry")
        print(" 10. Get Entry Logs")
        print("\nWorkflows:")
        print(" 11. Full Workflow (All Steps)")
        print("\n  0. Exit")
        print("="*60)
        
        choice = input("Enter choice: ")
        
        if choice == '1':
            client_token = example_client_login()
        elif choice == '2':
            if client_token:
                example_get_profile(client_token)
            else:
                print("❌ Please login first (option 1)")
        elif choice == '3':
            if client_token:
                qr_token = example_generate_qr(client_token)
            else:
                print("❌ Please login first (option 1)")
        elif choice == '4':
            if client_token:
                example_get_history(client_token)
            else:
                print("❌ Please login first (option 1)")
        elif choice == '5':
            if client_token:
                example_get_stats(client_token)
            else:
                print("❌ Please login first (option 1)")
        elif choice == '6':
            staff_token = example_staff_login()
        elif choice == '7':
            if staff_token and qr_token:
                example_validate_qr(staff_token, qr_token)
            else:
                print("❌ Need staff token (option 6) and QR token (option 3)")
        elif choice == '8':
            if staff_token:
                example_validate_barcode(staff_token)
            else:
                print("❌ Please staff login first (option 6)")
        elif choice == '9':
            if staff_token:
                example_manual_entry(staff_token)
            else:
                print("❌ Please staff login first (option 6)")
        elif choice == '10':
            if staff_token:
                example_get_entry_logs(staff_token)
            else:
                print("❌ Please staff login first (option 6)")
        elif choice == '11':
            full_workflow_example()
        elif choice == '0':
            print("\nGoodbye!")
            break
        else:
            print("❌ Invalid choice")


if __name__ == '__main__':
    # Check if requests is installed
    try:
        import requests
    except ImportError:
        print("❌ Please install requests: pip install requests")
        exit(1)
    
    main()
