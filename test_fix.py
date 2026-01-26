#!/usr/bin/env python3
"""Test script to verify the fix for the todo app."""

import sys
sys.path.insert(0, './phase1/src')

from main import TodoApp
from io import StringIO
import cmd2

def test_add_command():
    """Test that the add command preserves full title and case."""
    app = TodoApp()

    # Capture output
    old_stdout = sys.stdout
    captured_output = StringIO()
    sys.stdout = captured_output

    try:
        # Test adding a task with multiple words in the title
        app.onecmd("add Buy Milk")

        # Check the output
        output = captured_output.getvalue()
        print(f"Command output: {output}")

        # List tasks to see what was saved
        captured_output = StringIO()
        sys.stdout = captured_output
        app.onecmd("list")
        list_output = captured_output.getvalue()
        print(f"List output: {list_output}")

        # Reset stdout
        sys.stdout = old_stdout

        # Verify that the full title "Buy Milk" was preserved
        if "Buy Milk" in list_output:
            print("✅ SUCCESS: Full title preserved")
        else:
            print("❌ FAILURE: Full title not preserved")

        # Test adding a task with title and description
        captured_output = StringIO()
        sys.stdout = captured_output
        app.onecmd("add Clean Room Make the bed and organize desk")
        output2 = captured_output.getvalue()
        print(f"Second command output: {output2}")

        # List tasks again
        captured_output = StringIO()
        sys.stdout = captured_output
        app.onecmd("list")
        list_output2 = captured_output.getvalue()
        print(f"Updated list output: {list_output2}")

        # Reset stdout
        sys.stdout = old_stdout

        if "Clean Room" in list_output2 and "Make the bed" in list_output2:
            print("✅ SUCCESS: Title and description both preserved")
        else:
            print("❌ FAILURE: Title and/or description not properly handled")

    except Exception as e:
        sys.stdout = old_stdout
        print(f"Error during test: {e}")

if __name__ == "__main__":
    test_add_command()