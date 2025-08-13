#!/usr/bin/env python3
"""Import async_generator from 0-async_generator"""
from typing import List
import asyncio
async_generator = __import__('0-async_generator').async_generator


async def async_comprehension() -> List[float]:
    """
    Uses async comprehension to collect 10 random numbers
    from async_generator
    """
    return [async_value async for async_value in async_generator()]
