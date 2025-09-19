#!/usr/bin/env python3
"""
Test script for the Travel Planner application
"""
import requests
import json
import time
import sys

API_BASE_URL = "http://localhost:8000"

def test_api_connection():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ API is running and healthy")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API. Make sure the backend is running.")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def test_endpoints():
    """Test various API endpoints"""
    print("\n🧪 Testing API endpoints...")
    
    # Test destinations endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/destinations")
        if response.status_code == 200:
            destinations = response.json()
            print(f"✅ Destinations endpoint: {len(destinations)} destinations found")
        else:
            print(f"❌ Destinations endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing destinations: {e}")
    
    # Test hotels endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/hotels")
        if response.status_code == 200:
            hotels = response.json()
            print(f"✅ Hotels endpoint: {len(hotels)} hotels found")
        else:
            print(f"❌ Hotels endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing hotels: {e}")
    
    # Test activities endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/activities")
        if response.status_code == 200:
            activities = response.json()
            print(f"✅ Activities endpoint: {len(activities)} activities found")
        else:
            print(f"❌ Activities endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing activities: {e}")
    
    # Test reviews endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/reviews")
        if response.status_code == 200:
            reviews = response.json()
            print(f"✅ Reviews endpoint: {len(reviews)} reviews found")
        else:
            print(f"❌ Reviews endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing reviews: {e}")

def test_user_registration():
    """Test user registration"""
    print("\n👤 Testing user registration...")
    
    test_user = {
        "username": "test_user",
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/register", json=test_user)
        if response.status_code == 200:
            print("✅ User registration successful")
            return True
        else:
            print(f"❌ User registration failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error testing registration: {e}")
        return False

def test_user_login():
    """Test user login"""
    print("\n🔐 Testing user login...")
    
    login_data = {
        "username": "test_user",
        "password": "testpassword123"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            if "access_token" in token_data:
                print("✅ User login successful")
                return token_data["access_token"]
            else:
                print("❌ No access token in response")
                return None
        else:
            print(f"❌ User login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error testing login: {e}")
        return None

def test_authenticated_endpoints(token):
    """Test endpoints that require authentication"""
    if not token:
        print("❌ No token available for authenticated tests")
        return
    
    print("\n🔒 Testing authenticated endpoints...")
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test itineraries endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/itineraries", headers=headers)
        if response.status_code == 200:
            itineraries = response.json()
            print(f"✅ Itineraries endpoint: {len(itineraries)} itineraries found")
        else:
            print(f"❌ Itineraries endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error testing itineraries: {e}")

def test_recommendations():
    """Test AI recommendations endpoint"""
    print("\n🤖 Testing AI recommendations...")
    
    recommendation_data = {
        "destination_id": 1,
        "budget": 1000,
        "duration": 5,
        "interests": ["Culture", "Food"],
        "travel_style": "Mid-range"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/recommendations", json=recommendation_data)
        if response.status_code == 200:
            result = response.json()
            if "recommendations" in result:
                print("✅ AI recommendations endpoint working")
                print(f"📝 Sample recommendation: {result['recommendations'][:100]}...")
            else:
                print("❌ No recommendations in response")
        else:
            print(f"❌ Recommendations endpoint failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error testing recommendations: {e}")

def main():
    """Run all tests"""
    print("🧳 Travel Planner App - Test Suite")
    print("=" * 50)
    
    # Test API connection
    if not test_api_connection():
        print("\n❌ API is not running. Please start the backend first:")
        print("   python start_backend.py")
        sys.exit(1)
    
    # Test basic endpoints
    test_endpoints()
    
    # Test user registration
    if test_user_registration():
        # Test user login
        token = test_user_login()
        
        # Test authenticated endpoints
        test_authenticated_endpoints(token)
    
    # Test AI recommendations
    test_recommendations()
    
    print("\n" + "=" * 50)
    print("✅ Test suite completed!")
    print("\n📋 Next steps:")
    print("1. Start the frontend: python start_frontend.py")
    print("2. Open http://localhost:8501 in your browser")
    print("3. Register a new account or use test_user/testpassword123")

if __name__ == "__main__":
    main()
