#!/usr/bin/env python3
"""
Simple test for Botnoi API
"""

import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("BOTNOI_API_KEY")
BASE_URL = "https://voice.botnoi.ai"

print("=" * 60)
print("Botnoi API Simple Test")
print("=" * 60)
print(f"API Key: {API_KEY[:10]}...")
print(f"Base URL: {BASE_URL}")
print()

# Test 1: Translation (simpler test)
print("Test 1: Translation API")
print("-" * 60)

try:
    with httpx.Client(timeout=30.0) as client:
        url = f"{BASE_URL}/translate"
        headers = {
            "botnoi-token": API_KEY,
            "Content-Type": "application/json"
        }
        payload = {
            "language": "en",
            "native_style": True,
            "simple_style": True,
            "text": "สวัสดีครับ"
        }
        
        print(f"POST {url}")
        print(f"Headers: {headers}")
        print(f"Payload: {payload}")
        print()
        
        response = client.post(url, headers=headers, json=payload)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text}")
        print()
        
        if response.status_code == 200:
            print("✅ Translation API works!")
        else:
            print(f"❌ Translation API failed: {response.status_code}")
            
except Exception as e:
    print(f"❌ Error: {str(e)}")

print()

# Test 2: Transcription
print("Test 2: Transcription API")
print("-" * 60)

# Find a test MP3 file
upload_dir = Path("backend/uploads")
mp3_files = list(upload_dir.glob("*.mp3"))

if not mp3_files:
    print("⚠️  No MP3 files found in backend/uploads")
    print("   Please upload a video first to test transcription")
else:
    test_file = mp3_files[0]
    print(f"Test file: {test_file}")
    print()
    
    try:
        with httpx.Client(timeout=300.0) as client:
            url = f"{BASE_URL}/gensub_upload"
            headers = {
                "botnoi-token": API_KEY
            }
            
            with open(test_file, "rb") as f:
                files = {
                    "audio_file": (test_file.name, f, "audio/mpeg")
                }
                data = {
                    "max_duration": "10",
                    "max_silence": "0.3",
                    "language": "th",
                    "srt": "yes"
                }
                
                print(f"POST {url}")
                print(f"Headers: {headers}")
                print(f"Data: {data}")
                print(f"File: {test_file.name}")
                print()
                
                response = client.post(url, headers=headers, files=files, data=data)
                
                print(f"Status: {response.status_code}")
                print(f"Response: {response.text[:500]}...")
                print()
                
                if response.status_code == 200:
                    print("✅ Transcription API works!")
                else:
                    print(f"❌ Transcription API failed: {response.status_code}")
                    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print()
print("=" * 60)
print("Test Complete")
print("=" * 60)
