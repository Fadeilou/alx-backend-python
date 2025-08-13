#!/usr/bin/env python3
"""Create and manage coroutines"""
import asyncio
from typing import List
task_wait_random = __import__('3-tasks').task_wait_random


async def task_wait_n(n: int, max_delay: int) -> List[float]:
    tasks = [task_wait_random(max_delay) for _ in range(n)]
    delays = []

    # Await tasks as they complete and append delays in order
    for task in asyncio.as_completed(tasks):
        delay = await task
        delays.append(delay)

    return delays
