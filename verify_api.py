#!/usr/bin/env python3
"""
Verification script for Phase II-V API integration.
This script validates successful task creation and retrieval through API endpoints.
"""

import asyncio
import httpx
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "email": "testuser@example.com",
    "password": "securepassword123",
    "name": "Test User"
}

async def verify_api_integration():
    """Main verification function that performs login, task creation, and task retrieval"""

    print("Starting API integration verification...")

    # Create an HTTP client
    async with httpx.AsyncClient(timeout=30.0) as client:

        # 1. Attempt to register a test user (OK if it already exists)
        print("Step 1: Registering test user...")
        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/signup",
                json=TEST_USER
            )
            if response.status_code in [200, 400]:  # 400 might indicate user already exists
                print("✓ Test user registration completed")
            else:
                print(f"⚠ User registration returned status {response.status_code}, continuing anyway")
        except Exception as e:
            print(f"⚠ Could not register test user: {e}. This might be OK if user exists.")

        # 2. Login to get JWT token
        print("Step 2: Logging in to get JWT token...")
        login_data = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }

        try:
            response = await client.post(
                f"{BASE_URL}/api/auth/login",
                json=login_data
            )

            if response.status_code == 200:
                auth_data = response.json()
                token = auth_data.get("access_token")
                print(f"✓ Successfully logged in, token length: {len(token) if token else 0}")
            else:
                print(f"✗ Login failed with status {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Login failed with exception: {e}")
            return False

        # Set up authentication headers
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        # 3. Create a test task
        print("Step 3: Creating a test task...")
        task_data = {
            "title": "Test Task - API Integration Verification",
            "description": "This is a test task created to verify API integration",
            "priority": "medium",
            "tags": ["test", "verification"],
            "ai_interpret": False
        }

        try:
            # Try both paths to see which one works
            response = await client.post(
                f"{BASE_URL}/api/tasks/",
                json=task_data,
                headers=headers
            )

            if response.status_code == 200:
                created_task = response.json()
                print(f"✓ Task created successfully: {created_task.get('title', 'Unknown')}")
                task_id = created_task.get('task_id')
            elif response.status_code == 307:
                # Retry with non-slash version
                response = await client.post(
                    f"{BASE_URL}/api/tasks",
                    json=task_data,
                    headers=headers
                )
                if response.status_code == 200:
                    created_task = response.json()
                    print(f"✓ Task created successfully: {created_task.get('title', 'Unknown')}")
                    task_id = created_task.get('task_id')
                else:
                    print(f"✗ Task creation failed with status {response.status_code}: {response.text}")
                    return False
            else:
                print(f"✗ Task creation failed with status {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Task creation failed with exception: {e}")
            return False

        # 4. Retrieve the task list
        print("Step 4: Retrieving task list...")
        try:
            response = await client.get(
                f"{BASE_URL}/api/tasks",
                headers=headers
            )

            if response.status_code == 200:
                tasks = response.json()
                print(f"✓ Retrieved {len(tasks)} tasks from server")

                # Find our test task
                test_task_found = False
                for task in tasks:
                    if task.get('title') == task_data['title']:
                        test_task_found = True
                        print(f"✓ Found our test task in the retrieved list: {task.get('title')}")
                        break

                if not test_task_found:
                    print("✗ Our test task was not found in the retrieved list")
                    return False
            else:
                print(f"✗ Task retrieval failed with status {response.status_code}: {response.text}")
                return False

        except Exception as e:
            print(f"✗ Task retrieval failed with exception: {e}")
            return False

    # If we reached here, all tests passed
    print("\n🎉 ALL TESTS PASSED!")
    print("- User authentication works correctly")
    print("- Task creation API is functional")
    print("- Task retrieval API is functional")
    print("- End-to-end flow completed successfully")
    return True


if __name__ == "__main__":
    print("=" * 60)
    print("API INTEGRATION VERIFICATION SCRIPT")
    print("=" * 60)

    success = asyncio.run(verify_api_integration())

    if success:
        print("=" * 60)
        print("SUCCESS: ALL INTEGRATION TESTS PASSED")
        print("=" * 60)
        print("API integration between frontend and backend is working correctly!")
    else:
        print("=" * 60)
        print("FAILURE: SOME TESTS FAILED")
        print("=" * 60)
        print("API integration has issues that need to be addressed.")