"""
Test the new customer registration endpoint
"""
import requests
import json

# API base URL
BASE_URL = "http://127.0.0.1:5000/api"

def login(username, password):
    """Login and get JWT token"""
    response = requests.post(f"{BASE_URL}/auth/login", json={
        "username": username,
        "password": password
    })
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
        return None

def register_customer(token, customer_data):
    """Register a new customer"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.post(f"{BASE_URL}/customers/register", 
                           json=customer_data, 
                           headers=headers)
    return response

# Test flow
print("=" * 60)
print("Testing Customer Registration Endpoint")
print("=" * 60)

# Step 1: Login as reception user
print("\n1. Logging in as reception1...")
token = login("reception1", "reception123")
if not token:
    print("❌ Login failed, cannot proceed")
    exit(1)
print("✅ Login successful")

# Step 2: Register a new customer
print("\n2. Registering new customer...")
customer_data = {
    "full_name": "Ahmed Test Customer",
    "phone": "01234567890",
    "email": "ahmed.test@example.com",
    "national_id": "30012251234567",
    "age": 24,  # Will be converted to date_of_birth
    "gender": "male",
    "address": "123 Test Street, Cairo",
    "height": 175.0,
    "weight": 78.5,
    "health_notes": "No health issues",
    "branch_id": 1  # Main Branch
}

print(f"Request data:\n{json.dumps(customer_data, indent=2)}")

response = register_customer(token, customer_data)

print(f"\n3. Response Status: {response.status_code}")

if response.status_code == 201:
    data = response.json()
    print("\n✅ Customer registered successfully!")
    print("\nResponse data:")
    print(json.dumps(data, indent=2))
    
    # Verify required fields
    print("\n4. Verifying required fields:")
    required_fields = ['id', 'qr_code', 'full_name', 'phone', 'age', 'bmi', 'bmi_category', 'bmr']
    for field in required_fields:
        if field in data:
            print(f"  ✅ {field}: {data[field]}")
        else:
            print(f"  ❌ Missing field: {field}")
    
    # Verify QR code format
    if data.get('qr_code', '').startswith('GYM-'):
        print(f"\n✅ QR code format is correct: {data['qr_code']}")
    else:
        print(f"\n❌ QR code format is incorrect: {data.get('qr_code')}")
else:
    print(f"\n❌ Registration failed!")
    print(f"Error: {response.text}")

print("\n" + "=" * 60)
