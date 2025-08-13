#!/usr/bin/env python3
"""Defines a function sum_mixed_list that takes one argument"""
from typing import List, Union


def sum_mixed_list(mxd_lst: List[Union[int, float]]) -> float:
    """Calculates the sum of elements in a list of integers or floats."""
    return sum(mxd_lst)
