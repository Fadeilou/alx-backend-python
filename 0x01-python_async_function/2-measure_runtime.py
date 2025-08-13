#!/usr/bin/env python3
"""
Create and manage coroutines
import wait_n from 1-concurrent_coroutines
"""
import asyncio
import time
wait_n = __import__('1-concurrent_coroutines').wait_n


def measure_time(n: int, max_delay: int) -> float:
    """
    Measure the total execution time of wait_n(n, max_delay) and
    returns the average time per call (total_time / n).

    Args:
        n: The numer of times to spawn wait_random.
        max_delay: The maximum delay for each wait random call.

    Returns:
       The average execution time per wait_n call (float)
    """
    start_time = time.perf_counter()

    async def wrapper():
        await wait_n(n, max_delay)

    asyncio.run(wrapper())

    end_time = time.perf_counter()
    total_time = end_time - start_time

    return total_time / n
