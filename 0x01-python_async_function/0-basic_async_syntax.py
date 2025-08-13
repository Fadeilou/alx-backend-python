#!/usr/bin/env python3
"""
Modules used to create and manage coroutines and offers functions
for generating random numbers
"""
import asyncio
import random


async def wait_random(max_delay: int = 10) -> float:
    """
    Waits for a random delay betweeen 0 and max_delay seconds
    and returns it.

    Args:
        max_delay: The maximum delay in seconds. Defaults to 10.

    Returns:
        The actual delay in seconds that was waited.
    """
    # Generate a random delay between 0 and max_delay as a float
    delay = random.uniform(0, max_delay)

    # Pause the coroutine for the specified delay
    await asyncio.sleep(delay)

    # Return the actual delay
    return delay
