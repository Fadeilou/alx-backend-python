#!/usr/bin/env python3
"""Create and manage coroutines"""
import asyncio
wait_random = __import__('0-basic_async_syntax').wait_random


def task_wait_random(max_delay: int) -> asyncio.Task:
    """
    Create and returns a Task object that will execute the
    wait_random coroutine

    Args:
        max_delay: The maximum delay for the wait_random coroutine

    Returns:
        An asyncio.Task object representing the execution
        of the wait_random
    """
    task = asyncio.create_task(wait_random(max_delay))
    return task
