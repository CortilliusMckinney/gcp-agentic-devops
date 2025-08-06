import unittest
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import NotFound

from agents import secrets_manager

class TestSecretsManager(unittest.TestCase):
    @patch("agents.secrets_manager.secretmanager.SecretManagerServiceClient")
    def test_get_secret_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.return_value.payload.data.decode.return_value = "test-secret"

        result = secrets_manager.get_secret("my-secret", "test-project")
        self.assertEqual(result, "test-secret")
        mock_client.access_secret_version.assert_called_once()

    @patch("agents.secrets_manager.secretmanager.SecretManagerServiceClient")
    def test_get_secret_not_found(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.side_effect = NotFound("Secret not found")

        with self.assertRaises(NotFound):
            secrets_manager.get_secret("missing-secret", "test-project")

if __name__ == "__main__":
    unittest.main() 