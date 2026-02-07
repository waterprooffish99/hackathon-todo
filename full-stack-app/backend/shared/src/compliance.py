"""
Compliance and data retention/deletion policies for the Cloud-Native AI Todo Platform.
"""

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlmodel import Session, select
from .models import User, Task, Event, AuditLog


class ComplianceManager:
    """
    Manager for handling compliance requirements including data retention and deletion policies.
    """

    def __init__(self, session: Session):
        self.session = session

    async def apply_retention_policy(self, days: int = 365) -> int:
        """
        Apply data retention policy by removing data older than specified days.

        Args:
            days: Number of days to retain data (default: 365)

        Returns:
            Number of records deleted
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # Delete old events
        old_events = await self._get_old_events(cutoff_date)
        deleted_events = 0
        for event in old_events:
            self.session.delete(event)
            deleted_events += 1

        # Delete old audit logs
        old_audit_logs = await self._get_old_audit_logs(cutoff_date)
        deleted_audit_logs = 0
        for log in old_audit_logs:
            self.session.delete(log)
            deleted_audit_logs += 1

        # Commit changes
        self.session.commit()

        return deleted_events + deleted_audit_logs

    async def _get_old_events(self, cutoff_date: datetime) -> List[Event]:
        """
        Get events older than the cutoff date.

        Args:
            cutoff_date: Date before which events are considered old

        Returns:
            List of old events
        """
        statement = select(Event).where(Event.timestamp < cutoff_date)
        events = self.session.exec(statement).all()
        return events

    async def _get_old_audit_logs(self, cutoff_date: datetime) -> List[AuditLog]:
        """
        Get audit logs older than the cutoff date.

        Args:
            cutoff_date: Date before which audit logs are considered old

        Returns:
            List of old audit logs
        """
        statement = select(AuditLog).where(AuditLog.timestamp < cutoff_date)
        logs = self.session.exec(statement).all()
        return logs

    async def anonymize_user_data(self, user_id: str) -> bool:
        """
        Anonymize a user's data upon request (GDPR compliance).

        Args:
            user_id: ID of the user whose data should be anonymized

        Returns:
            True if successful, False otherwise
        """
        try:
            # Instead of deleting, we'll anonymize the user's data
            # Update tasks to anonymize user reference
            tasks = self.session.exec(select(Task).where(Task.user_id == user_id)).all()
            for task in tasks:
                # Anonymize by changing user_id to a generic identifier
                task.user_id = "anonymized-user"
                self.session.add(task)

            # Update events
            events = self.session.exec(select(Event).where(Event.user_id == user_id)).all()
            for event in events:
                event.user_id = "anonymized-user"
                self.session.add(event)

            # Update audit logs
            audit_logs = self.session.exec(select(AuditLog).where(AuditLog.user_id == user_id)).all()
            for log in audit_logs:
                log.user_id = "anonymized-user"
                self.session.add(log)

            self.session.commit()
            return True
        except Exception as e:
            print(f"Error anonymizing user data: {e}")
            return False

    async def delete_user_account(self, user_id: str) -> bool:
        """
        Permanently delete a user's account and associated data.

        Args:
            user_id: ID of the user whose account should be deleted

        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete user's tasks
            tasks = self.session.exec(select(Task).where(Task.user_id == user_id)).all()
            for task in tasks:
                self.session.delete(task)

            # Delete user's events
            events = self.session.exec(select(Event).where(Event.user_id == user_id)).all()
            for event in events:
                self.session.delete(event)

            # Delete user's audit logs
            audit_logs = self.session.exec(select(AuditLog).where(AuditLog.user_id == user_id)).all()
            for log in audit_logs:
                self.session.delete(log)

            # Delete the user
            user = self.session.get(User, user_id)
            if user:
                self.session.delete(user)

            self.session.commit()
            return True
        except Exception as e:
            print(f"Error deleting user account: {e}")
            return False

    async def schedule_data_cleanup(self):
        """
        Schedule regular data cleanup based on retention policies.
        """
        # This would typically be called by a scheduler/cron job
        print("Running scheduled data cleanup...")

        # Apply retention policy (keep data for 1 year by default)
        deleted_count = await self.apply_retention_policy(days=365)
        print(f"Cleaned up {deleted_count} old records")

    async def get_compliance_report(self) -> Dict[str, Any]:
        """
        Generate a compliance report with data retention statistics.

        Returns:
            Dictionary with compliance statistics
        """
        # Count total records
        total_tasks = self.session.exec(select(Task)).count()
        total_events = self.session.exec(select(Event)).count()
        total_audit_logs = self.session.exec(select(AuditLog)).count()
        total_users = self.session.exec(select(User)).count()

        # Get oldest records
        oldest_task = self.session.exec(select(Task).order_by(Task.created_at.asc()).limit(1)).first()
        oldest_event = self.session.exec(select(Event).order_by(Event.timestamp.asc()).limit(1)).first()
        oldest_audit_log = self.session.exec(select(AuditLog).order_by(AuditLog.timestamp.asc()).limit(1)).first()

        report = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_records": {
                "tasks": total_tasks,
                "events": total_events,
                "audit_logs": total_audit_logs,
                "users": total_users
            },
            "oldest_records": {
                "task": oldest_task.created_at.isoformat() if oldest_task else None,
                "event": oldest_event.timestamp.isoformat() if oldest_event else None,
                "audit_log": oldest_audit_log.timestamp.isoformat() if oldest_audit_log else None
            }
        }

        return report


# Example usage function
async def run_compliance_tasks(session: Session):
    """
    Run compliance-related tasks.

    Args:
        session: Database session
    """
    compliance_manager = ComplianceManager(session)

    # Apply retention policy
    deleted_count = await compliance_manager.apply_retention_policy()

    # Generate compliance report
    report = await compliance_manager.get_compliance_report()

    print(f"Compliance tasks completed. Deleted {deleted_count} records.")
    print(f"Compliance report: {report}")

    return deleted_count, report