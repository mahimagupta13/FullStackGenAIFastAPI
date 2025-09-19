#!/usr/bin/env python3
"""
Test login for multiple users
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_user_login(username, password):
    """Test login for a specific user"""
    print(f"🔐 Testing login for user '{username}'...")
    
    login_data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print(f"✅ Login successful for {username}!")
                print(f"Token: {token_data['access_token'][:50]}...")
                return token_data["access_token"]
            else:
                print(f"❌ No access token in response for {username}")
                return None
        else:
            print(f"❌ Login failed for {username}: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login for {username}: {e}")
        return None

def test_authenticated_request(username, token):
    """Test an authenticated request"""
    if not token:
        print(f"❌ No token available for {username}")
        return
    
    print(f"\n🔒 Testing authenticated request for {username}...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/itineraries", headers=headers)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print(f"✅ Authenticated request successful for {username}!")
        else:
            print(f"❌ Authenticated request failed for {username}: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing authenticated request for {username}: {e}")

if __name__ == "__main__":
    print("🧳 Testing User Logins")
    print("=" * 40)
    
    # Test users
    test_users = [
        ("Mahima", "12345"),
        ("amit", "amit123"),
        ("anika", "anika123")
    ]
    
    for username, password in test_users:
        print(f"\n{'='*20} {username} {'='*20}")
        token = test_user_login(username, password)
        test_authenticated_request(username, token)
        print()
