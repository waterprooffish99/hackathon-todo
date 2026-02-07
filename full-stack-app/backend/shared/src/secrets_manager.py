"""
Secure secret management using Dapr Secrets API.
"""

import os
from typing import Optional, Dict, Any
from .dapr_client import dapr_client


class SecretsManager:
    """
    Manager for handling secrets using Dapr Secrets API.
    """

    def __init__(self):
        self.dapr_client = dapr_client

    async def get_secret(self, store_name: str, key: str, metadata: Optional[Dict[str, str]] = None) -> Optional[str]:
        """
        Retrieve a secret from Dapr secret store.

        Args:
            store_name: Name of the secret store
            key: Key of the secret to retrieve
            metadata: Optional metadata for the secret retrieval

        Returns:
            The secret value or None if not found
        """
        try:
            return await self.dapr_client.get_secret(store_name, key, metadata)
        except Exception as e:
            print(f"Error retrieving secret {key} from store {store_name}: {e}")
            return None

    async def get_database_credentials(self) -> Dict[str, str]:
        """
        Get database credentials from secret store.

        Returns:
            Dictionary with database connection parameters
        """
        db_secrets = {
            "host": await self.get_secret("todo-secrets", "db-host") or os.getenv("DB_HOST", "localhost"),
            "port": await self.get_secret("todo-secrets", "db-port") or os.getenv("DB_PORT", "5432"),
            "database": await self.get_secret("todo-secrets", "db-name") or os.getenv("DB_NAME", "todo_db"),
            "username": await self.get_secret("todo-secrets", "db-username") or os.getenv("DB_USERNAME", "todo_user"),
            "password": await self.get_secret("todo-secrets", "db-password") or os.getenv("DB_PASSWORD", ""),
        }

        return db_secrets

    async def get_jwt_secret(self) -> str:
        """
        Get JWT secret key from secret store.

        Returns:
            JWT secret key
        """
        jwt_secret = await self.get_secret("todo-secrets", "jwt-secret-key")
        if not jwt_secret:
            # Fallback to environment variable
            jwt_secret = os.getenv("JWT_SECRET_KEY", "fallback-secret-key-change-in-production")

        return jwt_secret

    async def get_kafka_config(self) -> Dict[str, str]:
        """
        Get Kafka configuration from secret store.

        Returns:
            Dictionary with Kafka connection parameters
        """
        kafka_secrets = {
            "bootstrap_servers": await self.get_secret("todo-secrets", "kafka-bootstrap-servers") or os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            "security_protocol": await self.get_secret("todo-secrets", "kafka-security-protocol") or os.getenv("KAFKA_SECURITY_PROTOCOL", "PLAINTEXT"),
            "sasl_mechanism": await self.get_secret("todo-secrets", "kafka-sasl-mechanism") or os.getenv("KAFKA_SASL_MECHANISM", ""),
            "username": await self.get_secret("todo-secrets", "kafka-username") or os.getenv("KAFKA_USERNAME", ""),
            "password": await self.get_secret("todo-secrets", "kafka-password") or os.getenv("KAFKA_PASSWORD", ""),
        }

        return kafka_secrets

    async def get_external_api_keys(self) -> Dict[str, str]:
        """
        Get external API keys from secret store.

        Returns:
            Dictionary with API keys for external services
        """
        api_keys = {}

        # Example: Get OpenAI API key if needed
        openai_key = await self.get_secret("todo-secrets", "openai-api-key")
        if openai_key:
            api_keys["openai"] = openai_key

        # Add other API keys as needed
        return api_keys

    async def get_encryption_keys(self) -> Dict[str, str]:
        """
        Get encryption keys from secret store.

        Returns:
            Dictionary with encryption keys
        """
        encryption_keys = {
            "aes_key": await self.get_secret("todo-secrets", "encryption-aes-key") or os.getenv("AES_KEY", ""),
            "rsa_public_key": await self.get_secret("todo-secrets", "rsa-public-key") or os.getenv("RSA_PUBLIC_KEY", ""),
            "rsa_private_key": await self.get_secret("todo-secrets", "rsa-private-key") or os.getenv("RSA_PRIVATE_KEY", ""),
        }

        return encryption_keys


# Global instance
secrets_manager = SecretsManager()