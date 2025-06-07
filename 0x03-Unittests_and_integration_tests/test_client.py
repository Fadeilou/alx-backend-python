#!/usr/bin/env python3
"""
Module de tests pour client.py
"""
import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from parameterized import parameterized, parameterized_class
from typing import Dict
from client import GithubOrgClient
from fixtures import TEST_PAYLOAD


class TestGithubOrgClient(unittest.TestCase):
    """
    Classe de test pour la classe GithubOrgClient (tests unitaires).
    """

    # --- Tâche 4 ---
    @parameterized.expand([
        ("google",),
        ("abc",),
    ])
    @patch('client.get_json')
    def test_org(self, org_name: str, mock_get_json: MagicMock) -> None:
        """
        Teste que GithubOrgClient.org retourne la valeur correcte
        et que get_json est appelé une seule fois avec la bonne URL.
        """
        # Configure le mock pour retourner une valeur connue
        expected_payload = {"name": org_name, "id": 123}
        mock_get_json.return_value = expected_payload

        # Crée une instance de GithubOrgClient
        client = GithubOrgClient(org_name)

        # Appelle la méthode (qui est une propriété)
        result = client.org

        # Vérifie que get_json a été appelé avec l'URL attendue
        expected_url = f"https://api.github.com/orgs/{org_name}"
        mock_get_json.assert_called_once_with(expected_url)

        # Vérifie que le résultat est correct
        self.assertEqual(result, expected_payload)

    # --- Tâche 5 ---
    def test_public_repos_url(self) -> None:
        """
        Teste la propriété _public_repos_url en mockant la propriété 'org'.
        """
        # Payload de test pour le mock de 'org'
        known_payload = {"repos_url": "https://api.github.com/orgs/google/repos"}

        # Utilise patch.object avec PropertyMock pour mocker la propriété 'org'
        with patch.object(GithubOrgClient,
                          'org',
                          new_callable=PropertyMock) as mock_org:
            mock_org.return_value = known_payload
            client = GithubOrgClient("google")

            # Appelle la propriété _public_repos_url et vérifie le résultat
            result = client._public_repos_url
            self.assertEqual(result, known_payload["repos_url"])

    # --- Tâche 6 ---
    @patch('client.get_json')
    def test_public_repos(self, mock_get_json: MagicMock) -> None:
        """
        Teste la méthode public_repos en mockant get_json et _public_repos_url.
        """
        # Payload de test pour la liste des repos
        repos_payload = [
            {"name": "repo1", "license": {"key": "mit"}},
            {"name": "repo2", "license": {"key": "apache-2.0"}},
            {"name": "repo3", "license": {"key": "mit"}}
        ]
        mock_get_json.return_value = repos_payload

        # Mock de la propriété _public_repos_url
        with patch.object(GithubOrgClient,
                          '_public_repos_url',
                          new_callable=PropertyMock) as mock_public_repos_url:
            # Configure la valeur de retour du mock de la propriété
            mock_public_repos_url.return_value = "https://some.url/repos"
            client = GithubOrgClient("google")

            # Appelle la méthode à tester
            public_repos_list = client.public_repos()

            # Vérifie que la liste des noms de repos est correcte
            expected_repos = ["repo1", "repo2", "repo3"]
            self.assertEqual(public_repos_list, expected_repos)

            # Vérifie que les mocks ont été appelés une seule fois
            mock_public_repos_url.assert_called_once()
            mock_get_json.assert_called_once()

    # --- Tâche 7 ---
    @parameterized.expand([
        ({"license": {"key": "my_license"}}, "my_license", True),
        ({"license": {"key": "other_license"}}, "my_license", False),
    ])
    def test_has_license(self, repo: Dict, license_key: str, expected: bool) -> None:
        """
        Teste la méthode statique has_license avec différents inputs.
        """
        result = GithubOrgClient.has_license(repo, license_key)
        self.assertEqual(result, expected)


# --- Tâche 8 ---
@parameterized_class(
    ("org_payload", "repos_payload", "expected_repos", "apache2_repos"),
    TEST_PAYLOAD
)
class TestIntegrationGithubOrgClient(unittest.TestCase):
    """
    Classe de test d'intégration pour GithubOrgClient, en utilisant des fixtures.
    """
    @classmethod
    def setUpClass(cls) -> None:
        """
        Met en place le mock pour requests.get pour toute la classe de test.
        """
        # Fonction side_effect pour retourner des payloads différents selon l'URL
        def get_side_effect(url):
            mock_response = Mock()
            if url == "https://api.github.com/orgs/google":
                mock_response.json.return_value = cls.org_payload
            elif url == "https://api.github.com/orgs/google/repos":
                mock_response.json.return_value = cls.repos_payload
            else:
                # Retourne une réponse 404 pour les autres URLs non prévues
                mock_response.status_code = 404
            return mock_response

        # Démarre le patcher pour requests.get
        cls.get_patcher = patch('requests.get')
        cls.mock_get = cls.get_patcher.start()
        cls.mock_get.side_effect = get_side_effect

    @classmethod
    def tearDownClass(cls) -> None:
        """
        Arrête le patcher après que tous les tests de la classe soient terminés.
        """
        cls.get_patcher.stop()

    def test_public_repos(self) -> None:
        """
        Teste la méthode public_repos dans un contexte d'intégration.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos(), self.expected_repos)

    def test_public_repos_with_license(self) -> None:
        """
        Teste la méthode public_repos avec un filtre de licence.
        """
        client = GithubOrgClient("google")
        self.assertEqual(client.public_repos("apache-2.0"), self.apache2_repos)


if __name__ == '__main__':
    unittest.main()
