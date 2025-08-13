#!/usr/bin/env python3
"""
Create and manage coroutines
import async_comprehension from 1-async_comprehension
"""
import asyncio
async_comprehension = __import__('1-async_comprehension').async_comprehension


async def measure_runtime() -> float:
    """
    Measure the total runtime of executing async_comprehension
    four times in parallel
    """
    start_time = asyncio.get_running_loop().time()
    await asyncio.gather(*[async_comprehension() for _ in range(4)])
    end_time = asyncio.get_running_loop().time()
    return end_time - start_time
