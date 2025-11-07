#!/usr/bin/env python3
"""
Test script to verify OpenAI API connectivity and model availability
"""

import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_openai_connection():
    """Test basic OpenAI API connection"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("❌ OPENAI_API_KEY not found in environment")
            return False
        
        client = OpenAI(api_key=api_key)
        print("✅ OpenAI client initialized successfully")
        
        # Test with a simple chat completion
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=10
        )
        print("✅ OpenAI API connection working")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI API test failed: {str(e)}")
        return False

def test_transcription_models():
    """Test available transcription models"""
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        
        # Check if we have any audio files to test with
        upload_dir = Path("uploads")
        if not upload_dir.exists():
            print("⚠️  No uploads directory found, cannot test transcription")
            return False
        
        mp3_files = list(upload_dir.glob("*.mp3"))
        if not mp3_files:
            print("⚠️  No MP3 files found in uploads directory")
            return False
        
        test_file = mp3_files[0]
        print(f"📁 Testing with file: {test_file}")
        print(f"📊 File size: {test_file.stat().st_size} bytes")
        
        # Test gpt-4o-mini-transcribe
        try:
            with open(test_file, "rb") as audio_file:
                print("🧪 Testing gpt-4o-mini-transcribe...")
                response = client.audio.transcriptions.create(
                    model="gpt-4o-mini-transcribe",
                    file=audio_file,
                    response_format="text"
                )
                print("✅ gpt-4o-mini-transcribe works!")
                print(f"📝 Sample output: {response[:100]}...")
                return True
        except Exception as e:
            print(f"❌ gpt-4o-mini-transcribe failed: {str(e)}")
        
        # Test whisper-1 as fallback
        try:
            with open(test_file, "rb") as audio_file:
                print("🧪 Testing whisper-1...")
                response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
                print("✅ whisper-1 works!")
                print(f"📝 Sample output: {response[:100]}...")
                return True
        except Exception as e:
            print(f"❌ whisper-1 failed: {str(e)}")
        
        return False
        
    except Exception as e:
        print(f"❌ Transcription test failed: {str(e)}")
        return False

def main():
    print("🧪 OpenAI API Test\n")
    
    print("1. Testing OpenAI connection...")
    connection_ok = test_openai_connection()
    
    print("\n2. Testing transcription models...")
    if connection_ok:
        transcription_ok = test_transcription_models()
    else:
        print("⏭️  Skipping transcription test due to connection failure")
        transcription_ok = False
    
    print("\n" + "="*50)
    print("📊 Test Summary:")
    print("="*50)
    print(f"OpenAI Connection: {'✅ PASS' if connection_ok else '❌ FAIL'}")
    print(f"Transcription: {'✅ PASS' if transcription_ok else '❌ FAIL'}")
    
    if connection_ok and transcription_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n⚠️  Some tests failed. Check the logs above.")

if __name__ == "__main__":
    main()