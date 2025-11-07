#!/usr/bin/env python3
"""
Simple test script to verify the setup
"""

import sys
import os
from pathlib import Path

def test_python_imports():
    """Test if all required Python packages can be imported"""
    print("🐍 Testing Python imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError:
        print("❌ FastAPI not found")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except ImportError:
        print("❌ OpenAI not found")
        return False
    
    try:
        import moviepy
        print("✅ MoviePy imported successfully")
    except ImportError:
        print("❌ MoviePy not found")
        return False
    
    return True

def test_env_file():
    """Test if .env file exists"""
    print("\n📝 Testing environment setup...")
    
    env_path = Path(".env")
    if env_path.exists():
        print("✅ .env file found")
        
        # Check if OpenAI API key is set
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your_openai_api_key_here":
            print("✅ OpenAI API key is configured")
            return True
        else:
            print("⚠️  OpenAI API key not configured properly")
            return False
    else:
        print("❌ .env file not found")
        return False

def test_directory_structure():
    """Test if all required directories exist"""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        "backend",
        "backend/services",
        "backend/models",
        "frontend",
        "frontend/src",
        "frontend/src/components"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print(f"✅ {dir_path}")
        else:
            print(f"❌ {dir_path}")
            all_exist = False
    
    return all_exist

def main():
    print("🧪 Video Subtitle Generator - Setup Test\n")
    
    tests = [
        ("Directory Structure", test_directory_structure),
        ("Python Imports", test_python_imports),
        ("Environment File", test_env_file)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "="*50)
    print("📊 Test Results:")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 All tests passed! Your setup is ready.")
        print("\n📋 Next steps:")
        print("1. Make sure OpenAI API key is set in .env")
        print("2. Run: ./start-backend.sh")
        print("3. Run: ./start-frontend.sh")
    else:
        print("⚠️  Some tests failed. Please check the setup.")
        print("\n🔧 Try running: ./setup.sh")

if __name__ == "__main__":
    main()