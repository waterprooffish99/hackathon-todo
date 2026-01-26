#!/usr/bin/env python3
"""
Test script to verify the signup endpoint works with the fixed database dependency
"""
import requests
import json
import sys
import subprocess
import time

def test_signup_endpoint():
    """Test the signup endpoint to ensure it works with the fixed database dependency"""

    # Start the server in the background
    print("Starting the FastAPI server...")
    process = subprocess.Popen([
        "python3", "-m", "uvicorn", "src.main:app", "--host", "127.0.0.1", "--port", "8001", "--reload"
    ], cwd="/mnt/c/Users/WaterProof Fish/hackathon-todo/backend")

    # Give the server time to start
    time.sleep(3)

    try:
        # Test the signup endpoint
        test_data = {
            "name": "Test User",
            "email": "test@example.com",
            "password": "securepassword123"
        }

        print("Testing POST /api/auth/signup endpoint...")
        response = requests.post("http://127.0.0.1:8001/api/auth/signup", json=test_data)

        print(f"Response Status Code: {response.status_code}")
        print(f"Response Body: {response.text}")

        # Check if we get a proper response (not a 500 error due to the original _GeneratorContextManager issue)
        if response.status_code == 500:
            print("❌ FAILED: Got a 500 error, which indicates the original issue might not be fully resolved")
            return False
        elif response.status_code in [200, 409]:  # 200 for success, 409 for conflict (email exists)
            print("✅ SUCCESS: Got a proper HTTP response, indicating the dependency injection works!")
            return True
        else:
            print(f"⚠️ UNEXPECTED: Got unexpected status code {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ ERROR: Failed to test the endpoint: {str(e)}")
        return False
    finally:
        # Kill the server process
        process.terminate()
        process.wait()

if __name__ == "__main__":
    print("Testing the signup endpoint fix...")
    success = test_signup_endpoint()
    if success:
        print("\n🎉 The fix is working correctly! The database dependency issue has been resolved.")
    else:
        print("\n❌ The fix may not be working as expected.")
        sys.exit(1)