"""
Module for implementing retry mechanisms with exponential backoff for failed event processing.
"""

import asyncio
import random
from functools import wraps
from typing import Callable, Any, Union
from datetime import datetime


class RetryConfig:
    """
    Configuration for retry mechanism with exponential backoff.
    """
    def __init__(
        self,
        max_attempts: int = 5,
        base_delay: float = 1.0,  # seconds
        max_delay: float = 60.0,  # seconds
        backoff_factor: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter


async def retry_with_exponential_backoff(
    func: Callable,
    retry_config: RetryConfig,
    *args,
    **kwargs
) -> Any:
    """
    Execute a function with exponential backoff retry mechanism.

    Args:
        func: The function to execute
        retry_config: Configuration for retry mechanism
        *args: Arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function

    Returns:
        Result of the function execution

    Raises:
        Exception: If all retry attempts fail
    """
    last_exception = None

    for attempt in range(retry_config.max_attempts):
        try:
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        except Exception as e:
            last_exception = e

            # If this was the last attempt, raise the exception
            if attempt == retry_config.max_attempts - 1:
                raise last_exception

            # Calculate delay with exponential backoff
            delay = min(
                retry_config.base_delay * (retry_config.backoff_factor ** attempt),
                retry_config.max_delay
            )

            # Add jitter if enabled
            if retry_config.jitter:
                delay *= (0.5 + random.random() * 0.5)

            print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds...")

            # Wait before retrying
            await asyncio.sleep(delay)

    # This line should never be reached, but included for completeness
    raise last_exception


def retryable(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True
):
    """
    Decorator for making a function retryable with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for first retry
        max_delay: Maximum delay in seconds between retries
        backoff_factor: Factor by which delay increases after each attempt
        jitter: Whether to add randomness to delays to prevent thundering herd

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter
            )
            return await retry_with_exponential_backoff(func, config, *args, **kwargs)

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            config = RetryConfig(
                max_attempts=max_attempts,
                base_delay=base_delay,
                max_delay=max_delay,
                backoff_factor=backoff_factor,
                jitter=jitter
            )

            # For synchronous functions, we'll use a simple retry loop
            last_exception = None
            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    # If this was the last attempt, raise the exception
                    if attempt == config.max_attempts - 1:
                        raise last_exception

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.backoff_factor ** attempt),
                        config.max_delay
                    )

                    # Add jitter if enabled
                    if config.jitter:
                        delay *= (0.5 + random.random() * 0.5)

                    print(f"Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay:.2f} seconds...")

                    # Wait before retrying
                    import time
                    time.sleep(delay)

            # This line should never be reached
            raise last_exception

        # Return the appropriate wrapper based on whether the function is async
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


class EventProcessorWithRetry:
    """
    Wrapper for event processors that adds retry capability with exponential backoff.
    """

    def __init__(self, retry_config: RetryConfig = None):
        self.retry_config = retry_config or RetryConfig()

    async def process_event_with_retry(
        self,
        event_processor_func: Callable,
        event_data: dict,
        *args,
        **kwargs
    ) -> Union[Any, None]:
        """
        Process an event with retry mechanism.

        Args:
            event_processor_func: Function to process the event
            event_data: Data of the event to process
            *args: Additional arguments to pass to the processor
            **kwargs: Additional keyword arguments to pass to the processor

        Returns:
            Result of the event processing or None if all retries failed
        """
        try:
            return await retry_with_exponential_backoff(
                event_processor_func,
                self.retry_config,
                event_data,
                *args,
                **kwargs
            )
        except Exception as e:
            print(f"All retry attempts failed for event processing: {str(e)}")
            return None


# Example usage:
# @retryable(max_attempts=3, base_delay=1.0, max_delay=10.0)
# async def example_event_processor(event_data):
#     # Simulate a flaky operation
#     import random
#     if random.random() < 0.7:  # 70% chance of failure
#         raise Exception("Random failure for demonstration")
#     return {"status": "success", "event_id": event_data.get("event_id")}