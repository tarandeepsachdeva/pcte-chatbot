#!/usr/bin/env python3
"""
Setup script for the Chatbot API with Gemini Integration
"""

import os
import subprocess
import sys

def install_requirements():
    """Install required packages"""
    print("Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False

def check_api_key():
    """Check if Google API key is set"""
    api_key = os.getenv('GOOGLE_API_KEY')
    if not api_key:
        print("⚠️  GOOGLE_API_KEY environment variable not set!")
        print("\nTo set your API key:")
        print("1. Get your API key from: https://makersuite.google.com/app/apikey")
        print("2. Set it as an environment variable:")
        print("   export GOOGLE_API_KEY='your_api_key_here'")
        print("   # or add it to your .bashrc/.zshrc file")
        print("\nAlternatively, you can create a .env file with:")
        print("GOOGLE_API_KEY=your_api_key_here")
        return False
    else:
        print("✅ Google API key is configured!")
        return True

def main():
    print("Chatbot API Setup")
    print("=" * 20)
    
    # Install requirements
    if not install_requirements():
        return
    
    print()
    
    # Check API key
    api_key_ok = check_api_key()
    
    print("\nSetup Instructions:")
    print("1. Make sure you have your Google API key set")
    print("2. Run the API server: python api_server.py")
    print("3. Test the API: python test_api.py")
    print("\nAPI Endpoints:")
    print("- POST http://localhost:5000/chat")
    print("- GET http://localhost:5000/health")
    print("- GET http://localhost:5000/")
    
    if not api_key_ok:
        print("\n⚠️  Remember to set your GOOGLE_API_KEY before running the server!")

if __name__ == "__main__":
    main()


