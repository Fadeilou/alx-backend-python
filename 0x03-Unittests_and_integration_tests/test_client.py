#!/usr/bin/env python3
"""
Unit and integration tests for the client.py module.
"""
import unittest
from unittest.mock import patch, PropertyMock, Mock
from parameterized import parameterized, parameterized_class
from typing import Dict, List

from client import GithubOrgClient
from fixtures import TEST_SETTING


class TestGithubOrgClient(unittest.TestCase):
    """
    Unit test suite for the `GithubOrgClient` class.
    """
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(
        self,
        org_name: str,
        mock_get_json: Mock
    ) -> None:
        """
        Tests that GithubOrgClient.org returns the correct value.
        """
        test_payload = {"name": org_name, "id": 123}
        mock_get_json.return_value = test_payload

        client = GithubOrgClient(org_name)
        result = client.org

        self.assertEqual(result, test_payload)
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

    def test_public_repos_url(self) -> None:
        """
        Tests the `_public_repos_url` property.
        """
        known_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}
        with patch.object(
            GithubOrgClient,
            'org',
            new_callable=PropertyMock
        ) as mock_org:
            mock_org.return_value = known_payload
            client = GithubOrgClient("google")
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: Mock) -> None:
        """
        Tests the `public_repos` method.
        """
        test_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
        ]
        mock_get_json.return_value = test_payload

        with patch.object(
            GithubOrgClient,
            '_public_repos_url',
            new_callable=PropertyMock
        ) as mock_public_repos_url:
            mock_public_repos_url.return_value = "https://some.url/repos"
            client = GithubOrgClient("google")
            repos = client.public_repos()

            self.assertEqual(repos, ["repo1", "repo2"])
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once_with("https://some.url/repos")

    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(
        self,
        repo: Dict,
        license_key: str,
        expected: bool
    ) -> None:
        """
        Tests the `has_license` static method.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


@parameterized_class(
    ('org_payload', 'repos_payload', 'expected_repos', 'apache2_repos'),
    TEST_SETTING
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Integration test suite for the `GithubOrgClient` class using fixtures.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Sets up the class-level fixtures for integration tests.
        This method mocks `requests.get` to return predefined payloads.
        """
        # Define a side effect function for the mock
        def side_effect(url):
            if url == f"https://api.github.com/orgs/{cls.org_payload['login']}":
                mock_response = Mock()
                mock_response.json.return_value = cls.org_payload
                return mock_response
            if url == cls.org_payload['repos_url']:
                mock_response = Mock()
                mock_response.json.return_value = cls.repos_payload
                return mock_response
            # Return a default mock for any other unhandled URL
            return Mock()

        cls.get_patcher = patch('requests.get', side_effect=side_effect)
        cls.mock_get = cls.get_patcher.start()

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Tears down the class-level fixtures after all tests have run.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Tests the `public_repos` method in an integration context.
        """
        client = GithubOrgClient(self.org_payload['login'])
        repos = client.public_repos()
        self.assertEqual(repos, self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Tests the `public_repos` method with a license filter.
        """
        client = GithubOrgClient(self.org_payload['login'])
        repos = client.public_repos(license="apache-2.0")
        self.assertEqual(repos, self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
