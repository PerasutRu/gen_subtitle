#!/usr/bin/env python3
"""
Script สำหรับสร้าง user ใหม่
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def create_user(admin_username, admin_password, new_username, new_password, role="user"):
    """สร้าง user ใหม่"""
    
    # 1. Login as admin
    print(f"🔐 Logging in as {admin_username}...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": admin_username,
            "password": admin_password
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.json()}")
        return False
    
    admin_token = login_response.json()["access_token"]
    print("✅ Login successful!")
    
    # 2. Create new user
    print(f"\n👤 Creating user: {new_username}...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    register_response = requests.post(
        f"{BASE_URL}/admin/register",
        headers=headers,
        json={
            "username": new_username,
            "password": new_password,
            "role": role
        }
    )
    
    if register_response.status_code != 200:
        print(f"❌ Registration failed: {register_response.json()}")
        return False
    
    result = register_response.json()
    print(f"✅ {result['message']}")
    print(f"   Username: {result['username']}")
    print(f"   Role: {result['role']}")
    
    return True

def list_users(admin_username, admin_password):
    """แสดงรายการ users ทั้งหมด"""
    
    # Login as admin
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "username": admin_username,
            "password": admin_password
        }
    )
    
    if login_response.status_code != 200:
        print(f"❌ Login failed")
        return
    
    admin_token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {admin_token}"}
    
    # Get users
    users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
    
    if users_response.status_code != 200:
        print(f"❌ Failed to get users")
        return
    
    data = users_response.json()
    print(f"\n📋 Total users: {data['total']}\n")
    
    for user in data['users']:
        print(f"  • {user['username']} ({user['role']}) - Created: {user['created_at']}")

if __name__ == "__main__":
    print("=" * 60)
    print("🎬 Video Subtitle Generator - User Management")
    print("=" * 60)
    
    # Admin credentials
    admin_user = input("\nAdmin username [admin]: ").strip() or "admin"
    admin_pass = input("Admin password [admin123]: ").strip() or "admin123"
    
    while True:
        print("\n" + "=" * 60)
        print("เลือกการทำงาน:")
        print("  1. สร้าง user ใหม่")
        print("  2. ดูรายการ users")
        print("  3. ออก")
        print("=" * 60)
        
        choice = input("\nเลือก (1-3): ").strip()
        
        if choice == "1":
            print("\n--- สร้าง User ใหม่ ---")
            new_user = input("Username: ").strip()
            new_pass = input("Password: ").strip()
            role = input("Role (user/admin) [user]: ").strip() or "user"
            
            if new_user and new_pass:
                create_user(admin_user, admin_pass, new_user, new_pass, role)
            else:
                print("❌ Username และ Password ต้องไม่ว่าง")
        
        elif choice == "2":
            list_users(admin_user, admin_pass)
        
        elif choice == "3":
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ กรุณาเลือก 1-3")
