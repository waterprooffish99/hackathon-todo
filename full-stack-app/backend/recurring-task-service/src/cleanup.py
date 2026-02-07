"""
Cleanup procedures for recurring tasks in the Cloud-Native AI Todo Platform.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session, select, and_

from .models import Task, Event
from .database import get_session


class RecurringTaskCleanupService:
    """
    Service for cleaning up recurring tasks and related resources.
    """

    def __init__(self, session: Session):
        self.session = session
        self.logger = logging.getLogger(__name__)

    async def cleanup_expired_tasks(self, days_old: int = 30) -> int:
        """
        Clean up recurring tasks that have been completed for more than specified days.

        Args:
            days_old: Number of days after which completed recurring tasks should be archived/cleaned up

        Returns:
            Number of tasks cleaned up
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Find completed recurring tasks older than cutoff
        statement = select(Task).where(
            and_(
                Task.completed == True,
                Task.completion_date < cutoff_date,
                Task.recurrence_rule.is_not(None)  # Only recurring tasks
            )
        )

        expired_tasks = self.session.exec(statement).all()

        cleaned_count = 0
        for task in expired_tasks:
            try:
                # Instead of deleting, we'll archive these tasks
                # In a real system, you might want to move them to an archive table
                task.archived = True
                task.archived_at = datetime.utcnow()
                self.session.add(task)
                cleaned_count += 1
            except Exception as e:
                self.logger.error(f"Error cleaning up task {task.task_id}: {e}")

        self.session.commit()
        self.logger.info(f"Cleaned up {cleaned_count} expired recurring tasks")
        return cleaned_count

    async def cleanup_old_events(self, days_old: int = 90) -> int:
        """
        Clean up old events that are no longer needed for processing.

        Args:
            days_old: Number of days after which events should be cleaned up

        Returns:
            Number of events cleaned up
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)

        # Find old events
        statement = select(Event).where(Event.timestamp < cutoff_date)
        old_events = self.session.exec(statement).all()

        cleaned_count = 0
        for event in old_events:
            try:
                # Only clean up events that have been processed
                if event.processed:
                    self.session.delete(event)
                    cleaned_count += 1
            except Exception as e:
                self.logger.error(f"Error cleaning up event {event.event_id}: {e}")

        self.session.commit()
        self.logger.info(f"Cleaned up {cleaned_count} old events")
        return cleaned_count

    async def cleanup_orphaned_tasks(self) -> int:
        """
        Clean up orphaned tasks that don't have corresponding user records.

        Returns:
            Number of orphaned tasks cleaned up
        """
        # This would involve joining with user table to find tasks without valid users
        # Implementation would depend on the exact table structure
        # For now, this is a placeholder
        self.logger.info("Checking for orphaned tasks...")

        # In a real implementation, you would:
        # 1. Find tasks with user_id that doesn't exist in users table
        # 2. Clean up those tasks
        # 3. Return count of cleaned tasks

        return 0  # Placeholder return

    async def cleanup_duplicate_events(self) -> int:
        """
        Clean up duplicate events based on correlation_id.

        Returns:
            Number of duplicate events cleaned up
        """
        # Find events with duplicate correlation IDs
        # This is a simplified approach - in reality you'd want to be more careful
        # about which duplicate to keep

        from sqlalchemy import func

        # Find correlation_ids that appear more than once
        duplicate_corr_ids = self.session.exec(
            select(Event.correlation_id)
            .group_by(Event.correlation_id)
            .having(func.count(Event.correlation_id) > 1)
        ).all()

        cleaned_count = 0
        for corr_id in duplicate_corr_ids:
            # Keep the first occurrence, remove others
            events_with_corr_id = self.session.exec(
                select(Event)
                .where(Event.correlation_id == corr_id)
                .order_by(Event.timestamp)
            ).all()

            # Remove duplicates (keep first one)
            for event in events_with_corr_id[1:]:
                try:
                    self.session.delete(event)
                    cleaned_count += 1
                except Exception as e:
                    self.logger.error(f"Error cleaning up duplicate event {event.event_id}: {e}")

        self.session.commit()
        self.logger.info(f"Cleaned up {cleaned_count} duplicate events")
        return cleaned_count

    async def run_regular_cleanup(self):
        """
        Run all regular cleanup procedures.
        This method should be called periodically by a scheduler.
        """
        self.logger.info("Starting regular cleanup procedures...")

        results = {
            "expired_tasks": await self.cleanup_expired_tasks(),
            "old_events": await self.cleanup_old_events(),
            "orphaned_tasks": await self.cleanup_orphaned_tasks(),
            "duplicate_events": await self.cleanup_duplicate_events()
        }

        self.logger.info(f"Cleanup completed. Results: {results}")
        return results

    async def schedule_cleanup_jobs(self):
        """
        Schedule cleanup jobs to run periodically.
        This would typically be called when the service starts up.
        """
        # In a real implementation, you might use APScheduler or similar
        # to schedule the cleanup jobs to run periodically

        # For demonstration purposes, we'll just log what would be scheduled
        self.logger.info("Scheduling cleanup jobs:")
        self.logger.info("- Expired tasks cleanup: Daily at 2 AM")
        self.logger.info("- Old events cleanup: Daily at 3 AM")
        self.logger.info("- Duplicate events cleanup: Weekly on Sundays at 1 AM")
        self.logger.info("- Orphaned tasks cleanup: Weekly on Saturdays at 1 AM")

        # Example of how to schedule with APScheduler:
        # scheduler = AsyncIOScheduler()
        # scheduler.add_job(self.cleanup_expired_tasks, 'cron', hour=2, minute=0)
        # scheduler.add_job(self.cleanup_old_events, 'cron', hour=3, minute=0)
        # scheduler.add_job(self.cleanup_duplicate_events, 'cron', day_of_week='sun', hour=1, minute=0)
        # scheduler.add_job(self.cleanup_orphaned_tasks, 'cron', day_of_week='sat', hour=1, minute=0)
        # scheduler.start()


# Global instance
cleanup_service = RecurringTaskCleanupService(get_session())