#!/usr/bin/env python3
"""
Test script to verify password validation works correctly.
This tests that passwords longer than 72 bytes are properly rejected.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
from backend.src.skills.auth_skill import AuthSkill


def test_password_length_validation():
    """Test that passwords longer than 72 bytes are rejected."""

    # Test with a password that is exactly 72 bytes (should work)
    password_72_bytes = "a" * 72  # 72 ASCII characters = 72 bytes
    print(f"Testing password with {len(password_72_bytes.encode('utf-8'))} bytes (should work)")

    try:
        hash_result = AuthSkill.get_password_hash(password_72_bytes)
        print("✓ Password with 72 bytes was accepted")
    except ValueError as e:
        print(f"✗ Password with 72 bytes was rejected: {e}")

    # Test with a password that is 73 bytes (should fail)
    password_73_bytes = "a" * 73  # 73 ASCII characters = 73 bytes
    print(f"\nTesting password with {len(password_73_bytes.encode('utf-8'))} bytes (should fail)")

    try:
        hash_result = AuthSkill.get_password_hash(password_73_bytes)
        print("✗ Password with 73 bytes was incorrectly accepted")
    except ValueError as e:
        print(f"✓ Password with 73 bytes was correctly rejected: {e}")

    # Test with a password that is much longer (100 bytes) to simulate the original error scenario
    password_long = "a" * 100  # 100 ASCII characters = 100 bytes
    print(f"\nTesting password with {len(password_long.encode('utf-8'))} bytes (should fail)")

    try:
        hash_result = AuthSkill.get_password_hash(password_long)
        print("✗ Long password was incorrectly accepted")
    except ValueError as e:
        print(f"✓ Long password was correctly rejected: {e}")

    # Test with a UTF-8 password that might exceed 72 bytes even if character count is less
    # For example, emoji or accented characters take more than 1 byte each
    utf8_password = "🔑" * 20  # Each emoji is typically 4 bytes, so 20 * 4 = 80 bytes
    print(f"\nTesting UTF-8 password with {len(utf8_password.encode('utf-8'))} bytes (should fail)")

    try:
        hash_result = AuthSkill.get_password_hash(utf8_password)
        print("✗ UTF-8 password was incorrectly accepted")
    except ValueError as e:
        print(f"✓ UTF-8 password was correctly rejected: {e}")


if __name__ == "__main__":
    print("Testing password validation...")
    test_password_length_validation()
    print("\nTest completed!")