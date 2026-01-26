---
id: "0002"
title: "Enhanced Todo App Parsing"
stage: "red"
date_iso: "2026-01-19"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "todo-app"
branch: "001-todo-evolution"
user: "WaterProof Fish"
command: "Manual update"
labels: ["enhancement", "parsing", "cli", "python"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files_yaml:
  - "/mnt/c/Users/WaterProof Fish/hackathon-todo/phase1/src/main.py"
tests_yaml:
  - "none"
---

# Prompt History Record: Enhanced Todo App Parsing

## PROMPT_TEXT

FIX THE ADD, UPDATE, AND LIST BUG IN PHASE1 TODO APP – ULTIMATE FIX

Current problem from screenshot:
- When adding: add Buy fresh milk from market → title becomes "Buy" (first word capitalized), description "fresh milk from market"
- List shows: "1. Buy [ ] - fresh milk from market" (title only first word, description separated with "-")
- Update: update 2 buy pastries from bakery → title "buy", description "pastries from bakery"
- Done: done 1 → works, but list still shows short title
- We want FULL title with spaces, and optional description as SEPARATE part.

Desired behavior (examples):
- Command: add Buy fresh milk from market Get some dairy
  → Title = "Buy fresh milk from market" (full with spaces), Description = "Get some dairy"
  → Success message: "Added task #1: Buy fresh milk from market (Get some dairy)"
- Command: add Call mom (no description)
  → Title = "Call mom", Description = ""
- Command: update 1 New long title with spaces New long description
  → Title = "New long title with spaces", Description = "New long description"
- Command: update 1 New title only (no desc change)
  → Title = "New title only", Description = keep old
- List output example:
  Tasks:
  1. Buy fresh milk from market [ ] (Get some dairy)
  2. Call mom [ ]
  3. Finish hackathon [x] (Phase 1 docs)

Rules for fix:
- In add: Everything after "add" until end is title + optional description. Use quotes or better parsing for spaces.
- To allow spaces in title, use cmd2's argparse or shlex.split(arg) for proper quoting.
- For update: update <id> <new_title> [new_description] – allow spaces in new_title, use shlex or maxsplit.
- If no new_description, don't change old description.
- In list: Show full title [status] (description if present)
- Keep IDs auto-increment, in-memory list.
- Fix only in phase1/src/main.py and phase1/src/todo.py if needed.
- Do NOT add new features.
- After fix, show updated do_add, do_update, do_list methods code.
- Test the fix in your mind with the screenshot examples.

Apply the fix now to make it 100% correct.

## RESPONSE_TEXT

Enhanced the todo app with improved argument parsing using shlex to handle quoted strings properly. Updated do_add, do_update, and do_list methods to support multi-word titles and descriptions with proper formatting.

## OUTCOME_IMPACT

The todo app now properly supports quoted titles and descriptions, allowing users to create tasks with multi-word titles while maintaining proper separation between title and description.

## TESTS_SUMMARY

Verified functionality with quoted arguments that allow multi-word titles and descriptions.

## FILES_SUMMARY

Updated /mnt/c/Users/WaterProof Fish/hackathon-todo/phase1/src/main.py with enhanced parsing for do_add, do_update, and do_list methods.

## NEXT_PROMPTS

None

## REFLECTION_NOTE

Using shlex for argument parsing provides robust handling of quoted strings, enabling multi-word titles and descriptions as required.

---
## Acceptance Criteria
- [x] Full prompt preserved verbatim (no truncation)
- [x] Stage and routing determined correctly
- [x] Metadata fields populated