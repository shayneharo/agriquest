#!/usr/bin/env python3
"""
AgriQuest Deployment Diagnostic Tool
Helps identify and fix deployment issues
"""

import os
import sys
import requests
import subprocess

def check_requirements():
    """Check if requirements.txt is correct"""
    print("📋 Checking requirements.txt...")
    
    if not os.path.exists('requirements.txt'):
        print("   ❌ requirements.txt not found")
        return False
    
    with open('requirements.txt', 'r') as f:
        content = f.read()
    
    required_packages = [
        'Flask',
        'psycopg2-binary',
        'Werkzeug'
    ]
    
    missing_packages = []
    for package in required_packages:
        if package.lower() not in content.lower():
            missing_packages.append(package)
    
    if missing_packages:
        print(f"   ❌ Missing packages: {', '.join(missing_packages)}")
        return False
    else:
        print("   ✅ requirements.txt looks good")
        return True

def check_procfile():
    """Check if Procfile is correct"""
    print("\n📄 Checking Procfile...")
    
    if not os.path.exists('Procfile'):
        print("   ❌ Procfile not found")
        return False
    
    with open('Procfile', 'r') as f:
        content = f.read().strip()
    
    if 'web: python run.py' in content:
        print("   ✅ Procfile looks correct")
        return True
    else:
        print(f"   ❌ Procfile content: '{content}'")
        print("   💡 Should be: 'web: python run.py'")
        return False

def check_run_py():
    """Check if run.py exists and is correct"""
    print("\n🐍 Checking run.py...")
    
    if not os.path.exists('run.py'):
        print("   ❌ run.py not found")
        return False
    
    with open('run.py', 'r') as f:
        content = f.read()
    
    if 'if __name__ == "__main__":' in content and 'app.run(' in content:
        print("   ✅ run.py looks correct")
        return True
    else:
        print("   ❌ run.py might have issues")
        return False

def check_environment_variables():
    """Check if environment variables are set"""
    print("\n🔧 Checking environment variables...")
    
    required_vars = ['DATABASE_URL', 'SECRET_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ Missing environment variables: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ Environment variables are set")
        return True

def test_local_app():
    """Test if the app runs locally"""
    print("\n🧪 Testing local app...")
    
    try:
        # Try to import the app
        sys.path.insert(0, '.')
        from backend import create_app
        app = create_app()
        print("   ✅ App imports successfully")
        return True
    except Exception as e:
        print(f"   ❌ App import failed: {e}")
        return False

def main():
    """Main diagnostic function"""
    print("🔍 AgriQuest Deployment Diagnostic")
    print("=" * 50)
    
    checks = [
        check_requirements(),
        check_procfile(),
        check_run_py(),
        check_environment_variables(),
        test_local_app()
    ]
    
    passed = sum(checks)
    total = len(checks)
    
    print(f"\n📊 Diagnostic Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your app should deploy successfully.")
        print("\n💡 If it's still not working, try:")
        print("   1. Force redeploy on Render")
        print("   2. Check Render logs for specific errors")
        print("   3. Verify your GitHub repository is up to date")
    else:
        print("\n❌ Some issues found. Fix these before deploying:")
        
        if not checks[0]:
            print("   📋 Fix requirements.txt")
        if not checks[1]:
            print("   📄 Fix Procfile")
        if not checks[2]:
            print("   🐍 Fix run.py")
        if not checks[3]:
            print("   🔧 Set environment variables on Render")
        if not checks[4]:
            print("   🧪 Fix app import issues")

if __name__ == "__main__":
    main()
