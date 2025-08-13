#!/usr/bin/env python3
"""Defines a function make_multiplier that takes one argument"""
from typing import Callable


def make_multiplier(multiplier: float) -> Callable[[float], float]:
    """Return a function that multiplies by the input multiplier"""

    def inner(number: float) -> float:
        """Multiplies the input number the multiplier"""
        return number * multiplier

    return inner
