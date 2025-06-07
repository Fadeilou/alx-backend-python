#!/usr/bin/env python3
"""
Unit tests for the utils.py module.
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from typing import Dict, Tuple, Any, Sequence

from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Test suite for the `access_nested_map` function.
    """
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Dict,
        path: Tuple[str],
        expected: Any
    ) -> None:
        """
        Tests that access_nested_map returns the correct value for valid inputs.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",)),
        ({"a": 1}, ("a", "b")),
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Dict,
        path: Tuple[str]
    ) -> None:
        """
        Tests that access_nested_map raises a KeyError for invalid paths.
        """
        with self.assertRaises(KeyError) as context:
            access_nested_map(nested_map, path)
        self.assertEqual(str(context.exception), f"'{path[-1]}'")


class TestGetJson(unittest.TestCase):
    """
    Test suite for the `get_json` function.
    """
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: Dict) -> None:
        """
        Tests that get_json returns the expected dictionary from a URL.
        """
        # Create a mock for requests.get
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        with patch('requests.get', return_value=mock_response) as mock_get:
            # Call the function
            result = get_json(test_url)

            # Assertions
            mock_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Test suite for the `memoize` decorator.
    """
    def test_memoize(self) -> None:
        """
        Tests that the memoize decorator caches the result of a method.
        """
        class TestClass:
            """A sample class for testing memoization."""
            def a_method(self) -> int:
                """A method that returns a constant value."""
                return 42

            @memoize
            def a_property(self) -> int:
                """A property that uses memoization."""
                return self.a_method()

        with patch.object(
            TestClass,
            'a_method',
            return_value=42
        ) as mock_method:
            test_instance = TestClass()

            # Call the property twice
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Assertions
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
