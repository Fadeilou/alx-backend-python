# 0x03. Unittests and Integration Tests

This project focuses on learning the principles and practices of unit and integration testing in Python. It covers the use of the `unittest` framework, the `unittest.mock` library for mocking objects and external calls, and the `parameterized` library for creating data-driven tests.

## Learning Objectives
- The difference between unit and integration tests.
- How to write unit tests for Python code.
- How to use `unittest.mock` to patch functions and objects.
- Mocking properties and handling side effects.
- How to use the `parameterized` library to run tests with multiple sets of inputs.
- Writing integration tests using fixtures.
- Understanding and using `setUpClass` and `tearDownClass` methods.

## Files
- `utils.py`: Utility functions to be tested.
- `client.py`: A client for interacting with the GitHub API.
- `fixtures.py`: Test fixtures for integration tests.
- `test_utils.py`: Unit tests for the `utils.py` module.
- `test_client.py`: Unit and integration tests for the `client.py` module.
