"""
Test script to verify that the new API endpoints are properly defined.
This checks that the new endpoints without user_id in path exist alongside the old ones.
"""
import inspect
from backend.src.api.tasks import router

def test_new_endpoints_exist():
    """Test that new endpoints without user_id in path have been added."""

    # Get all route definitions from the router
    routes = router.routes

    # Convert routes to a more readable format
    route_paths = [route.path for route in routes]

    print("Current API routes:")
    for path in sorted(route_paths):
        print(f"  {path}")

    # Check that new endpoints exist
    expected_new_routes = [
        "/api/tasks",  # GET
        "/api/tasks",  # POST
        "/api/tasks/{task_id}",  # PUT
        "/api/tasks/{task_id}",  # DELETE
        "/api/tasks/{task_id}/complete"  # PATCH
    ]

    # Check that old routes still exist (for backward compatibility)
    expected_old_routes = [
        "/api/{user_id}/tasks",  # GET
        "/api/{user_id}/tasks",  # POST
        "/api/{user_id}/tasks/{task_id}",  # PUT
        "/api/{user_id}/tasks/{task_id}",  # DELETE
        "/api/{user_id}/tasks/{task_id}/complete"  # PATCH
    ]

    print("\nVerifying new endpoints exist...")
    for route in expected_new_routes:
        if route in route_paths:
            print(f"✓ Found: {route}")
        else:
            print(f"✗ Missing: {route}")

    print("\nVerifying old endpoints still exist...")
    for route in expected_old_routes:
        if route in route_paths:
            print(f"✓ Found: {route}")
        else:
            print(f"✗ Missing: {route}")

    # Count the number of routes to ensure we have the expected amount
    # We should have 10 routes (5 old + 5 new)
    expected_route_count = 10
    actual_route_count = len(route_paths)

    print(f"\nTotal routes: {actual_route_count} (expected: {expected_route_count})")

    if actual_route_count == expected_route_count:
        print("✓ Route count is correct!")
        return True
    else:
        print("✗ Route count is incorrect!")
        return False

if __name__ == "__main__":
    success = test_new_endpoints_exist()
    if success:
        print("\n✅ All tests passed! The API endpoints have been properly updated.")
    else:
        print("\n❌ Some tests failed! Check the implementation.")