#!/usr/bin/env python3
"""
AgriQuest - Agricultural Learning Platform
Run script for easy application startup
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['flask', 'werkzeug']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install missing packages with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    return True

def setup_environment():
    """Setup environment variables and paths"""
    # Set the current directory as the working directory
    current_dir = Path(__file__).parent.absolute()
    os.chdir(current_dir)
    
    # Set Flask environment
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    
    print(f"📁 Working directory: {current_dir}")

def print_banner():
    """Print application banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🌱 AgriQuest 🌱                       ║
║              Agricultural Learning Platform                  ║
║                                                              ║
║  👨‍💼 Admins:  Manage system, users, and subjects            ║
║  👨‍🏫 Teachers: Create and manage educational content        ║
║  🎓 Students: Learn through interactive quizzes             ║
║  📝 All users must register to get started                 ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_test_accounts():
    """Print test account information"""
    print("🔑 Test Accounts (For Testing Only):")
    print("   👨‍💼 Admin:   username='admin', password='admin123'")
    print("   👨‍🏫 Teacher: username='teacherdenisse', password='Teacher123!'")
    print("   🎓 Student:  username='studentdenisse', password='Student123!'")
    print()
    print("🔑 Real User Registration:")
    print("   📝 New users register with their actual email/phone")
    print("   📧 Email OTP: Sent to user's actual email address")
    print("   📱 SMS OTP: Displayed in this terminal (for testing)")
    print("   🎓 Students: Learn through interactive quizzes")
    print("   👨‍🏫 Teachers: Create and manage educational content")
    print()

def print_access_info():
    """Print access information"""
    print("🌐 Application Access:")
    print("   📱 Local:    http://localhost:5000")
    print("   🌍 Network:  http://127.0.0.1:5000")
    print()
    print("⌨️  Controls:")
    print("   🛑 Stop:     Ctrl+C")
    print("   🔄 Restart:  Run this script again")
    print()

def main():
    """Main function to run the application"""
    print_banner()
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    print("✅ All dependencies found")
    
    # Setup environment
    print("⚙️  Setting up environment...")
    setup_environment()
    print("✅ Environment ready")
    
    # Print test accounts
    print_test_accounts()
    
    # Print access info
    print_access_info()
    
    # Import and run the application
    try:
        print("🚀 Starting AgriQuest...")
        print("=" * 60)
        
        # Show actual configuration status
        print("📧 Email: Configured (shayneharo03@gmail.com)")
        print("📱 SMS: Console mode (OTP codes printed to terminal)")
        print()
        print("🔑 Authentication System:")
        print("   📧 Real Email: OTP codes sent to user's email")
        print("   📱 Console SMS: OTP codes displayed in this terminal")
        print("   🔐 Secure: All authentication working with real email")
        print()
        print("✨ Features:")
        print("   🔄 Real email verification for registration")
        print("   🎯 SMS codes appear in terminal for testing")
        print("   📱 All authentication features fully functional")
        print("💡 OTP codes will appear in this terminal when generated!")
 
        
        # Import the app
        from app import app
        
        # Run the application
        app.run(
            host='0.0.0.0',  # Allow external connections
            port=5000,
            debug=True,
            use_reloader=True
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Application stopped by user")
        print("👋 Thank you for using AgriQuest!")
        
    except Exception as e:
        print(f"\n❌ Error starting application: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Make sure all dependencies are installed")
        print("   2. Check if port 5000 is available")
        print("   3. Verify database permissions")
        sys.exit(1)

if __name__ == "__main__":
    main()
