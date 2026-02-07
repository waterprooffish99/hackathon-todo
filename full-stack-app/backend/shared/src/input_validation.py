"""
Input validation and sanitization for the Cloud-Native AI Todo Platform.
"""

import re
from typing import Any, Dict, List, Union
from urllib.parse import urlparse
import html
import bleach


class InputSanitizer:
    """
    Sanitizer for input data to prevent XSS, injection attacks, and other security vulnerabilities.
    """

    def __init__(self):
        # Define allowed tags and attributes for rich text
        self.allowed_tags = [
            'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li', 'blockquote',
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
        ]
        self.allowed_attributes = {
            '*': ['style']  # Allow style attribute on all tags
        }

    def sanitize_text(self, text: str, max_length: int = 10000) -> str:
        """
        Sanitize plain text input.

        Args:
            text: Input text to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized text
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string")

        # Strip leading/trailing whitespace
        text = text.strip()

        # Limit length
        if len(text) > max_length:
            text = text[:max_length]

        # Remove null bytes
        text = text.replace('\x00', '')

        # Escape HTML characters
        text = html.escape(text)

        return text

    def sanitize_html(self, html_content: str, max_length: int = 10000) -> str:
        """
        Sanitize HTML content input.

        Args:
            html_content: HTML content to sanitize
            max_length: Maximum allowed length

        Returns:
            Sanitized HTML content
        """
        if not isinstance(html_content, str):
            raise ValueError("Input must be a string")

        # Limit length
        if len(html_content) > max_length:
            html_content = html_content[:max_length]

        # Use bleach to sanitize HTML
        sanitized = bleach.clean(
            html_content,
            tags=self.allowed_tags,
            attributes=self.allowed_attributes,
            strip=True
        )

        return sanitized

    def validate_email(self, email: str) -> bool:
        """
        Validate email format.

        Args:
            email: Email address to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(email, str):
            return False

        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def validate_url(self, url: str) -> bool:
        """
        Validate URL format.

        Args:
            url: URL to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(url, str):
            return False

        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def validate_uuid(self, uuid_str: str) -> bool:
        """
        Validate UUID format.

        Args:
            uuid_str: UUID string to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(uuid_str, str):
            return False

        # UUID regex pattern
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return re.match(uuid_pattern, uuid_str, re.IGNORECASE) is not None

    def sanitize_task_input(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sanitize task input data.

        Args:
            task_data: Task data to sanitize

        Returns:
            Sanitized task data
        """
        sanitized_task = {}

        # Sanitize title (required, max 255 chars)
        title = task_data.get('title', '')
        if not isinstance(title, str) or len(title.strip()) == 0:
            raise ValueError("Title is required and must be a non-empty string")
        sanitized_task['title'] = self.sanitize_text(title, max_length=255)

        # Sanitize description (optional, max 10000 chars)
        description = task_data.get('description', '')
        if description:
            sanitized_task['description'] = self.sanitize_text(description, max_length=10000)
        else:
            sanitized_task['description'] = ''

        # Validate and sanitize priority
        priority = task_data.get('priority', 'medium')
        if priority not in ['low', 'medium', 'high']:
            raise ValueError(f"Invalid priority: {priority}. Must be 'low', 'medium', or 'high'")
        sanitized_task['priority'] = priority

        # Sanitize tags
        tags = task_data.get('tags', [])
        if isinstance(tags, str):
            # If tags are provided as a string, split by comma
            tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
        elif not isinstance(tags, list):
            tags = []

        sanitized_tags = []
        for tag in tags:
            if isinstance(tag, str):
                clean_tag = self.sanitize_text(tag, max_length=50)
                if clean_tag and clean_tag not in sanitized_tags:
                    sanitized_tags.append(clean_tag)

        # Limit to 10 tags
        sanitized_task['tags'] = sanitized_tags[:10]

        # Validate due_at and remind_at dates (these should be validated separately as datetime objects)
        sanitized_task['due_at'] = task_data.get('due_at')
        sanitized_task['remind_at'] = task_data.get('remind_at')

        # Validate recurrence rule
        recurrence_rule = task_data.get('recurrence_rule')
        if recurrence_rule and recurrence_rule not in ['daily', 'weekly', 'monthly']:
            raise ValueError(f"Invalid recurrence rule: {recurrence_rule}")
        sanitized_task['recurrence_rule'] = recurrence_rule

        # Validate completion status
        completed = task_data.get('completed', False)
        if not isinstance(completed, bool):
            raise ValueError("Completed field must be a boolean")
        sanitized_task['completed'] = completed

        return sanitized_task

    def validate_user_input(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate user input data.

        Args:
            user_data: User data to validate

        Returns:
            Validated user data
        """
        validated_user = {}

        # Validate email (required)
        email = user_data.get('email', '')
        if not self.validate_email(email):
            raise ValueError(f"Invalid email format: {email}")
        validated_user['email'] = email.lower().strip()

        # Validate name (optional)
        name = user_data.get('name', '')
        if name:
            if not isinstance(name, str) or len(name) > 100:
                raise ValueError("Name must be a string with maximum 100 characters")
            validated_user['name'] = self.sanitize_text(name, max_length=100)
        else:
            validated_user['name'] = ''

        return validated_user

    def sanitize_search_query(self, query: str) -> str:
        """
        Sanitize search query input.

        Args:
            query: Search query to sanitize

        Returns:
            Sanitized search query
        """
        if not isinstance(query, str):
            raise ValueError("Search query must be a string")

        # Remove dangerous characters and limit length
        query = query.strip()[:500]  # Limit to 500 chars

        # Remove SQL injection patterns
        dangerous_patterns = [
            r'(drop|create|alter|delete|insert)\s+',  # SQL keywords
            r'(\'|";|--|/\*|\*/)',  # Comment markers and quote characters
            r'(union|select|from|where)\s+'  # More SQL keywords
        ]

        for pattern in dangerous_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                raise ValueError("Query contains potentially dangerous characters")

        return query

    def validate_api_parameters(self, params: Dict[str, Any], allowed_params: List[str]) -> Dict[str, Any]:
        """
        Validate API parameters against allowed list.

        Args:
            params: Parameters to validate
            allowed_params: List of allowed parameter names

        Returns:
            Filtered parameters with only allowed keys
        """
        validated_params = {}

        for key, value in params.items():
            if key in allowed_params:
                # Sanitize string values
                if isinstance(value, str):
                    validated_params[key] = self.sanitize_text(value)
                else:
                    validated_params[key] = value
            else:
                # Log potential security issue
                print(f"Warning: Unexpected parameter '{key}' received and filtered out")

        return validated_params

    def sanitize_json_input(self, json_data: Union[Dict, List]) -> Union[Dict, List]:
        """
        Sanitize JSON input data recursively.

        Args:
            json_data: JSON data to sanitize

        Returns:
            Sanitized JSON data
        """
        if isinstance(json_data, dict):
            sanitized = {}
            for key, value in json_data.items():
                # Sanitize keys (limit length and remove dangerous chars)
                clean_key = self.sanitize_text(str(key), max_length=100)

                # Recursively sanitize values
                if isinstance(value, (dict, list)):
                    sanitized[clean_key] = self.sanitize_json_input(value)
                elif isinstance(value, str):
                    sanitized[clean_key] = self.sanitize_text(value)
                else:
                    sanitized[clean_key] = value

            return sanitized
        elif isinstance(json_data, list):
            return [self.sanitize_json_input(item) if isinstance(item, (dict, list)) else
                   self.sanitize_text(item) if isinstance(item, str) else item for item in json_data]
        else:
            return json_data


class SecurityValidator:
    """
    Security validator for additional security checks.
    """

    def __init__(self):
        self.sanitizer = InputSanitizer()

    def check_for_malicious_content(self, text: str) -> Dict[str, bool]:
        """
        Check text for potentially malicious content.

        Args:
            text: Text to check

        Returns:
            Dictionary with security check results
        """
        checks = {
            "contains_javascript": bool(re.search(r'javascript:', text, re.IGNORECASE)),
            "contains_script_tags": bool(re.search(r'<script', text, re.IGNORECASE)),
            "contains_sql_keywords": bool(re.search(r'(drop|create|alter|delete|insert|select|from|where)', text, re.IGNORECASE)),
            "has_unusual_encoding": bool(re.search(r'%[0-9A-Fa-f]{2}', text)),  # URL encoding patterns
            "excessive_punctuation": len(re.findall(r'[!@#$%^&*(),.?":{}|<>]', text)) > 50,
            "potential_xss_vectors": self._check_xss_vectors(text)
        }

        return checks

    def _check_xss_vectors(self, text: str) -> bool:
        """
        Check for common XSS vectors.

        Args:
            text: Text to check

        Returns:
            True if potential XSS vector found, False otherwise
        """
        xss_patterns = [
            r'on\w+\s*=',
            r'<iframe',
            r'<object',
            r'<embed',
            r'data:text/html',
            r'expression\(',
            r'eval\(',
            r'javascript:',
            r'vbscript:',
        ]

        for pattern in xss_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def validate_rate_limiting_bypass_attempt(self, user_input: str) -> bool:
        """
        Check if user input might be attempting to bypass rate limiting.

        Args:
            user_input: User input to check

        Returns:
            True if potential bypass attempt, False otherwise
        """
        # Look for patterns that might indicate attempts to bypass rate limiting
        bypass_patterns = [
            r'(#|\*)\s*\d+\s*times?',  # Comments with numbers
            r'batch|bulk|multiple|many',  # Words suggesting bulk operations
            r';\s*\w+',  # Multiple statements separated by semicolon
        ]

        for pattern in bypass_patterns:
            if re.search(pattern, user_input, re.IGNORECASE):
                return True

        return False


# Global instance
input_sanitizer = InputSanitizer()
security_validator = SecurityValidator()