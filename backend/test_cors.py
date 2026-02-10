"""
CORS Test Script
Run this to verify CORS is working on your PythonAnywhere API
"""
import requests
import json

# Configuration
API_BASE_URL = "https://yamenmod91.pythonanywhere.com"
FLUTTER_ORIGIN = "http://localhost:3000"  # Change to your Flutter web app port

def test_cors_health_check():
    """Test 1: Simple health check with CORS headers"""
    print("\n" + "="*60)
    print("TEST 1: Health Check with CORS")
    print("="*60)
    
    url = f"{API_BASE_URL}/api/health"
    headers = {
        "Origin": FLUTTER_ORIGIN,
        "Content-Type": "application/json"
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nResponse Headers:")
    print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"  Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
    print(f"  Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    
    print(f"\nResponse Body:")
    print(f"  {response.json()}")
    
    # Validation
    if response.headers.get('Access-Control-Allow-Origin'):
        print("\n✅ CORS headers present!")
    else:
        print("\n❌ CORS headers missing!")
    
    return response.status_code == 200


def test_cors_preflight():
    """Test 2: OPTIONS preflight request"""
    print("\n" + "="*60)
    print("TEST 2: Preflight OPTIONS Request")
    print("="*60)
    
    url = f"{API_BASE_URL}/api/subscriptions/activate"
    headers = {
        "Origin": FLUTTER_ORIGIN,
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type,Authorization"
    }
    
    response = requests.options(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nPreflight Response Headers:")
    print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"  Access-Control-Allow-Methods: {response.headers.get('Access-Control-Allow-Methods', 'NOT SET')}")
    print(f"  Access-Control-Allow-Headers: {response.headers.get('Access-Control-Allow-Headers', 'NOT SET')}")
    print(f"  Access-Control-Max-Age: {response.headers.get('Access-Control-Max-Age', 'NOT SET')}")
    
    # Validation
    allow_methods = response.headers.get('Access-Control-Allow-Methods', '')
    if 'POST' in allow_methods and 'OPTIONS' in allow_methods:
        print("\n✅ Preflight request successful!")
    else:
        print("\n❌ Preflight request failed!")
    
    return response.status_code == 200


def test_cors_with_auth():
    """Test 3: Request with Authorization header"""
    print("\n" + "="*60)
    print("TEST 3: Request with Authorization Header")
    print("="*60)
    
    url = f"{API_BASE_URL}/api/health"
    headers = {
        "Origin": FLUTTER_ORIGIN,
        "Content-Type": "application/json",
        "Authorization": "Bearer test_token_123"  # Fake token for testing
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nCORS Headers:")
    print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    print(f"  Access-Control-Allow-Credentials: {response.headers.get('Access-Control-Allow-Credentials', 'NOT SET')}")
    
    print(f"\nResponse Body:")
    print(f"  {response.json()}")
    
    # Validation
    if response.headers.get('Access-Control-Allow-Origin'):
        print("\n✅ Authorization header accepted!")
    else:
        print("\n❌ Authorization header blocked!")
    
    return response.status_code == 200


def test_cors_post_request():
    """Test 4: POST request simulation"""
    print("\n" + "="*60)
    print("TEST 4: POST Request Simulation")
    print("="*60)
    
    # Note: This will fail authentication but should pass CORS
    url = f"{API_BASE_URL}/api/auth/login"
    headers = {
        "Origin": FLUTTER_ORIGIN,
        "Content-Type": "application/json"
    }
    data = {
        "username": "test",
        "password": "test"
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    print(f"Status Code: {response.status_code}")
    print(f"\nCORS Headers:")
    print(f"  Access-Control-Allow-Origin: {response.headers.get('Access-Control-Allow-Origin', 'NOT SET')}")
    
    print(f"\nResponse Body:")
    print(f"  {response.json()}")
    
    # Validation (CORS should work even if auth fails)
    if response.headers.get('Access-Control-Allow-Origin'):
        print("\n✅ POST request CORS working (auth failed as expected)!")
    else:
        print("\n❌ POST request CORS not working!")
    
    return response.headers.get('Access-Control-Allow-Origin') is not None


def main():
    """Run all CORS tests"""
    print("\n" + "🧪"*30)
    print("CORS CONFIGURATION TEST SUITE")
    print("🧪"*30)
    print(f"\nTesting API: {API_BASE_URL}")
    print(f"Simulating Origin: {FLUTTER_ORIGIN}")
    
    results = []
    
    try:
        results.append(("Health Check", test_cors_health_check()))
    except Exception as e:
        print(f"\n❌ Error in health check: {str(e)}")
        results.append(("Health Check", False))
    
    try:
        results.append(("Preflight", test_cors_preflight()))
    except Exception as e:
        print(f"\n❌ Error in preflight: {str(e)}")
        results.append(("Preflight", False))
    
    try:
        results.append(("Authorization", test_cors_with_auth()))
    except Exception as e:
        print(f"\n❌ Error in auth test: {str(e)}")
        results.append(("Authorization", False))
    
    try:
        results.append(("POST Request", test_cors_post_request()))
    except Exception as e:
        print(f"\n❌ Error in POST test: {str(e)}")
        results.append(("POST Request", False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! CORS is properly configured!")
    else:
        print("\n⚠️  Some tests failed. Check the guide for troubleshooting.")
        print("📖 See CORS_SETUP_GUIDE.md for help")


if __name__ == "__main__":
    main()
