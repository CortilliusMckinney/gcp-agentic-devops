#!/usr/bin/env python3
"""
Test runner for GCP Agentic DevOps system.
Runs all tests with pytest and provides a summary.
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with pytest."""
    print("🧪 Running GCP Agentic DevOps Test Suite")
    print("=" * 50)
    
    # Change to the agents directory to ensure proper imports
    agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
    os.chdir(agents_dir)
    
    # Run pytest
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            '../tests/', 
            '-v', 
            '--tb=short',
            '--disable-warnings'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("\n🎉 All tests passed!")
            return True
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_basic_tests():
    """Run basic functionality tests only."""
    print("🧪 Running Basic Tests Only")
    print("=" * 30)
    
    agents_dir = os.path.join(os.path.dirname(__file__), 'agents')
    os.chdir(agents_dir)
    
    try:
        result = subprocess.run([
            sys.executable, '-m', 'pytest', 
            '../tests/test_basic_functionality.py', 
            '-v', 
            '--tb=short',
            '--disable-warnings'
        ], capture_output=True, text=True)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n✅ Basic tests passed!")
            return True
        else:
            print(f"\n❌ Basic tests failed (exit code: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ Error running basic tests: {e}")
        return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run GCP Agentic DevOps tests")
    parser.add_argument(
        "--basic", 
        action="store_true", 
        help="Run only basic functionality tests"
    )
    
    args = parser.parse_args()
    
    if args.basic:
        success = run_basic_tests()
    else:
        success = run_tests()
    
    sys.exit(0 if success else 1) 