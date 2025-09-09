import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import unittest
from unittest.mock import patch, MagicMock
from google.api_core.exceptions import NotFound


from agents.secrets_manager import get_secret

class TestSecretsManager(unittest.TestCase):
    @patch("secrets_manager.secretmanager.SecretManagerServiceClient")
    def test_get_secret_success(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.return_value.payload.data.decode.return_value = "test-secret"

        result = get_secret("my-secret", "test-project")
        self.assertEqual(result, "test-secret")
        mock_client.access_secret_version.assert_called_once()

    @patch("secrets_manager.secretmanager.SecretManagerServiceClient")
    def test_get_secret_not_found(self, mock_client_class):
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.side_effect = NotFound("Secret not found")

        with self.assertRaises(NotFound):
            get_secret("missing-secret", "test-project")

if __name__ == "__main__":
    unittest.main() 