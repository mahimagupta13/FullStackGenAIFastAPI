#!/usr/bin/env python3
"""
Startup script for the Travel Planner Streamlit frontend
"""
import subprocess
import sys
import os

def main():
    """Start the Streamlit frontend"""
    print("🎨 Starting Travel Planner Frontend...")
    print("🌐 Frontend will be available at: http://localhost:8501")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "UI.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped by user")
    except Exception as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
