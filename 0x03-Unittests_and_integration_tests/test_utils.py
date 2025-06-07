```python
#!/usr/bin/env python3
"""
Module de tests pour utils.py
"""
import unittest
from unittest.mock import patch, Mock
from parameterized import parameterized
from typing import Mapping, Sequence, Dict, Any
from utils import access_nested_map, get_json, memoize


class TestAccessNestedMap(unittest.TestCase):
    """
    Classe de test pour la fonction access_nested_map.
    """

    # --- Tâche 0 ---
    @parameterized.expand([
        ({"a": 1}, ("a",), 1),
        ({"a": {"b": 2}}, ("a",), {"b": 2}),
        ({"a": {"b": 2}}, ("a", "b"), 2),
    ])
    def test_access_nested_map(
        self,
        nested_map: Mapping,
        path: Sequence,
        expected: Any
    ) -> None:
        """
        Teste que access_nested_map retourne le résultat attendu.
        """
        self.assertEqual(access_nested_map(nested_map, path), expected)

    # --- Tâche 1 ---
    @parameterized.expand([
        ({}, ("a",), 'a'),
        ({"a": 1}, ("a", "b"), 'b')
    ])
    def test_access_nested_map_exception(
        self,
        nested_map: Mapping,
        path: Sequence,
        expected_key: str
    ) -> None:
        """
        Teste que access_nested_map lève une KeyError pour des chemins invalides.
        """
        with self.assertRaises(KeyError) as cm:
            access_nested_map(nested_map, path)
        # Vérifie que le message de l'exception est la clé manquante
        self.assertEqual(str(cm.exception), f"'{expected_key}'")


class TestGetJson(unittest.TestCase):
    """
    Classe de test pour la fonction get_json.
    """

    # --- Tâche 2 ---
    @parameterized.expand([
        ("http://example.com", {"payload": True}),
        ("http://holberton.io", {"payload": False}),
    ])
    def test_get_json(self, test_url: str, test_payload: Dict) -> None:
        """
        Teste que get_json retourne le payload JSON attendu
        sans faire de véritables appels HTTP.
        """
        # Crée un mock pour la réponse de requests.get
        mock_response = Mock()
        mock_response.json.return_value = test_payload

        # Utilise patch pour remplacer requests.get
        with patch('requests.get', return_value=mock_response) as mock_get:
            # Appelle la fonction à tester
            result = get_json(test_url)

            # Vérifie que la méthode mockée a été appelée une fois avec la bonne URL
            mock_get.assert_called_once_with(test_url)

            # Vérifie que le résultat de get_json est le payload de test
            self.assertEqual(result, test_payload)


class TestMemoize(unittest.TestCase):
    """
    Classe de test pour le décorateur memoize.
    """

    # --- Tâche 3 ---
    def test_memoize(self) -> None:
        """
        Teste que le décorateur memoize met en cache le résultat
        d'une méthode, la transformant en propriété.
        """

        class TestClass:
            """Classe de test interne pour memoize."""

            def a_method(self) -> int:
                """Une méthode simple qui retourne 42."""
                return 42

            @memoize
            def a_property(self) -> int:
                """
                Une propriété qui utilise memoize pour appeler a_method.
                """
                return self.a_method()

        # Utilise patch.object pour mocker la méthode 'a_method'
        with patch.object(TestClass,
                          'a_method',
                          return_value=42) as mock_a_method:
            test_instance = TestClass()

            # Appelle la propriété deux fois
            result1 = test_instance.a_property
            result2 = test_instance.a_property

            # Vérifie que le résultat est correct
            self.assertEqual(result1, 42)
            self.assertEqual(result2, 42)

            # Vérifie que la méthode sous-jacente n'a été appelée qu'une seule fois
            mock_a_method.assert_called_once()


if __name__ == '__main__':
    unittest.main()
