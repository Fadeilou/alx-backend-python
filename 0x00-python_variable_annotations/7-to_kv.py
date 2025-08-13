#!/usr/bin/env python3
"""Defines a function to_kv that takes two arguments"""
from typing import Union, Tuple


def to_kv(k: str, v: Union[int, float]) -> Tuple[str, float]:
    """
    Takes a tring key and an int/float value and returns a tuple with
    key and squared value (float)"""
    return k, v**2
