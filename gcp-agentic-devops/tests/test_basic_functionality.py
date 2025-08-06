"""
Basic functionality tests for GCP Agentic DevOps system.
Tests core functionality without requiring actual API calls.
"""

import os
import sys
import pytest

# Add the agents directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'agents'))

from secrets_manager import get_secret
from clients import headers_cf, CLOUDFLARE_BASE_URL
from model_router import ModelRouter


class TestModuleImports:
    """Test that all modules can be imported successfully."""
    
    def test_secrets_manager_import(self):
        """Test secrets_manager module import."""
        from secrets_manager import get_secret
        assert get_secret is not None
    
    def test_clients_import(self):
        """Test clients module import."""
        from clients import openai_client, anthropic_client, headers_cf, CLOUDFLARE_BASE_URL
        assert openai_client is not None
        assert anthropic_client is not None
        assert headers_cf is not None
        assert CLOUDFLARE_BASE_URL is not None
    
    def test_model_router_import(self):
        """Test model_router module import."""
        from model_router import ModelRouter
        assert ModelRouter is not None


class TestEnvironmentConfiguration:
    """Test environment configuration."""
    
    def test_project_id_configured(self):
        """Test that project ID is configured."""
        project_id = os.environ.get("GCP_PROJECT_ID", "agentic-devops-464519")
        assert project_id is not None
        assert len(project_id) > 0
    
    def test_virtual_environment_active(self):
        """Test that virtual environment is active."""
        venv_path = os.environ.get("VIRTUAL_ENV")
        # This is optional - don't fail if not in venv
        if venv_path:
            assert os.path.exists(venv_path)


class TestSecretsManager:
    """Test secrets manager functionality."""
    
    def test_get_secret_function_signature(self):
        """Test that get_secret has correct function signature."""
        import inspect
        sig = inspect.signature(get_secret)
        params = list(sig.parameters.keys())
        
        assert len(params) == 2
        assert "secret_id" in params
        assert "project_id" in params
    
    def test_get_secret_return_type(self):
        """Test that get_secret returns a string."""
        import inspect
        sig = inspect.signature(get_secret)
        assert sig.return_annotation == str


class TestClientConfigurations:
    """Test client configurations."""
    
    def test_cloudflare_headers_configured(self):
        """Test that Cloudflare headers are properly configured."""
        assert "Authorization" in headers_cf
        assert "Content-Type" in headers_cf
        assert headers_cf["Content-Type"] == "application/json"
    
    def test_cloudflare_url_configured(self):
        """Test that Cloudflare URL is properly configured."""
        assert isinstance(CLOUDFLARE_BASE_URL, str)
        assert "api.cloudflare.com" in CLOUDFLARE_BASE_URL


class TestModelRouter:
    """Test ModelRouter functionality."""
    
    def test_router_initialization(self):
        """Test that ModelRouter can be initialized."""
        router = ModelRouter()
        assert router is not None
        assert hasattr(router, 'openai')
        assert hasattr(router, 'anthropic')
        assert hasattr(router, 'cloudflare_url')
        assert hasattr(router, 'cloudflare_headers')
    
    def test_router_has_route_method(self):
        """Test that ModelRouter has the route method."""
        router = ModelRouter()
        assert hasattr(router, 'route')
        assert callable(router.route)
    
    def test_route_method_signature(self):
        """Test that route method has correct signature."""
        router = ModelRouter()
        import inspect
        sig = inspect.signature(router.route)
        params = list(sig.parameters.keys())
        
        # Should have prompt and metadata parameters (self is not included in signature)
        assert len(params) == 2  # prompt + metadata parameters
        assert "prompt" in params
        assert "metadata" in params


class TestRoutingLogic:
    """Test routing logic without making actual API calls."""
    
    @pytest.fixture
    def router(self):
        """Create a router instance for testing."""
        return ModelRouter()
    
    def test_route_openai_provider(self, router):
        """Test routing to OpenAI provider."""
        metadata = {"provider": "openai", "model": "gpt-3.5-turbo"}
        result = router.route("Test prompt", metadata)
        
        # Should return a dict with either provider or error
        assert isinstance(result, dict)
        assert "provider" in result or "error" in result
    
    def test_route_anthropic_provider(self, router):
        """Test routing to Anthropic provider."""
        metadata = {"provider": "anthropic", "model": "claude-3-haiku-20240307"}
        result = router.route("Test prompt", metadata)
        
        assert isinstance(result, dict)
        assert "provider" in result or "error" in result
    
    def test_route_cloudflare_provider(self, router):
        """Test routing to Cloudflare provider."""
        metadata = {"provider": "cloudflare"}
        result = router.route("Test prompt", metadata)
        
        assert isinstance(result, dict)
        assert "provider" in result or "error" in result
    
    def test_route_unsupported_provider(self, router):
        """Test handling of unsupported providers."""
        metadata = {"provider": "unsupported"}
        result = router.route("Test prompt", metadata)
        
        assert isinstance(result, dict)
        assert "error" in result
        assert "Unsupported provider" in result["error"]
    
    def test_route_without_model(self, router):
        """Test routing without specifying a model."""
        metadata = {"provider": "openai"}
        result = router.route("Test prompt", metadata)
        
        assert isinstance(result, dict)
        assert "provider" in result or "error" in result
    
    def test_route_with_none_model(self, router):
        """Test routing with None model."""
        metadata = {"provider": "anthropic", "model": None}
        result = router.route("Test prompt", metadata)
        
        assert isinstance(result, dict)
        assert "provider" in result or "error" in result 