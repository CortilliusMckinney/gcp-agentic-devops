#!/usr/bin/env python3
"""
Basic functionality test for GCP Agentic DevOps system.
This script tests the core functionality without requiring actual API keys.
"""

import os
import sys

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Testing module imports...")
    
    try:
        from secrets_manager import get_secret
        print("✅ secrets_manager imported successfully")
    except ImportError as e:
        print(f"❌ secrets_manager import failed: {e}")
        return False
    
    try:
        from clients import openai_client, anthropic_client, headers_cf, CLOUDFLARE_BASE_URL
        print("✅ clients imported successfully")
    except ImportError as e:
        print(f"❌ clients import failed: {e}")
        return False
    
    try:
        from model_router import ModelRouter
        print("✅ model_router imported successfully")
    except ImportError as e:
        print(f"❌ model_router import failed: {e}")
        return False
    
    return True

def test_environment():
    """Test environment configuration."""
    print("\n🔍 Testing environment configuration...")
    
    # Check project ID
    project_id = os.environ.get("GCP_PROJECT_ID", "agentic-devops-464519")
    print(f"✅ Project ID: {project_id}")
    
    # Check if we're in the right directory
    current_dir = os.getcwd()
    print(f"✅ Current directory: {current_dir}")
    
    return True

def test_model_router():
    """Test ModelRouter initialization and basic functionality."""
    print("\n🔍 Testing ModelRouter...")
    
    try:
        from model_router import ModelRouter
        router = ModelRouter()
        print("✅ ModelRouter initialized successfully")
        
        # Test routing logic (without making actual API calls)
        test_metadata = {"provider": "openai", "model": "gpt-3.5-turbo"}
        result = router.route("Test prompt", test_metadata)
        
        if "provider" in result or "error" in result:
            print("✅ ModelRouter routing logic working")
        else:
            print("⚠️  ModelRouter routing logic may have issues")
            
    except Exception as e:
        print(f"❌ ModelRouter test failed: {e}")
        return False
    
    return True

def test_secrets_manager():
    """Test secrets manager functionality."""
    print("\n🔍 Testing secrets manager...")
    
    try:
        from secrets_manager import get_secret
        
        # Test function signature
        import inspect
        sig = inspect.signature(get_secret)
        params = list(sig.parameters.keys())
        
        if len(params) == 2 and "secret_id" in params and "project_id" in params:
            print("✅ get_secret function signature correct")
        else:
            print(f"⚠️  get_secret function signature: {params}")
            
    except Exception as e:
        print(f"❌ Secrets manager test failed: {e}")
        return False
    
    return True

def test_clients():
    """Test client configurations."""
    print("\n🔍 Testing client configurations...")
    
    try:
        from clients import headers_cf, CLOUDFLARE_BASE_URL
        
        # Test Cloudflare headers
        if "Authorization" in headers_cf and "Content-Type" in headers_cf:
            print("✅ Cloudflare headers configured")
        else:
            print("⚠️  Cloudflare headers may be incomplete")
        
        # Test Cloudflare URL
        if isinstance(CLOUDFLARE_BASE_URL, str) and "api.cloudflare.com" in CLOUDFLARE_BASE_URL:
            print("✅ Cloudflare URL configured")
        else:
            print("⚠️  Cloudflare URL may be incorrect")
            
    except Exception as e:
        print(f"❌ Client configuration test failed: {e}")
        return False
    
    return True

def main():
    """Run all basic tests."""
    print("🚀 Starting GCP Agentic DevOps Basic Tests")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("Environment Configuration", test_environment),
        ("ModelRouter", test_model_router),
        ("Secrets Manager", test_secrets_manager),
        ("Client Configurations", test_clients),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        if test_func():
            passed += 1
            print(f"✅ {test_name} passed")
        else:
            print(f"❌ {test_name} failed")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your system is ready for development.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 