"""
Row Level Security (RLS) configuration for PostgreSQL database.
"""

from typing import Optional
from sqlmodel import Session, create_engine
from .models import User, Task, Event, AuditLog


class RowLevelSecurity:
    """
    Class to manage Row Level Security policies in PostgreSQL.
    """

    def __init__(self, session: Session):
        self.session = session

    def enable_rls_on_table(self, table_name: str):
        """
        Enable Row Level Security on a specific table.

        Args:
            table_name: Name of the table to enable RLS on
        """
        # Raw SQL to enable RLS on the table
        enable_rls_sql = f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;"
        self.session.exec(enable_rls_sql)
        self.session.commit()

    def create_rls_policy_for_user_isolation(self, table_name: str, user_column: str = "user_id"):
        """
        Create a policy to ensure users can only access their own data.

        Args:
            table_name: Name of the table to apply the policy to
            user_column: Name of the column that stores user ID (default: "user_id")
        """
        policy_name = f"{table_name}_tenant_isolation_policy"

        # Raw SQL to create the RLS policy
        create_policy_sql = f"""
        CREATE POLICY {policy_name} ON {table_name}
        FOR ALL TO todo_app_user
        USING ({user_column} = current_setting('app.current_user_id')::uuid);
        """

        self.session.exec(create_policy_sql)
        self.session.commit()

    def create_permissive_policy(self, policy_name: str, table_name: str, using_clause: str):
        """
        Create a permissive RLS policy.

        Args:
            policy_name: Name of the policy
            table_name: Name of the table
            using_clause: The USING clause for the policy
        """
        create_policy_sql = f"""
        CREATE POLICY {policy_name} ON {table_name}
        AS PERMISSIVE
        FOR ALL TO todo_app_user
        USING ({using_clause});
        """

        self.session.exec(create_policy_sql)
        self.session.commit()

    def setup_all_rls_policies(self):
        """
        Set up RLS policies for all tenant-isolated tables.
        """
        # Enable RLS on all tenant-isolated tables
        tenant_isolated_tables = [
            ("tasks", "user_id"),
            ("events", "user_id"),
            ("audit_logs", "user_id")
        ]

        for table_name, user_column in tenant_isolated_tables:
            # Enable RLS on the table
            self.enable_rls_on_table(table_name)

            # Create tenant isolation policy
            self.create_rls_policy_for_user_isolation(table_name, user_column)

    def set_current_user_in_session(self, user_id: str):
        """
        Set the current user ID in the PostgreSQL session for RLS evaluation.

        Args:
            user_id: The ID of the current user
        """
        set_user_sql = f"SET app.current_user_id = '{user_id}';"
        self.session.exec(set_user_sql)
        self.session.commit()

    def setup_rls_schema(self):
        """
        Create the necessary schema for RLS if it doesn't exist.
        """
        # Create app schema if it doesn't exist
        create_schema_sql = "CREATE SCHEMA IF NOT EXISTS app;"
        self.session.exec(create_schema_sql)

        # Commit the transaction
        self.session.commit()


# Example usage function
def setup_row_level_security(session: Session):
    """
    Convenience function to set up row level security for the entire application.

    Args:
        session: Database session
    """
    rls = RowLevelSecurity(session)

    # Set up the RLS schema
    rls.setup_rls_schema()

    # Set up all RLS policies
    rls.setup_all_rls_policies()

    return rls