"""
Chat parser for handling natural language commands related to tasks.
"""

import re
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum


class CommandAction(Enum):
    ADD_TASK = "add_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    UPDATE_TASK = "update_task"
    DELETE_TASK = "delete_task"
    SHOW_TAGS = "show_tags"


class ChatCommandParser:
    """
    Parser for natural language chat commands related to task management.
    """

    def __init__(self):
        # Precompile regex patterns for efficiency
        self.patterns = {
            'add_task': [
                r"add task (?P<title>.+?)(?: with priority (?P<priority>\w+))?(?: and tags? (?P<tags>[^\.]+?))?(?=\.|$)",
                r"create task (?P<title>.+?)(?: with priority (?P<priority>\w+))?(?: and tags? (?P<tags>[^\.]+?))?(?=\.|$)",
                r"make task (?P<title>.+?)(?: with priority (?P<priority>\w+))?(?: and tags? (?P<tags>[^\.]+?))?(?=\.|$)",
            ],
            'show_tagged': [
                r"show tasks tagged (?P<tags>.+)",
                r"show (?P<tags>.+) tasks",
            ],
            'add_tag': [
                r"add tag (?P<tag>\w+) to task (?P<task_id>\d+)",
                r"add tag (?P<tag>\w+) to task #(?P<task_id>\d+)",
            ],
            'set_priority': [
                r"set priority (?P<priority>\w+) for task (?P<task_id>\d+)",
                r"set priority (?P<priority>\w+) for task #(?P<task_id>\d+)",
            ],
            'complete_task': [
                r"complete task (?P<task_id>\d+)",
                r"complete task #(?P<task_id>\d+)",
                r"mark task (?P<task_id>\d+) as complete",
                r"mark task #(?P<task_id>\d+) as complete",
            ],
            'list_tasks': [
                r"show my tasks",
                r"list tasks",
                r"what are my tasks",
            ]
        }

    def parse_command(self, command: str) -> Dict:
        """
        Parse a natural language command and extract relevant information.

        Args:
            command: Natural language command string

        Returns:
            Dictionary with parsed command information
        """
        command_lower = command.lower().strip()

        # Check for each command type
        for action, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, command_lower)
                if match:
                    result = {
                        'action': action,
                        'params': match.groupdict(),
                        'original_command': command
                    }

                    # Process the extracted parameters
                    result = self._process_params(result)

                    return result

        # If no pattern matched, return a generic add_task command
        return {
            'action': 'add_task',
            'params': {'title': command},
            'original_command': command
        }

    def _process_params(self, result: Dict) -> Dict:
        """
        Process and normalize extracted parameters.
        """
        action = result['action']
        params = result['params']

        if action == 'add_task':
            # Normalize priority
            if 'priority' in params and params['priority']:
                params['priority'] = params['priority'].lower()
                if params['priority'] not in ['low', 'medium', 'high']:
                    params['priority'] = 'medium'  # Default priority

            # Process tags
            if 'tags' in params and params['tags']:
                # Extract individual tags from the string
                raw_tags = params['tags']
                # Split by commas or 'and' and clean up
                tag_parts = re.split(r',|\sand\s', raw_tags)
                tags = []
                for tag_part in tag_parts:
                    tag = tag_part.strip().lower()
                    if tag:
                        tags.append(tag)

                params['tags'] = tags if tags else None

        elif action == 'show_tagged':
            # Process tags for search
            if 'tags' in params:
                raw_tags = params['tags']
                tag_parts = re.split(r',|\sand\s', raw_tags)
                tags = []
                for tag_part in tag_parts:
                    tag = tag_part.strip().lower()
                    if tag:
                        tags.append(tag)

                params['tags'] = tags if tags else None

        elif action == 'add_tag':
            if 'tag' in params:
                params['tag'] = params['tag'].strip().lower()

        elif action == 'set_priority':
            if 'priority' in params:
                params['priority'] = params['priority'].lower()
                if params['priority'] not in ['low', 'medium', 'high']:
                    params['priority'] = 'medium'  # Default

        return result

    def extract_task_info_from_natural_language(self, text: str) -> Dict:
        """
        Extract task information from natural language description.

        Args:
            text: Natural language description of a task

        Returns:
            Dictionary with extracted task information
        """
        result = {
            'title': '',
            'description': '',
            'priority': None,
            'tags': [],
            'due_at': None,
            'remind_at': None,
            'recurrence_rule': None
        }

        # Extract title (basic approach - first sentence or clause)
        sentences = re.split(r'[.!?]', text)
        if sentences:
            # Remove leading action words for basic extraction
            first_sentence = sentences[0].strip()

            # Remove common action prefixes
            prefixes = ['add task ', 'create task ', 'make task ', 'do ', 'need to ', 'have to ']
            for prefix in prefixes:
                if first_sentence.lower().startswith(prefix):
                    first_sentence = first_sentence[len(prefix):].strip()
                    break

            result['title'] = first_sentence or text[:50]  # Fallback to first 50 chars

        # Look for priority indicators
        priority_patterns = {
            'high': [r'urgent', r'asap', r'important', r'high priority', r'critical'],
            'medium': [r'medium priority', r'normal'],
            'low': [r'low priority', r'whenever', r'whenever possible']
        }

        text_lower = text.lower()
        for priority, patterns in priority_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    result['priority'] = priority
                    break
            if result['priority']:
                break

        # Look for time-related keywords to determine due dates
        if 'tomorrow' in text_lower:
            result['due_at'] = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        elif 'next week' in text_lower:
            result['due_at'] = (datetime.now() + timedelta(weeks=1)).strftime('%Y-%m-%d')
        elif 'today' in text_lower:
            result['due_at'] = datetime.now().strftime('%Y-%m-%d')

        # Look for common tags in the text
        common_tags = ['work', 'personal', 'shopping', 'health', 'finance', 'project']
        for tag in common_tags:
            if tag in text_lower:
                result['tags'].append(tag)

        # Look for recurrence patterns
        recurrence_patterns = {
            'daily': [r'every day', r'daily', r'each day'],
            'weekly': [r'every week', r'weekly', r'each week'],
            'monthly': [r'every month', r'monthly', r'each month']
        }

        for rule, patterns in recurrence_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    result['recurrence_rule'] = rule
                    break
            if result['recurrence_rule']:
                break

        return result


# Global instance
chat_parser = ChatCommandParser()