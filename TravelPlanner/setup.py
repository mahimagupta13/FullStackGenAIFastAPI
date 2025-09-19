#!/usr/bin/env python3
"""
Setup script for Travel Planner App
"""
import subprocess
import sys
import os

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist"""
    if not os.path.exists(".env"):
        print("📝 Creating .env file...")
        with open(".env", "w") as f:
            f.write("GROQ_API_KEY=your_groq_api_key_here\n")
            f.write("SECRET_KEY=your_secret_key_here\n")
        print("✅ .env file created! Please update it with your actual API keys.")
        return True
    else:
        print("✅ .env file already exists")
        return True

def check_data_directory():
    """Check if data directory exists"""
    if os.path.exists("data"):
        print("✅ Data directory exists")
        return True
    else:
        print("❌ Data directory not found. Please ensure data files are present.")
        return False

def main():
    """Main setup function"""
    print("🧳 Travel Planner App - Setup")
    print("=" * 40)
    
    # Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return False
    
    # Create .env file
    if not create_env_file():
        print("❌ Setup failed at .env file creation")
        return False
    
    # Check data directory
    if not check_data_directory():
        print("❌ Setup failed at data directory check")
        return False
    
    print("\n" + "=" * 40)
    print("✅ Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Update .env file with your Groq API key")
    print("2. Run: python start_backend.py")
    print("3. Run: python start_frontend.py")
    print("4. Or use: start_app.bat (Windows)")
    print("\n🔗 Get your Groq API key from: https://console.groq.com/")
    
    return True

if __name__ == "__main__":
    main()
