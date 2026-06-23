import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, path):
    url = f"{BASE_URL}{path}"
    print(f"Testing {name} ({url})... ", end="")
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            print("PASS")
            return True
        else:
            print(f"FAIL (Status: {response.status_code})")
            return False
    except Exception as e:
        print(f"FAIL (Exception: {e})")
        return False

def main():
    print("--- Formularios MVP Local API Tests ---")
    endpoints = [
        ("Health", "/health"),
        ("Students", "/api/students"),
        ("Settings", "/api/settings"),
        ("Debug Status", "/api/debug/status")
    ]
    
    all_passed = True
    for name, path in endpoints:
        if not test_endpoint(name, path):
            all_passed = False
            
    if all_passed:
        print("\nAll tests passed successfully!")
        sys.exit(0)
    else:
        print("\nSome tests failed. Check backend console.")
        sys.exit(1)

if __name__ == "__main__":
    main()
