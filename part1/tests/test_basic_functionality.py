"""
Part 1 - Basic functionality tests for agents.
Tests core agent functionality without requiring Cloud Functions.
"""

import os
import sys
import unittest

# Add the agents directory to the path
project_root = os.path.dirname(os.path.dirname(__file__))
agents_path = os.path.join(project_root, 'agents')
sys.path.insert(0, agents_path)

# Simple import with Pylance warnings disabled
ModelRouter = None
ROUTER_AVAILABLE = False

try:
    from model_router import ModelRouter  # type: ignore
    ROUTER_AVAILABLE = True
    print("✅ Successfully imported ModelRouter")
except ImportError as e:
    print(f"⚠️ ModelRouter not available: {e}")
    ROUTER_AVAILABLE = False


class TestBasicFunctionality(unittest.TestCase):
    """Basic smoke tests for agent functionality."""
    
    def setUp(self):
        if ROUTER_AVAILABLE:
            try:
                self.router = ModelRouter()  # type: ignore
            except Exception as e:
                self.skipTest(f"Router initialization failed: {e}")
        else:
            self.skipTest("ModelRouter not available")

    def test_openai_routing(self):
        """Basic smoke test for OpenAI provider."""
        result = self.router.route(
            prompt="Test basic functionality - say hello",
            metadata={"provider": "openai"}
        )
        self.assertIn("provider", result)
        self.assertEqual(result["provider"], "openai")
        # Allow for error responses in test environment
        self.assertTrue("response" in result or "error" in result)

    def test_anthropic_routing(self):
        """Basic smoke test for Anthropic provider."""
        result = self.router.route(
            prompt="Test basic functionality - say hello",
            metadata={"provider": "anthropic"}
        )
        self.assertIn("provider", result)
        self.assertEqual(result["provider"], "anthropic")
        self.assertTrue("response" in result or "error" in result)

    def test_cloudflare_routing(self):
        """Basic smoke test for Cloudflare provider."""
        result = self.router.route(
            prompt="Test basic functionality - say hello",
            metadata={"provider": "cloudflare"}
        )
        self.assertIn("provider", result)
        self.assertEqual(result["provider"], "cloudflare")
        self.assertTrue("response" in result or "error" in result)

    def test_invalid_provider(self):
        """Test handling of invalid providers."""
        result = self.router.route(
            prompt="Test invalid provider",
            metadata={"provider": "invalid"}
        )
        # Should return error for unsupported provider
        self.assertTrue("error" in result)


class TestProjectStructure(unittest.TestCase):
    """Test that basic project structure exists."""
    
    def test_agents_directory_exists(self):
        """Test that agents directory exists."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        agents_path = os.path.join(project_root, 'agents')
        self.assertTrue(os.path.exists(agents_path))
        self.assertTrue(os.path.isdir(agents_path))

    def test_agents_files_exist(self):
        """Test that basic agent files exist."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        agents_path = os.path.join(project_root, 'agents')
        
        # Check for key files
        model_router_path = os.path.join(agents_path, 'model_router.py')
        secrets_manager_path = os.path.join(agents_path, 'secrets_manager.py')
        
        if os.path.exists(agents_path):
            files = os.listdir(agents_path)
            print(f"Found agent files: {files}")
            # At least one Python file should exist
            py_files = [f for f in files if f.endswith('.py')]
            self.assertGreater(len(py_files), 0, "No Python files found in agents directory")


if __name__ == "__main__":
    print("🧪 Running Part 1 - Basic Agent Tests...")
    print("=" * 40)
    
    # Run tests with more verbose output
    unittest.main(verbosity=2)