#!/usr/bin/env python3
"""
Test script to verify custom limits are working
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_login():
    """Test login"""
    print("1. Testing login...")
    response = requests.post(
        f"{API_URL}/auth/login",
        json={"username": "test1", "password": "test123"}
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data["access_token"]
        print(f"   ✅ Login successful")
        return token
    else:
        print(f"   ❌ Login failed: {response.status_code}")
        return None

def test_get_session(token):
    """Test get user session"""
    print("\n2. Testing /user/session...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/user/session", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Session retrieved")
        print(f"   Session ID: {data['session_id']}")
        print(f"   Username: {data['username']}")
        print(f"   Limits: {json.dumps(data['limits'], indent=2)}")
        return data
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

def test_get_user_limits(token, username):
    """Test get user limits (admin endpoint)"""
    print(f"\n3. Testing /admin/user/{username}/limits...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{API_URL}/admin/user/{username}/limits", headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ User limits retrieved")
        print(f"   Custom limits: {json.dumps(data.get('custom_limits'), indent=2)}")
        print(f"   Active limits: {json.dumps(data.get('active_limits'), indent=2)}")
        return data
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        return None

if __name__ == "__main__":
    print("=" * 60)
    print("Testing Custom Limits Feature")
    print("=" * 60)
    
    # Test with test1 user (has custom limits)
    token = test_login()
    if token:
        session_data = test_get_session(token)
        
        # Check if limits match custom_limits
        if session_data:
            limits = session_data['limits']
            print("\n" + "=" * 60)
            print("RESULT:")
            if limits.get('maxVideos') == 2:
                print("✅ Custom limits are being used!")
                print(f"   maxVideos: {limits['maxVideos']} (expected: 2)")
            else:
                print("❌ Default limits are being used (should be custom)")
                print(f"   maxVideos: {limits.get('maxVideos')} (expected: 2)")
            print("=" * 60)
    
    print("\nTest completed!")
