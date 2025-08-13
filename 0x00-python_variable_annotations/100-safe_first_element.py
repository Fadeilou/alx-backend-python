#!/usr/bin/env python3
"""Defines a function safe_first_element that takes one argument"""
from typing import Sequence, Any, Union


def safe_first_element(lst: Sequence[Any]) -> Union[Any, None]:
    """
    Returns the first element of a sequence, or None if the sequence is empty

    Args:
        lst: A sequence of elements

    Returns:
        The first element of the sequence, or None if the sequence is empty
    """

    if lst:
        return lst[0]
    else:
        return None
