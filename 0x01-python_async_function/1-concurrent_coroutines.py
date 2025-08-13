#!/usr/bin/env python3
"""
Create and manage coroutines
import wait_random from 0-basic_async_syntax
"""
import asyncio
from typing import List
wait_random = __import__('0-basic_async_syntax').wait_random


async def wait_n(n: int, max_delay: int) -> List[float]:
    """
    Spawns wait_random n times with the specified max_delay

    Args:
        n: The number of times to spawn wait_random
        max_delay: The maximum delay for each wait_random coroutine

    Returns:
        A list of the delays in ascending order
    """
    tasks = [wait_random(max_delay) for _ in range(n)]
    tasks = asyncio.as_completed(tasks)
    delays = []

    # Await tasks as they complete and add delays to the list in order
    for task in tasks:
        delay = await task
        delays.append(delay)

    return delays
