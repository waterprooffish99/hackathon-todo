"""
Caching mechanisms for AI subagent responses to optimize token usage.
"""

import hashlib
import json
import asyncio
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Union
from redis.asyncio import Redis
from redis.exceptions import RedisError


class AIAgentCache:
    """
    Cache for AI subagent responses to optimize token usage and reduce redundant processing.
    """

    def __init__(self, redis_client: Redis, default_ttl: int = 3600):  # 1 hour default TTL
        self.redis = redis_client
        self.default_ttl = default_ttl

    def _generate_cache_key(self, agent_name: str, input_data: Union[str, Dict[str, Any]]) -> str:
        """
        Generate a cache key for the given agent and input data.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent

        Returns:
            Cache key string
        """
        # Convert input data to JSON string for consistent hashing
        if isinstance(input_data, str):
            input_str = input_data
        else:
            input_str = json.dumps(input_data, sort_keys=True, default=str)

        # Create a unique identifier for the combination of agent and input
        combined = f"{agent_name}:{input_str}"
        hash_object = hashlib.sha256(combined.encode())
        return f"ai_cache:{agent_name}:{hash_object.hexdigest()}"

    async def get_response(self, agent_name: str, input_data: Union[str, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Get cached response for the given agent and input data.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent

        Returns:
            Cached response if available, None otherwise
        """
        try:
            cache_key = self._generate_cache_key(agent_name, input_data)
            cached_data = await self.redis.get(cache_key)

            if cached_data:
                # Deserialize the cached response
                return json.loads(cached_data)
        except (RedisError, json.JSONDecodeError, Exception) as e:
            print(f"Error retrieving from cache for {agent_name}: {e}")

        return None

    async def set_response(
        self,
        agent_name: str,
        input_data: Union[str, Dict[str, Any]],
        response: Dict[str, Any],
        ttl: Optional[int] = None
    ) -> bool:
        """
        Store response in cache for the given agent and input data.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent
            response: Response to cache
            ttl: Time-to-live in seconds (uses default if not provided)

        Returns:
            True if successfully cached, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(agent_name, input_data)
            ttl = ttl or self.default_ttl

            # Serialize the response
            serialized_response = json.dumps(response, default=str)

            # Store in Redis with TTL
            await self.redis.setex(cache_key, ttl, serialized_response)
            return True
        except (RedisError, json.JSONEncodeError, Exception) as e:
            print(f"Error storing in cache for {agent_name}: {e}")
            return False

    async def invalidate_response(self, agent_name: str, input_data: Union[str, Dict[str, Any]]) -> bool:
        """
        Invalidate a specific cached response.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent

        Returns:
            True if successfully invalidated, False otherwise
        """
        try:
            cache_key = self._generate_cache_key(agent_name, input_data)
            result = await self.redis.delete(cache_key)
            return result > 0
        except RedisError as e:
            print(f"Error invalidating cache for {agent_name}: {e}")
            return False

    async def invalidate_agent_cache(self, agent_name: str) -> bool:
        """
        Invalidate all cached responses for a specific agent.

        Args:
            agent_name: Name of the AI agent

        Returns:
            True if successfully invalidated, False otherwise
        """
        try:
            # Find all keys matching the agent's cache pattern
            pattern = f"ai_cache:{agent_name}:*"
            keys = await self.redis.keys(pattern)

            if keys:
                # Delete all matching keys
                await self.redis.delete(*keys)

            return True
        except RedisError as e:
            print(f"Error invalidating cache for agent {agent_name}: {e}")
            return False

    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        try:
            # Get info about Redis
            info = await self.redis.info()

            # Get our specific cache keys
            all_keys = await self.redis.keys("ai_cache:*")

            # Group by agent
            agent_stats = {}
            for key in all_keys:
                key_str = key.decode() if isinstance(key, bytes) else key
                parts = key_str.split(":")
                if len(parts) >= 3:
                    agent_name = parts[2]
                    if agent_name not in agent_stats:
                        agent_stats[agent_name] = 0
                    agent_stats[agent_name] += 1

            stats = {
                "total_cached_responses": len(all_keys),
                "agent_breakdown": agent_stats,
                "redis_info": {
                    "used_memory_human": info.get("used_memory_human"),
                    "connected_clients": info.get("connected_clients"),
                    "total_commands_processed": info.get("total_commands_processed"),
                    "keyspace_hits": info.get("keyspace_hits"),
                    "keyspace_misses": info.get("keyspace_misses")
                },
                "hit_rate": self._calculate_hit_rate(info)
            }

            return stats
        except RedisError as e:
            print(f"Error getting cache stats: {e}")
            return {"error": str(e)}

    def _calculate_hit_rate(self, redis_info: Dict[str, Any]) -> Optional[float]:
        """
        Calculate cache hit rate.

        Args:
            redis_info: Redis info dictionary

        Returns:
            Hit rate as a percentage, or None if not calculable
        """
        hits = redis_info.get("keyspace_hits", 0)
        misses = redis_info.get("keyspace_misses", 0)
        total = hits + misses

        if total > 0:
            return (hits / total) * 100
        else:
            return None

    async def warmup_cache(self, agent_name: str, training_data: List[Dict[str, Any]]) -> int:
        """
        Warm up the cache with training data.

        Args:
            agent_name: Name of the AI agent
            training_data: List of {input: ..., output: ...} pairs

        Returns:
            Number of items cached
        """
        cached_count = 0
        for item in training_data:
            input_data = item.get("input")
            output_data = item.get("output")

            if input_data and output_data:
                success = await self.set_response(agent_name, input_data, output_data)
                if success:
                    cached_count += 1

        return cached_count


class AICacheMiddleware:
    """
    Middleware to automatically cache AI subagent responses.
    """

    def __init__(self, cache: AIAgentCache):
        self.cache = cache

    async def execute_with_cache(
        self,
        agent_name: str,
        input_data: Union[str, Dict[str, Any]],
        agent_func,
        *args,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute an AI agent function with automatic caching.

        Args:
            agent_name: Name of the AI agent
            input_data: Input data for the agent
            agent_func: Function to execute if cache miss
            *args: Additional arguments to pass to the agent function
            **kwargs: Additional keyword arguments to pass to the agent function

        Returns:
            Response from cache or agent execution
        """
        # Try to get from cache first
        cached_response = await self.cache.get_response(agent_name, input_data)

        if cached_response is not None:
            # Return cached response with cache hit indicator
            cached_response["_cached"] = True
            cached_response["_cache_hit"] = True
            return cached_response

        # Execute the agent function since no cache hit
        response = await agent_func(input_data, *args, **kwargs)

        # Add cache metadata
        response["_cached"] = False
        response["_cache_hit"] = False
        response["_timestamp"] = datetime.utcnow().isoformat()

        # Store in cache for future requests
        await self.cache.set_response(agent_name, input_data, response)

        return response


# Global instance (would be initialized with actual Redis client when used)
# ai_cache = AIAgentCache(redis_client=redis_instance)