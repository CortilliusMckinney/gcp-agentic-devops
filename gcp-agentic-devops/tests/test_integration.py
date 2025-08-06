"""
Integration tests for GCP Agentic DevOps system.
Tests complete workflows with mocked API calls.
"""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Add the agents directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from secrets_manager import get_secret
from model_router import ModelRouter


class TestSecretsManagerIntegration:
    """Integration tests for secrets manager."""
    
    @patch('secrets_manager.secretmanager.SecretManagerServiceClient')
    def test_get_secret_success(self, mock_client_class):
        """Test successful secret retrieval."""
        # Setup mock
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_response = MagicMock()
        mock_response.payload.data.decode.return_value = "test-secret-value"
        mock_client.access_secret_version.return_value = mock_response
        
        # Test
        result = get_secret("test-secret", "test-project")
        
        # Assertions
        assert result == "test-secret-value"
        mock_client.access_secret_version.assert_called_once()
    
    @patch('secrets_manager.secretmanager.SecretManagerServiceClient')
    def test_get_secret_not_found(self, mock_client_class):
        """Test handling of missing secrets."""
        from google.api_core.exceptions import NotFound
        
        # Setup mock to raise exception
        mock_client = MagicMock()
        mock_client_class.return_value = mock_client
        mock_client.access_secret_version.side_effect = NotFound("Secret not found")
        
        # Test
        with pytest.raises(NotFound):
            get_secret("missing-secret", "test-project")


class TestClientsIntegration:
    """Integration tests for API clients."""
    
    def test_openai_client_initialized(self):
        """Test that OpenAI client is properly initialized."""
        from clients import openai_client
        assert openai_client is not None
        assert hasattr(openai_client, 'api_key')
    
    def test_anthropic_client_initialized(self):
        """Test that Anthropic client is properly initialized."""
        from clients import anthropic_client
        assert anthropic_client is not None
        assert hasattr(anthropic_client, 'api_key')
    
    def test_cloudflare_headers_configured(self):
        """Test that Cloudflare headers are properly configured."""
        from clients import headers_cf
        assert "Authorization" in headers_cf
        assert "Content-Type" in headers_cf
        assert headers_cf["Content-Type"] == "application/json"
    
    def test_cloudflare_url_configured(self):
        """Test that Cloudflare URL is properly configured."""
        from clients import CLOUDFLARE_BASE_URL
        assert isinstance(CLOUDFLARE_BASE_URL, str)
        assert "api.cloudflare.com" in CLOUDFLARE_BASE_URL


class TestModelRouterIntegration:
    """Integration tests for ModelRouter."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return ModelRouter()
    
    def test_router_initialization(self, router):
        """Test that router is properly initialized."""
        assert router is not None
        assert hasattr(router, 'openai')
        assert hasattr(router, 'anthropic')
        assert hasattr(router, 'cloudflare_url')
        assert hasattr(router, 'cloudflare_headers')
    
    @patch('agents.clients.openai_client')
    def test_openai_routing(self, mock_openai, router):
        """Test OpenAI routing with mocked client."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Hello from OpenAI!"
        mock_openai.chat.completions.create.return_value = mock_response
        
        # Test
        result = router.call_openai("Test prompt", "gpt-3.5-turbo")
        
        # Assertions
        assert result["provider"] == "openai"
        assert result["response"] == "Hello from OpenAI!"
        assert "raw" in result
    
    @patch('agents.clients.anthropic_client')
    def test_anthropic_routing(self, mock_anthropic, router):
        """Test Anthropic routing with mocked client."""
        # Setup mock response
        mock_response = MagicMock()
        mock_content = MagicMock()
        # Use a simple string representation
        mock_content.__str__ = MagicMock(return_value="Hello from Anthropic!")
        mock_response.content = [mock_content]
        mock_anthropic.messages.create.return_value = mock_response
        
        # Test
        result = router.call_anthropic("Test prompt", "claude-3-haiku-20240307")
        
        # Assertions
        assert result["provider"] == "anthropic"
        assert result["response"] == "Hello from Anthropic!"
        assert "raw" in result
    
    @patch('agents.model_router.requests.post')
    def test_cloudflare_routing(self, mock_post, router):
        """Test Cloudflare routing with mocked requests."""
        # Setup mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"response": "Hello from Cloudflare!"}
        }
        mock_post.return_value = mock_response
        
        # Test
        result = router.call_cloudflare("Test prompt")
        
        # Assertions
        assert result["provider"] == "cloudflare"
        assert result["response"] == "Hello from Cloudflare!"
        assert "raw" in result
    
    def test_unsupported_provider(self, router):
        """Test handling of unsupported providers."""
        result = router.route("Test prompt", {"provider": "unsupported"})
        
        assert "error" in result
        assert "Unsupported provider" in result["error"]


class TestEndToEndWorkflow:
    """End-to-end workflow tests."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return ModelRouter()
    
    @patch('agents.clients.openai_client')
    @patch('agents.clients.anthropic_client')
    def test_full_workflow_openai(self, mock_anthropic, mock_openai, router):
        """Test complete workflow with OpenAI."""
        # Setup OpenAI mock
        mock_openai_response = MagicMock()
        mock_openai_response.choices = [MagicMock()]
        mock_openai_response.choices[0].message.content = "Hello from OpenAI!"
        mock_openai.chat.completions.create.return_value = mock_openai_response
        
        # Test
        result = router.route("Test prompt", {"provider": "openai", "model": "gpt-3.5-turbo"})
        
        # Assertions
        assert result["provider"] == "openai"
        assert result["response"] == "Hello from OpenAI!"
    
    @patch('agents.clients.openai_client')
    @patch('agents.clients.anthropic_client')
    def test_full_workflow_anthropic(self, mock_anthropic, mock_openai, router):
        """Test complete workflow with Anthropic."""
        # Setup Anthropic mock
        mock_anthropic_response = MagicMock()
        mock_content = MagicMock()
        # Use a simple string representation
        mock_content.__str__ = MagicMock(return_value="Hello from Anthropic!")
        mock_anthropic_response.content = [mock_content]
        mock_anthropic.messages.create.return_value = mock_anthropic_response
        
        # Test
        result = router.route("Test prompt", {"provider": "anthropic", "model": "claude-3-haiku-20240307"})
        
        # Assertions
        assert result["provider"] == "anthropic"
        assert result["response"] == "Hello from Anthropic!"
    
    @patch('agents.model_router.requests.post')
    def test_full_workflow_cloudflare(self, mock_post, router):
        """Test complete workflow with Cloudflare."""
        # Setup Cloudflare mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "result": {"response": "Hello from Cloudflare!"}
        }
        mock_post.return_value = mock_response
        
        # Test
        result = router.route("Test prompt", {"provider": "cloudflare"})
        
        # Assertions
        assert result["provider"] == "cloudflare"
        assert result["response"] == "Hello from Cloudflare!"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return ModelRouter()
    
    @patch('agents.clients.openai_client')
    def test_openai_error_handling(self, mock_openai, router):
        """Test OpenAI error handling."""
        # Setup mock to raise exception
        mock_openai.chat.completions.create.side_effect = Exception("OpenAI API error")
        
        # Test
        result = router.call_openai("Test prompt", "gpt-3.5-turbo")
        
        # Assertions
        assert "error" in result
        assert "OpenAI call failed" in result["error"]
    
    @patch('agents.clients.anthropic_client')
    def test_anthropic_error_handling(self, mock_anthropic, router):
        """Test Anthropic error handling."""
        # Setup mock to raise exception
        mock_anthropic.messages.create.side_effect = Exception("Anthropic API error")
        
        # Test
        result = router.call_anthropic("Test prompt", "claude-3-haiku-20240307")
        
        # Assertions
        assert "error" in result
        assert "Anthropic call failed" in result["error"]
    
    @patch('agents.model_router.requests.post')
    def test_cloudflare_error_handling(self, mock_post, router):
        """Test Cloudflare error handling."""
        # Setup mock to raise exception
        mock_post.side_effect = Exception("Cloudflare API error")
        
        # Test
        result = router.call_cloudflare("Test prompt")
        
        # Assertions
        assert "error" in result
        assert "Cloudflare request error" in result["error"] 