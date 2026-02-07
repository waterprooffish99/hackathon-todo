"""
Task interpreter agent that processes natural language input to extract task properties.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .chat_parser import chat_parser


class TaskInterpreterAgent:
    """
    AI agent that interprets natural language task descriptions to extract structured task data.
    """

    def __init__(self):
        self.parser = chat_parser

    async def interpret_task(self, text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process natural language input to extract task properties and structure.

        Args:
            text: Natural language task description
            context: Additional context for interpretation

        Returns:
            Dictionary with interpreted task structure
        """
        # Use the chat parser to extract basic information
        task_info = self.parser.extract_task_info_from_natural_language(text)

        # Apply additional context if provided
        if context:
            # Apply user preferences from context
            user_preferences = context.get('user_preferences', {})

            # If priority wasn't detected but user has default preferences
            if not task_info['priority'] and 'default_priority' in user_preferences:
                task_info['priority'] = user_preferences['default_priority']

            # Apply timezone conversion if needed
            if 'timezone' in context:
                # In a real implementation, we would convert dates to user's timezone
                pass

        # Ensure proper format for the response
        result = {
            'title': task_info['title'] or text[:50],  # Use original text as fallback
            'description': task_info['description'],
            'priority': task_info['priority'] or 'medium',  # Default priority
            'tags': task_info['tags'],
            'due_at': task_info['due_at'],
            'remind_at': task_info['remind_at'],
            'recurrence_rule': task_info['recurrence_rule'],
            'confidence': 0.8,  # Default confidence score
            'extracted_entities': self._extract_entities(text)
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

    async def suggest_tags(self, text: str) -> list:
        """
        Suggest relevant tags based on the task description.

        Args:
            text: Task description

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

        return suggested_tags

    async def suggest_priority(self, text: str) -> str:
        """
        Suggest priority level based on the task description.

        Args:
            text: Task description

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


# Global instance
task_interpreter_agent = TaskInterpreterAgent()