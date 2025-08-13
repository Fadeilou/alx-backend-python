#!/usr/bin/env python3
'''
Common testing patterns such as mocking, parameterizations
and fixtures
'''
import unittest
from parameterized import parameterized
from utils import access_nested_map, get_json, memoize
from unittest.mock import patch, Mock


class TestAccessNestedMap(unittest.TestCase):
    '''
    Test class for the access_nested_map function.
    '''

    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2)
    ])
    def test_access_nested_map(self, nested_map, path, expected):
        '''
        Test that access_nested_map returns the expected result.

        Args:
            nested_map(dict): The nested dictionary.
            path(tuple): The path of keys to access the value.
            expected: The expected value.
            '''
        self.assertEqual(access_nested_map(nested_map, path), expected)

    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(self, nested_map, path, key):
        '''
        Test that access_nested_map raises a KeyError for invalid paths.

        Args:
            nested_map(dict): The nested dictionary.
            path(tuple): The path of keys to access the value.
        '''
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        self.assertEqual(str(cm.exception), repr(key))


class TestGetJson(unittest.TestCase):
    '''
    Test class for the get_json function.
    '''

    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False})
    ])
    def test_get_json(self, test_url, test_payload):
        '''
        Test that get_json returns the expected result and makes the correct
        HTTP call.

        Args:
            test_url(str): The URL to fetch JSON from.
            test_payload(dict): The expected JSON payload.
        '''
        with patch('utils.requests.get') as mocked_get:
            mocked_get.return_value = Mock(json=lambda: test_payload)
            result = get_json(test_url)

            mocked_get.assert_called_once_with(test_url)
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    '''
    Test class for the memoize decorator.
    '''

    def test_memoize(self):
        '''
        Test that the memoize decorator caches the result of a method.
        '''
        class TestClass:
            def a_method(self):
                return 42

            @memoize
            def a_property(self):
                return self.a_method()

        with patch.object(
                TestClass, 'a_method', return_value=42) as mock_method:
            test_instance = TestClass()
            self.assertEqual(test_instance.a_property, 42)
            self.assertEqual(test_instance.a_property, 42)
            mock_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
