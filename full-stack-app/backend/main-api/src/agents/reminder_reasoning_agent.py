"""
Reminder Reasoning Agent for smart notification timing.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import pytz


class ReminderReasoningAgent:
    """
    AI agent for calculating and managing reminder timing based on task type and user behavior.
    """

    def __init__(self):
        pass

    async def calculate_optimal_reminder_time(
        self,
        task: Dict[str, Any],
        user_profile: Dict[str, Any],
        task_history: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Calculate optimal reminder time based on task type and user behavior.

        Args:
            task: Task details
            user_profile: User's profile and preferences
            task_history: Historical data about how user interacts with similar tasks

        Returns:
            Dictionary with reminder calculation results
        """
        if task_history is None:
            task_history = []

        # Determine base reminder time based on task type
        base_reminder_time = await self._calculate_base_reminder_time(task, user_profile)

        # Adjust based on user behavior patterns
        adjusted_reminder_time = await self._adjust_for_user_behavior(
            base_reminder_time,
            task,
            user_profile,
            task_history
        )

        # Apply user preferences and constraints
        final_reminder_time = await self._apply_user_constraints(
            adjusted_reminder_time,
            user_profile
        )

        # Generate reasoning explanation
        reasoning = await self._generate_reasoning(task, user_profile, task_history)

        return {
            "calculated_reminder_time": final_reminder_time,
            "base_calculation": base_reminder_time,
            "adjustments_applied": reasoning.get("adjustments", []),
            "reasoning": reasoning,
            "confidence_score": reasoning.get("confidence", 0.85)
        }

    async def _calculate_base_reminder_time(
        self,
        task: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> datetime:
        """
        Calculate base reminder time based on task type and urgency.

        Args:
            task: Task details
            user_profile: User's profile and preferences

        Returns:
            Calculated reminder datetime
        """
        task_type = self._categorize_task(task)
        due_date = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00')) if task['due_at'] else None
        priority = task.get('priority', 'medium')

        # Base advance times by task type
        base_advances = {
            'work': timedelta(hours=24),
            'personal': timedelta(hours=2),
            'health': timedelta(hours=1),
            'financial': timedelta(days=3),
            'social': timedelta(hours=4),
            'general': timedelta(hours=6)
        }

        # Priority adjustments
        priority_multipliers = {
            'high': 0.5,    # Remind earlier for high priority
            'medium': 1.0,  # Normal timing for medium priority
            'low': 1.5      # Remind later for low priority
        }

        # Get base advance time
        base_advance = base_advances.get(task_type, timedelta(hours=6))

        # Apply priority adjustment
        multiplier = priority_multipliers.get(priority, 1.0)
        adjusted_advance = timedelta(seconds=base_advance.total_seconds() * multiplier)

        # Calculate base reminder time
        if due_date:
            base_reminder_time = due_date - adjusted_advance
        else:
            # If no due date, set reminder for tomorrow
            tomorrow = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0) + timedelta(days=1)
            base_reminder_time = tomorrow - adjusted_advance

        return base_reminder_time

    async def _adjust_for_user_behavior(
        self,
        base_reminder_time: datetime,
        task: Dict[str, Any],
        user_profile: Dict[str, Any],
        task_history: List[Dict[str, Any]]
    ) -> datetime:
        """
        Adjust reminder time based on user behavior patterns.

        Args:
            base_reminder_time: Initial calculated reminder time
            task: Task details
            user_profile: User's profile and preferences
            task_history: Historical task completion data

        Returns:
            Adjusted reminder datetime
        """
        if not task_history:
            return base_reminder_time

        task_type = self._categorize_task(task)

        # Analyze user's historical behavior for this task type
        relevant_history = [t for t in task_history if self._categorize_task(t) == task_type]

        if not relevant_history:
            return base_reminder_time

        # Calculate average time between reminder and completion
        avg_time_to_completion = self._calculate_avg_time_to_completion(relevant_history)

        # Adjust reminder based on user's typical behavior
        if avg_time_to_completion:
            # If user typically completes tasks quickly, remind earlier
            # If user typically completes tasks late, remind later
            adjustment_factor = self._calculate_behavior_adjustment(avg_time_to_completion)

            # Apply adjustment to base reminder time
            adjustment = timedelta(seconds=avg_time_to_completion.total_seconds() * adjustment_factor)
            adjusted_time = base_reminder_time - adjustment

            # Ensure reminder is not after due date
            due_date = datetime.fromisoformat(task['due_at'].replace('Z', '+00:00')) if task['due_at'] else None
            if due_date and adjusted_time > due_date:
                adjusted_time = due_date - timedelta(minutes=5)  # At least 5 mins before due

            return adjusted_time

        return base_reminder_time

    def _calculate_avg_time_to_completion(self, task_history: List[Dict[str, Any]]) -> timedelta:
        """
        Calculate average time between reminder and task completion from history.

        Args:
            task_history: Historical task data

        Returns:
            Average time to completion
        """
        total_time = timedelta()
        count = 0

        for task in task_history:
            if task.get('remind_at') and task.get('completion_date'):
                remind_time = datetime.fromisoformat(task['remind_at'].replace('Z', '+00:00'))
                completion_time = datetime.fromisoformat(task['completion_date'].replace('Z', '+00:00'))

                time_diff = completion_time - remind_time
                if time_diff > timedelta(0):  # Only count positive differences
                    total_time += time_diff
                    count += 1

        if count > 0:
            return total_time / count
        else:
            return timedelta(hours=2)  # Default average

    def _calculate_behavior_adjustment(self, avg_time_to_completion: timedelta) -> float:
        """
        Calculate adjustment factor based on user behavior.

        Args:
            avg_time_to_completion: Average time user takes to complete tasks

        Returns:
            Adjustment factor (positive for earlier reminders, negative for later)
        """
        # Standard time expectation (2 hours)
        standard_time = timedelta(hours=2)

        # If user completes tasks faster than expected, adjust to remind earlier
        if avg_time_to_completion < standard_time:
            # User is quick, remind earlier
            ratio = avg_time_to_completion / standard_time
            return -(1.0 - ratio.value)  # Negative for earlier reminder
        else:
            # User is slow, remind later
            ratio = avg_time_to_completion / standard_time
            return ratio.value - 1.0  # Positive for later reminder

    async def _apply_user_constraints(
        self,
        reminder_time: datetime,
        user_profile: Dict[str, Any]
    ) -> datetime:
        """
        Apply user constraints like quiet hours, preferred times, etc.

        Args:
            reminder_time: Calculated reminder time
            user_profile: User's profile and preferences

        Returns:
            Final reminder time with constraints applied
        """
        # Apply timezone
        tz_str = user_profile.get('timezone', 'UTC')
        tz = pytz.timezone(tz_str)
        localized_time = reminder_time.astimezone(tz)

        # Apply quiet hours constraint
        quiet_hours = user_profile.get('quiet_hours', {})
        if quiet_hours:
            start_hour = quiet_hours.get('start', 22)  # Default to 10 PM
            end_hour = quiet_hours.get('end', 7)      # Default to 7 AM

            # Check if reminder falls in quiet hours
            if start_hour <= localized_time.hour <= 23 or 0 <= localized_time.hour < end_hour:
                # Adjust to the beginning of the next available period
                new_hour = end_hour
                adjusted_time = localized_time.replace(
                    hour=new_hour,
                    minute=0,
                    second=0,
                    microsecond=0
                )

                # If this is still in the past, move to tomorrow
                now = datetime.now(tz)
                if adjusted_time < now:
                    adjusted_time = adjusted_time + timedelta(days=1)
                    adjusted_time = adjusted_time.replace(hour=new_hour)

                return adjusted_time.astimezone(pytz.UTC)

        # Apply preferred notification times
        preferred_times = user_profile.get('preferred_notification_times', [])
        if preferred_times and localized_time.strftime('%H:%M') not in preferred_times:
            # Find the closest preferred time
            closest_time = self._find_closest_preferred_time(localized_time, preferred_times)
            if closest_time:
                hour, minute = map(int, closest_time.split(':'))
                adjusted_time = localized_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

                # If this is in the past, move to tomorrow
                now = datetime.now(tz)
                if adjusted_time < now:
                    adjusted_time = adjusted_time + timedelta(days=1)

                return adjusted_time.astimezone(pytz.UTC)

        return reminder_time

    def _find_closest_preferred_time(self, current_time: datetime, preferred_times: List[str]) -> str:
        """
        Find the closest preferred time to the current time.

        Args:
            current_time: Current time
            preferred_times: List of preferred times in HH:MM format

        Returns:
            Closest preferred time string
        """
        if not preferred_times:
            return None

        current_minutes = current_time.hour * 60 + current_time.minute

        # Convert preferred times to minutes and find the closest one
        time_diffs = []
        for pref_time in preferred_times:
            hour, minute = map(int, pref_time.split(':'))
            pref_minutes = hour * 60 + minute
            diff = abs(pref_minutes - current_minutes)
            time_diffs.append((diff, pref_time))

        # Sort by difference and return the closest time
        time_diffs.sort(key=lambda x: x[0])
        return time_diffs[0][1]

    async def _generate_reasoning(
        self,
        task: Dict[str, Any],
        user_profile: Dict[str, Any],
        task_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate reasoning for reminder calculation.

        Args:
            task: Task details
            user_profile: User's profile and preferences
            task_history: Historical task data

        Returns:
            Dictionary with reasoning explanation
        """
        task_type = self._categorize_task(task)
        priority = task.get('priority', 'medium')

        # Base calculation reasoning
        base_reasoning = f"Initial reminder calculated based on task type '{task_type}' and priority '{priority}'"

        # Behavior adjustment reasoning
        if task_history:
            relevant_history = [t for t in task_history if self._categorize_task(t) == task_type]
            if relevant_history:
                avg_completion = self._calculate_avg_time_to_completion(relevant_history)
                behavior_reasoning = f"Adjusted based on user's historical behavior completing similar tasks in ~{avg_completion}"
            else:
                behavior_reasoning = "No historical data for this task type, using default timing"
        else:
            behavior_reasoning = "No historical data available, using default timing"

        # Constraints applied
        constraints_applied = []
        if user_profile.get('quiet_hours'):
            constraints_applied.append("Quiet hours restriction applied")
        if user_profile.get('preferred_notification_times'):
            constraints_applied.append("Preferred notification times applied")

        return {
            "base_calculation": base_reasoning,
            "behavior_adjustment": behavior_reasoning,
            "constraints_applied": constraints_applied,
            "confidence": 0.85,
            "adjustments": [
                {"type": "priority", "factor": f"Priority-based timing for {priority} priority"},
                {"type": "behavior", "factor": "Historical behavior pattern adjustment" if task_history else "Default timing"},
                {"type": "constraint", "factor": "User preference constraints applied" if constraints_applied else "No constraints applied"}
            ]
        }

    def _categorize_task(self, task: Dict[str, Any]) -> str:
        """
        Categorize a task based on its properties.

        Args:
            task: Task details

        Returns:
            Task category
        """
        if 'category' in task and task['category']:
            return task['category']

        # Fallback to categorization based on title/description
        title_desc = (task.get('title', '') + ' ' + task.get('description', '')).lower()

        categories = {
            'work': ['meeting', 'report', 'email', 'deadline', 'project', 'boss', 'colleague', 'client'],
            'personal': ['appointment', 'doctor', 'dentist', 'family', 'friend', 'personal'],
            'health': ['exercise', 'workout', 'meditation', 'medication', 'therapy', 'gym'],
            'financial': ['pay', 'bill', 'bank', 'tax', 'invoice', 'subscription', 'expense'],
            'social': ['party', 'dinner', 'lunch', 'coffee', 'hangout', 'event', 'celebration']
        }

        for category, keywords in categories.items():
            if any(keyword in title_desc for keyword in keywords):
                return category

        return 'general'

    async def manage_reminder_updates(
        self,
        original_reminder_time: datetime,
        task_changes: Dict[str, Any],
        user_profile: Dict[str, Any]
    ) -> datetime:
        """
        Manage reminder updates when task details change.

        Args:
            original_reminder_time: Original reminder time
            task_changes: Changes made to the task
            user_profile: User's profile and preferences

        Returns:
            Updated reminder time
        """
        # If due date changed significantly, recalculate reminder
        if 'due_at' in task_changes:
            due_change_threshold = timedelta(hours=2)  # Threshold for significant change
            original_due = datetime.fromisoformat(task_changes.get('original_due_at', datetime.now().isoformat()))
            new_due = datetime.fromisoformat(task_changes['due_at'])

            if abs((new_due - original_due).total_seconds()) > due_change_threshold.total_seconds():
                # Significant due date change, recalculate reminder
                task_copy = task_changes.copy()
                task_copy['due_at'] = task_changes['due_at']
                return await self._calculate_base_reminder_time(task_copy, user_profile)

        # For other changes, decide whether to adjust reminder
        should_adjust = False
        if 'priority' in task_changes:
            # Priority change might warrant reminder adjustment
            should_adjust = True

        if 'title' in task_changes or 'description' in task_changes:
            # Content changes might change task type and thus reminder timing
            should_adjust = True

        if should_adjust:
            # Recalculate based on updated task info
            return await self._calculate_base_reminder_time(task_changes, user_profile)

        # No significant changes, keep original reminder
        return original_reminder_time


# Global instance
reminder_reasoning_agent = ReminderReasoningAgent()