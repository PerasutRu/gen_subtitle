#!/usr/bin/env python3
"""
Test script for Botnoi Gensub API integration
"""

import os
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from services.botnoi_service import BotnoiService

async def test_botnoi_connection():
    """Test basic Botnoi API connection"""
    print("🔍 Testing Botnoi API connection...")
    
    try:
        service = BotnoiService()
        print("✅ Botnoi service initialized successfully")
        print(f"   API Key: {service.api_key[:10]}...")
        return True
    except ValueError as e:
        print(f"❌ Failed to initialize Botnoi service: {e}")
        print("   Please set BOTNOI_API_KEY in .env file")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_botnoi_translation():
    """Test Botnoi translation API"""
    print("\n🔍 Testing Botnoi translation...")
    
    try:
        service = BotnoiService()
        
        # Test translation
        test_text = "สวัสดีครับ ยินดีต้อนรับ"
        print(f"   Original text: {test_text}")
        
        translated = await service.translate_text(test_text, "english")
        print(f"   Translated text: {translated}")
        print("✅ Translation test passed")
        return True
        
    except Exception as e:
        print(f"❌ Translation test failed: {e}")
        return False

async def test_botnoi_transcription():
    """Test Botnoi transcription API (requires audio file)"""
    print("\n🔍 Testing Botnoi transcription...")
    
    # Look for test audio file
    test_audio_paths = [
        Path("backend/uploads").glob("*.mp3"),
        Path("test_audio.mp3"),
    ]
    
    audio_file = None
    for path_pattern in test_audio_paths:
        if isinstance(path_pattern, Path):
            if path_pattern.exists():
                audio_file = path_pattern
                break
        else:
            files = list(path_pattern)
            if files:
                audio_file = files[0]
                break
    
    if not audio_file:
        print("⚠️  No test audio file found")
        print("   To test transcription, place an MP3 file in backend/uploads/")
        return None
    
    try:
        service = BotnoiService()
        print(f"   Using audio file: {audio_file}")
        
        result = await service.transcribe_with_timestamps(audio_file)
        
        print(f"   Transcribed text: {result.text[:100]}...")
        print(f"   Number of segments: {len(result.segments)}")
        print(f"   Language: {result.language}")
        print("✅ Transcription test passed")
        return True
        
    except Exception as e:
        print(f"❌ Transcription test failed: {e}")
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("Botnoi Gensub API Test Suite")
    print("=" * 60)
    
    results = []
    
    # Test 1: Connection
    result = await test_botnoi_connection()
    results.append(("Connection", result))
    
    if not result:
        print("\n❌ Cannot proceed without valid API key")
        return
    
    # Test 2: Translation
    result = await test_botnoi_translation()
    results.append(("Translation", result))
    
    # Test 3: Transcription (optional)
    result = await test_botnoi_transcription()
    if result is not None:
        results.append(("Transcription", result))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for test_name, test_result in results:
        status = "✅ PASSED" if test_result else "❌ FAILED"
        print(f"{test_name:20s}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())
