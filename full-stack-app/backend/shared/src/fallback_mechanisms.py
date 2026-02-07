"""
Fallback mechanisms for AI subagents when they are unavailable.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable
from .logging_config import get_logger


class AIAgentFallbackManager:
    """
    Manager for handling fallback scenarios when AI subagents are unavailable.
    """

    def __init__(self):
        self.logger = get_logger("ai_fallback_manager")
        self.fallback_strategies = {
            "task_interpreter": self._task_interpreter_fallback,
            "scheduling_intelligence": self._scheduling_intelligence_fallback,
            "reminder_reasoning": self._reminder_reasoning_fallback
        }
        self.health_status = {
            "task_interpreter": True,
            "scheduling_intelligence": True,
            "reminder_reasoning": True
        }

    def register_fallback_strategy(self, agent_name: str, strategy_func: Callable):
        """
        Register a custom fallback strategy for an AI agent.

        Args:
            agent_name: Name of the AI agent
            strategy_func: Function to execute as fallback
        """
        self.fallback_strategies[agent_name] = strategy_func

    def set_agent_health(self, agent_name: str, is_healthy: bool):
        """
        Update the health status of an AI agent.

        Args:
            agent_name: Name of the AI agent
            is_healthy: Whether the agent is healthy/available
        """
        if agent_name in self.health_status:
            self.health_status[agent_name] = is_healthy
            self.logger.info(f"Updated health status for {agent_name}: {'healthy' if is_healthy else 'unhealthy'}")

    def is_agent_available(self, agent_name: str) -> bool:
        """
        Check if an AI agent is available.

        Args:
            agent_name: Name of the AI agent

        Returns:
            True if agent is available, False otherwise
        """
        return self.health_status.get(agent_name, True)

    async def execute_with_fallback(
        self,
        agent_name: str,
        input_data: Dict[str, Any],
        agent_func: Callable,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an AI agent with fallback if unavailable.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent
            agent_func: Function to execute the agent
            *args: Additional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Response from agent or fallback
        """
        if self.is_agent_available(agent_name):
            try:
                # Try to execute the agent
                result = await agent_func(input_data, *args, **kwargs)

                # Add metadata to indicate normal execution
                result["_execution_type"] = "normal"
                result["_agent_used"] = agent_name

                return result
            except Exception as e:
                self.logger.warning(f"Agent {agent_name} failed: {e}. Falling back to fallback strategy.")
                self.set_agent_health(agent_name, False)
        else:
            self.logger.info(f"Agent {agent_name} marked as unavailable, using fallback.")

        # Use fallback strategy
        fallback_result = await self._execute_fallback(agent_name, input_data)

        # Add metadata to indicate fallback execution
        fallback_result["_execution_type"] = "fallback"
        fallback_result["_agent_used"] = "fallback_strategy"
        fallback_result["_fallback_reason"] = f"Original agent {agent_name} was unavailable"

        return fallback_result

    async def _execute_fallback(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the appropriate fallback strategy for the agent.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent

        Returns:
            Fallback response
        """
        if agent_name in self.fallback_strategies:
            try:
                return await self.fallback_strategies[agent_name](input_data)
            except Exception as e:
                self.logger.error(f"Fallback strategy for {agent_name} failed: {e}")
                # Return a default response if fallback also fails
                return self._default_fallback_response(agent_name, input_data)
        else:
            self.logger.warning(f"No fallback strategy registered for {agent_name}")
            return self._default_fallback_response(agent_name, input_data)

    async def _task_interpreter_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback strategy for task interpreter agent.

        Args:
            input_data: Input data containing the task description

        Returns:
            Fallback task interpretation
        """
        text = input_data.get("text", "")

        # Simple heuristic-based interpretation
        fallback_result = {
            "title": text[:50] if text else "Untitled Task",
            "description": text,
            "priority": self._infer_priority_from_text(text),
            "tags": self._extract_basic_tags(text),
            "due_at": None,
            "remind_at": None,
            "recurrence_rule": None,
            "confidence": 0.5,  # Lower confidence for fallback
            "extracted_entities": [],
            "fallback_strategy_used": "heuristic_parsing"
        }

        self.logger.info(f"Task interpreter fallback used for: {text[:30]}...")
        return fallback_result

    async def _scheduling_intelligence_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback strategy for scheduling intelligence agent.

        Args:
            input_data: Input data containing task and user profile

        Returns:
            Fallback scheduling suggestions
        """
        task_description = input_data.get("task_description", "")
        user_profile = input_data.get("user_profile", {})

        # Default scheduling based on simple heuristics
        fallback_result = {
            "suggested_due_date": self._suggest_default_due_date(user_profile),
            "suggested_remind_at": self._suggest_default_reminder_time(user_profile),
            "reasoning": "Default scheduling based on user work hours",
            "conflicts": [],
            "alternative_schedules": [],
            "confidence": 0.6,  # Medium confidence for heuristic scheduling
            "fallback_strategy_used": "heuristic_scheduling"
        }

        self.logger.info("Scheduling intelligence fallback used")
        return fallback_result

    async def _reminder_reasoning_fallback(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fallback strategy for reminder reasoning agent.

        Args:
            input_data: Input data containing task and user profile

        Returns:
            Fallback reminder analysis
        """
        task = input_data.get("task", {})
        user_profile = input_data.get("user_profile", {})

        # Default reminder based on task priority and type
        priority = task.get("priority", "medium")
        due_date = task.get("due_at")

        # Calculate default reminder time based on priority
        default_reminder = self._calculate_default_reminder_time(priority, due_date, user_profile)

        fallback_result = {
            "calculated_reminder_time": default_reminder,
            "base_calculation": default_reminder,
            "adjustments_applied": [],
            "reasoning": f"Default reminder calculation based on {priority} priority task",
            "confidence_score": 0.5,
            "fallback_strategy_used": "priority_based_timing"
        }

        self.logger.info("Reminder reasoning fallback used")
        return fallback_result

    def _infer_priority_from_text(self, text: str) -> str:
        """
        Infer priority from task text using simple heuristics.

        Args:
            text: Task description text

        Returns:
            Inferred priority ('high', 'medium', 'low')
        """
        text_lower = text.lower()

        high_priority_keywords = [
            'urgent', 'asap', 'immediately', 'now', 'critical', 'emergency',
            'important', 'deadline', 'today', 'within', 'by today', 'crucial'
        ]

        low_priority_keywords = [
            'whenever', 'someday', 'eventually', 'maybe', 'possibly',
            'low priority', 'not urgent', 'take your time'
        ]

        high_count = sum(1 for keyword in high_priority_keywords if keyword in text_lower)
        low_count = sum(1 for keyword in low_priority_keywords if keyword in text_lower)

        if high_count > low_count:
            return 'high'
        elif low_count > high_count:
            return 'low'
        else:
            return 'medium'  # Default priority

    def _extract_basic_tags(self, text: str) -> List[str]:
        """
        Extract basic tags from text using simple heuristics.

        Args:
            text: Task description text

        Returns:
            List of extracted tags
        """
        text_lower = text.lower()
        tags = []

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
                tags.append(tag)

        return tags

    def _suggest_default_due_date(self, user_profile: Dict[str, Any]) -> str:
        """
        Suggest default due date based on user profile.

        Args:
            user_profile: User's profile information

        Returns:
            Suggested due date in ISO format
        """
        import datetime

        # Get user's work hours
        work_hours_start = user_profile.get('work_hours_start', '09:00')
        work_hours_end = user_profile.get('work_hours_end', '17:00')

        # Default to next business day
        now = datetime.datetime.now()
        due_date = now + datetime.timedelta(days=1)

        # Adjust to work hours
        time_parts = work_hours_start.split(':')
        due_date = due_date.replace(hour=int(time_parts[0]), minute=int(time_parts[1]))

        return due_date.isoformat()

    def _suggest_default_reminder_time(self, user_profile: Dict[str, Any]) -> str:
        """
        Suggest default reminder time based on user profile.

        Args:
            user_profile: User's profile information

        Returns:
            Suggested reminder time in ISO format
        """
        import datetime

        # Default to 2 hours before due time
        now = datetime.datetime.now()
        reminder_time = now + datetime.timedelta(hours=2)

        return reminder_time.isoformat()

    def _calculate_default_reminder_time(self, priority: str, due_date: str, user_profile: Dict[str, Any]) -> str:
        """
        Calculate default reminder time based on priority.

        Args:
            priority: Task priority
            due_date: Task due date
            user_profile: User's profile information

        Returns:
            Calculated reminder time in ISO format
        """
        import datetime

        if due_date:
            due_dt = datetime.datetime.fromisoformat(due_date.replace('Z', '+00:00'))
        else:
            due_dt = datetime.datetime.now() + datetime.timedelta(days=1)

        # Default reminder advance times by priority
        priority_reminder_advance = {
            'high': datetime.timedelta(hours=1),    # 1 hour before for high priority
            'medium': datetime.timedelta(hours=2),  # 2 hours before for medium priority
            'low': datetime.timedelta(hours=4)      # 4 hours before for low priority
        }

        advance_time = priority_reminder_advance.get(priority, datetime.timedelta(hours=2))
        reminder_time = due_dt - advance_time

        # Ensure reminder is not in the past
        now = datetime.datetime.now(due_dt.tzinfo) if due_dt.tzinfo else datetime.datetime.utcnow()
        if reminder_time < now:
            reminder_time = now + datetime.timedelta(minutes=15)  # Set to 15 minutes from now if in the past

        return reminder_time.isoformat()

    def _default_fallback_response(self, agent_name: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Default fallback response when no specific strategy is available.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent

        Returns:
            Default fallback response
        """
        self.logger.warning(f"Using default fallback for {agent_name}")

        default_responses = {
            "task_interpreter": {
                "title": "Fallback Task",
                "description": "Task created from fallback mechanism",
                "priority": "medium",
                "tags": ["fallback"],
                "due_at": None,
                "remind_at": None,
                "recurrence_rule": None,
                "confidence": 0.3,
                "extracted_entities": [],
                "fallback_strategy_used": "default_response"
            },
            "scheduling_intelligence": {
                "suggested_due_date": (datetime.now() + timedelta(days=1)).isoformat(),
                "suggested_remind_at": (datetime.now() + timedelta(hours=2)).isoformat(),
                "reasoning": "Default scheduling due to agent unavailability",
                "conflicts": [],
                "alternative_schedules": [],
                "confidence": 0.3,
                "fallback_strategy_used": "default_response"
            },
            "reminder_reasoning": {
                "calculated_reminder_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "base_calculation": (datetime.now() + timedelta(hours=2)).isoformat(),
                "adjustments_applied": [],
                "reasoning": "Default reminder calculation due to agent unavailability",
                "confidence_score": 0.3,
                "fallback_strategy_used": "default_response"
            }
        }

        return default_responses.get(agent_name, {
            "error": f"Agent {agent_name} unavailable",
            "fallback_strategy_used": "default_response",
            "recovery_hint": "Try again later or contact support"
        })

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on all agents and fallback mechanisms.

        Returns:
            Health check results
        """
        health_results = {
            "timestamp": datetime.now().isoformat(),
            "agent_health": self.health_status.copy(),
            "fallback_strategies_registered": list(self.fallback_strategies.keys()),
            "overall_status": "degraded" if not all(self.health_status.values()) else "healthy"
        }

        return health_results


# Global instance
ai_fallback_manager = AIAgentFallbackManager()