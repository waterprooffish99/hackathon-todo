#!/usr/bin/env python3
"""
Test script to validate API endpoints and verify the fixes for 400 Bad Request and 422/401 errors.
"""

import asyncio
import httpx
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
TEST_EMAIL = "testuser@example.com"
TEST_PASSWORD = "testpassword123"
TEST_NAME = "Test User"

async def test_api():
    """Test the API endpoints to verify fixes"""

    print("Starting API validation test...")

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test 1: Health check
        print("\n1. Testing health endpoint...")
        try:
            response = await client.get(f"{BASE_URL}/health")
            print(f"Health check: {response.status_code} - {response.json()}")
        except Exception as e:
            print(f"Health check failed: {e}")

        # Test 2: Register a test user
        print("\n2. Testing user registration...")
        try:
            register_data = {
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD,
                "name": TEST_NAME
            }
            response = await client.post(f"{BASE_URL}/api/auth/register", json=register_data)
            print(f"Registration: {response.status_code}")
            if response.status_code == 200:
                print("User registered successfully")
            elif response.status_code == 400:
                print("User may already exist (this is OK)")
            else:
                print(f"Unexpected registration response: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Registration failed: {e}")

        # Test 3: Login
        print("\n3. Testing user login...")
        login_data = {
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD
        }
        try:
            response = await client.post(f"{BASE_URL}/api/auth/login", json=login_data)
            print(f"Login status: {response.status_code}")

            if response.status_code == 200:
                auth_response = response.json()
                token = auth_response.get("access_token")
                if token:
                    print("Login successful, got token")

                    # Set up auth headers for subsequent requests
                    headers = {
                        "Authorization": f"Bearer {token}",
                        "Content-Type": "application/json"
                    }

                    # Test 4: Create a test task
                    print("\n4. Testing task creation...")
                    task_data = {
                        "title": "Test Task from API Validation Script",
                        "description": "This is a test task created by the validation script",
                        "priority": "medium",
                        "tags": ["test", "validation"],
                        "ai_interpret": False
                    }
                    try:
                        response = await client.post(f"{BASE_URL}/api/tasks", json=task_data, headers=headers)
                        print(f"Task creation: {response.status_code}")
                        if response.status_code == 200:
                            created_task = response.json()
                            print(f"Task created successfully: {created_task.get('title')}")
                            task_id = created_task.get('task_id')
                        else:
                            print(f"Task creation failed: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Task creation failed: {e}")

                    # Test 5: Get user's tasks
                    print("\n5. Testing task listing...")
                    try:
                        response = await client.get(f"{BASE_URL}/api/tasks", headers=headers)
                        print(f"Task listing: {response.status_code}")
                        if response.status_code == 200:
                            tasks = response.json()
                            print(f"Retrieved {len(tasks)} tasks")
                        else:
                            print(f"Task listing failed: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"Task listing failed: {e}")

                    # Test 6: Test AI chat endpoint
                    print("\n6. Testing AI chat endpoint...")
                    chat_data = {
                        "message": "Hello, can you help me manage my tasks?",
                        "context": {
                            "user_id": auth_response.get("user_id", "unknown") if 'user_id' in auth_response else "unknown"
                        }
                    }
                    try:
                        response = await client.post(f"{BASE_URL}/v1/ai/chat", json=chat_data, headers=headers)
                        print(f"AI chat: {response.status_code}")
                        if response.status_code == 200:
                            chat_response = response.json()
                            print(f"Chat response received: {chat_response.get('response', 'No response text')[:50]}...")
                        else:
                            print(f"AI chat failed: {response.status_code} - {response.text}")
                    except Exception as e:
                        print(f"AI chat failed: {e}")

                else:
                    print("No token received from login")
            else:
                print(f"Login failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Login failed: {e}")

if __name__ == "__main__":
    print("Running API validation tests...")
    asyncio.run(test_api())
    print("\nAPI validation complete.")