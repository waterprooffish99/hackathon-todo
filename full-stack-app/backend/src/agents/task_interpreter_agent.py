"""
Task Interpretation Agent for natural language processing.
"""

from typing import Dict, Any, List
from datetime import datetime
from ..models import Task
from .chat_parser import ChatCommandParser


class TaskInterpretationAgent:
    """
    AI agent for interpreting natural language task descriptions.
    """

    def __init__(self):
        self.parser = ChatCommandParser()

    async def interpret_task_description(self, text: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Interpret a natural language task description and extract structured information.

        Args:
            text: Natural language task description
            user_context: Contextual information about the user

        Returns:
            Dictionary with interpreted task properties
        """
        # Use the chat parser to extract basic information
        task_info = self.parser.extract_task_info_from_natural_language(text)

        # Apply user context if provided
        if user_context:
            # Apply user preferences
            user_preferences = user_context.get('preferences', {})

            # If no priority was detected but user has default preferences
            if not task_info['priority'] and 'default_priority' in user_preferences:
                task_info['priority'] = user_preferences['default_priority']

            # Apply timezone conversion if needed
            if 'timezone' in user_context:
                # In a real implementation, we would convert dates to user's timezone
                pass

        # Ensure proper format for the response
        result = {
            "title": task_info['title'] or text[:50],  # Use original text as fallback
            "description": task_info['description'],
            "priority": task_info['priority'] or 'medium',  # Default priority
            "tags": task_info['tags'],
            "due_at": task_info['due_at'],
            "remind_at": task_info['remind_at'],
            "recurrence_rule": task_info['recurrence_rule'],
            "confidence": 0.8,  # Default confidence score
            "extracted_entities": self._extract_entities(text)
        }

        return result

    def _extract_entities(self, text: str) -> list:
        """
        Extract named entities from the text.

        Args:
            text: Input text

        Returns:
            List of extracted entities
        """
        entities = []

        # Simple entity extraction - in a real implementation, this would use NLP libraries
        # Look for common entities in the text
        import re

        # Extract email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        for email in emails:
            entities.append({
                'entity_type': 'email',
                'value': email,
                'confidence': 0.9
            })

        # Extract phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        phones = re.findall(phone_pattern, text)
        for phone in phones:
            entities.append({
                'entity_type': 'phone',
                'value': phone,
                'confidence': 0.8
            })

        # Extract dates
        date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b'
        dates = re.findall(date_pattern, text)
        for date in dates:
            entities.append({
                'entity_type': 'date',
                'value': date,
                'confidence': 0.7
            })

        return entities

    async def suggest_tags(self, text: str, user_context: Dict[str, Any] = None) -> list:
        """
        Suggest relevant tags based on the task description.

        Args:
            text: Task description
            user_context: Contextual information about the user

        Returns:
            List of suggested tags
        """
        text_lower = text.lower()
        suggested_tags = []

        # Common tag mappings
        tag_keywords = {
            'work': ['meeting', 'report', 'presentation', 'deadline', 'project', 'boss', 'colleague'],
            'personal': ['grocery', 'doctor', 'appointment', 'family', 'friend', 'personal'],
            'shopping': ['buy', 'purchase', 'shop', 'order', 'amazon', 'store'],
            'health': ['exercise', 'medication', 'appointment', 'gym', 'health', 'doctor'],
            'finance': ['bill', 'payment', 'tax', 'expense', 'budget', 'money'],
            'learning': ['study', 'read', 'course', 'tutorial', 'learn', 'education']
        }

        for tag, keywords in tag_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                suggested_tags.append(tag)

        # Apply user-specific tag preferences if available
        if user_context and 'preferences' in user_context:
            user_tag_prefs = user_context['preferences'].get('suggested_tags', {})
            for tag, keywords in user_tag_prefs.items():
                if any(keyword in text_lower for keyword in keywords):
                    if tag not in suggested_tags:
                        suggested_tags.append(tag)

        return suggested_tags

    async def suggest_priority(self, text: str, user_context: Dict[str, Any] = None) -> str:
        """
        Suggest priority level based on the task description.

        Args:
            text: Task description
            user_context: Contextual information about the user

        Returns:
            Suggested priority level ('low', 'medium', 'high')
        """
        text_lower = text.lower()

        # Keywords indicating high priority
        high_priority_keywords = [
            'urgent', 'asap', 'immediately', 'now', 'critical', 'emergency',
            'important', 'deadline', 'today', 'within', 'by today', 'crucial'
        ]

        # Keywords indicating low priority
        low_priority_keywords = [
            'whenever', 'someday', 'eventually', 'maybe', 'possibly',
            'low priority', 'not urgent', 'take your time'
        ]

        # Count high priority indicators
        high_count = sum(1 for keyword in high_priority_keywords if keyword in text_lower)

        # Count low priority indicators
        low_count = sum(1 for keyword in low_priority_keywords if keyword in text_lower)

        if high_count > low_count:
            return 'high'
        elif low_count > high_count:
            return 'low'
        else:
            return 'medium'  # Default priority

    async def extract_due_date(self, text: str, user_context: Dict[str, Any] = None) -> str:
        """
        Extract due date from the task description.

        Args:
            text: Task description
            user_context: Contextual information about the user

        Returns:
            Due date in ISO format or None
        """
        import re
        from datetime import datetime, timedelta

        # Look for common date patterns
        date_patterns = [
            # "tomorrow", "next week", "in 3 days"
            (r'tomorrow', timedelta(days=1)),
            (r'next week', timedelta(weeks=1)),
            (r'in (\d+) days?', lambda m: timedelta(days=int(m.group(1)))),
            (r'next month', timedelta(days=30)),
            # Specific date formats
            (r'(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', lambda m: datetime.strptime(m.group(1), '%m/%d/%Y')),
        ]

        text_lower = text.lower()

        for pattern, date_func in date_patterns:
            match = re.search(pattern, text_lower)
            if match:
                if callable(date_func):
                    if isinstance(date_func(match), timedelta):
                        future_date = datetime.utcnow() + date_func(match)
                        return future_date.isoformat()
                    else:
                        return date_func(match).isoformat()
                else:
                    future_date = datetime.utcnow() + date_func
                    return future_date.isoformat()

        return None


# Global instance
task_interpreter_agent = TaskInterpretationAgent()