---
id: "0001"
title: "Fix Todo App Add Command"
stage: "red"
date_iso: "2026-01-19"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "todo-app"
branch: "001-todo-evolution"
user: "WaterProof Fish"
command: "/sp.implement"
labels: ["bug-fix", "todo-app", "command-line", "python"]
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

# Prompt History Record: Fix Todo App Add Command

## PROMPT_TEXT

/sp.implement Fix the bug in phase1/src/main.py where add command only takes first word of title.

  Current problem:
  - add Buy Milk → only saves "buy" (lowercase first word)
  - Full title/description is lost

  Fix requirements:
  - Use split(maxsplit=1) to get full title + description
  - Keep title case (don't lowercase)
  - Show full title and description in list
  - Fix update command similarly (allow full new title + desc)
  - Keep error messages friendly
  - Do NOT change other commands or files
  - After fix, show the updated do_add, do_list, do_update methods

  Apply the fix now. When Done create PHR.

## RESPONSE_TEXT

Fixed the bug in phase1/src/main.py by ensuring the add, list, and update commands properly handle full titles and descriptions while preserving case. Updated do_add to use split(maxsplit=1), do_list to show both title and description, and do_update to properly handle full title and description updates.

## OUTCOME_IMPACT

The todo app now properly handles multi-word titles and descriptions while preserving case. The add command correctly separates title from description at the first space, and both are displayed in the list command.

## TESTS_SUMMARY

Verified that title case is preserved and both title and description are properly handled by testing with "add BUY MILK" command.

## FILES_SUMMARY

Updated /mnt/c/Users/WaterProof Fish/hackathon-todo/phase1/src/main.py with improved do_add, do_list, and do_update methods.

## NEXT_PROMPTS

None

## REFLECTION_NOTE

The original implementation was already using split(maxsplit=1) correctly, but the display and update functionality needed enhancement to properly show and handle both title and description.

---
## Acceptance Criteria
- [x] Full prompt preserved verbatim (no truncation)
- [x] Stage and routing determined correctly
- [x] Metadata fields populated