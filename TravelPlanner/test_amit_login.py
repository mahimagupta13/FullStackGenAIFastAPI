#!/usr/bin/env python3
"""
Test login for user 'amit'
"""
import requests
import json

API_BASE_URL = "http://localhost:8000"

def test_amit_login():
    """Test login for user amit"""
    print("🔐 Testing login for user 'amit'...")
    
    # Test data
    login_data = {
        "username": "amit",
        "password": "amit123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print("✅ Login successful!")
                print(f"Token: {token_data['access_token'][:50]}...")
                return token_data["access_token"]
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_authenticated_request(token):
    """Test an authenticated request"""
    if not token:
        print("❌ No token available for authenticated test")
        return
    
    print("\n🔒 Testing authenticated request...")
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{API_BASE_URL}/itineraries", headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Authenticated request successful!")
        else:
            print(f"❌ Authenticated request failed: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error testing authenticated request: {e}")

if __name__ == "__main__":
    print("🧳 Testing Amit Login")
    print("=" * 30)
    
    # Test login
    token = test_amit_login()
    
    # Test authenticated request
    test_authenticated_request(token)
