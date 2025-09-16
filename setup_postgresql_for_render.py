#!/usr/bin/env python3
"""
AgriQuest - PostgreSQL Setup for Render.com Deployment
This script helps you set up PostgreSQL for Render.com deployment
"""

import os
import subprocess
import webbrowser
from pathlib import Path

def print_banner():
    """Print setup banner"""
    print("🚀 AgriQuest PostgreSQL Setup for Render.com")
    print("=" * 60)
    print("This will help you set up PostgreSQL for deployment on Render.com")
    print()

def setup_railway_database():
    """Guide user through Railway setup"""
    print("📦 Setting up Railway PostgreSQL Database...")
    print()
    print("1. 🌐 Opening Railway.app in your browser...")
    
    try:
        webbrowser.open("https://railway.app")
        print("   ✅ Railway opened in browser")
    except:
        print("   ⚠️  Please manually open https://railway.app")
    
    print()
    print("2. 📝 Follow these steps on Railway:")
    print("   • Sign up with GitHub")
    print("   • Click 'New Project'")
    print("   • Select 'Database' → 'PostgreSQL'")
    print("   • Wait for database to be created")
    print("   • Click on your database")
    print("   • Go to 'Connect' tab")
    print("   • Copy the 'Connection String'")
    print()
    
    # Get connection string from user
    connection_string = input("3. 🔗 Paste your Railway PostgreSQL connection string here: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided. Please try again.")
        return None
    
    # Validate connection string
    if not connection_string.startswith("postgresql://"):
        print("❌ Invalid connection string format. Should start with 'postgresql://'")
        return None
    
    return connection_string

def test_connection(connection_string):
    """Test PostgreSQL connection"""
    print("\n🔍 Testing PostgreSQL connection...")
    
    try:
        import psycopg2
        from urllib.parse import urlparse
        
        url = urlparse(connection_string)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        conn.close()
        
        print("   ✅ Connection successful!")
        print(f"   📊 PostgreSQL version: {version}")
        return True
        
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def create_env_file(connection_string):
    """Create .env file with DATABASE_URL"""
    print("\n📝 Creating .env file...")
    
    env_content = f"""# AgriQuest Environment Variables
DATABASE_URL={connection_string}

# Flask Configuration
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("   ✅ .env file created")
    print("   ⚠️  Remember to add .env to .gitignore for security")

def run_migration(connection_string):
    """Run the migration script"""
    print("\n🔄 Running database migration...")
    
    # Set environment variable
    os.environ['DATABASE_URL'] = connection_string
    
    try:
        # Import and run migration
        import sys
        sys.path.insert(0, '.')
        
        # Run the migration script
        result = subprocess.run([sys.executable, 'migrate_to_postgresql.py'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("   ✅ Migration completed successfully!")
            print(result.stdout)
        else:
            print("   ❌ Migration failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"   ❌ Migration error: {e}")
        return False
    
    return True

def create_render_config():
    """Create Render.com configuration files"""
    print("\n📋 Creating Render.com configuration...")
    
    # Create render.yaml
    render_config = """services:
  - type: web
    name: agriquest
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: python run.py
    envVars:
      - key: DATABASE_URL
        sync: false
      - key: FLASK_ENV
        value: production
      - key: SECRET_KEY
        generateValue: true
    healthCheckPath: /
    autoDeploy: true
"""
    
    with open('render.yaml', 'w') as f:
        f.write(render_config)
    
    print("   ✅ render.yaml created")
    
    # Create .gitignore additions
    gitignore_additions = """
# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python
env/
venv/
.venv/
"""
    
    # Append to .gitignore if it exists
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'a') as f:
            f.write(gitignore_additions)
    else:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_additions)
    
    print("   ✅ .gitignore updated")

def print_deployment_instructions():
    """Print deployment instructions"""
    print("\n🚀 Render.com Deployment Instructions")
    print("=" * 50)
    print("1. 📤 Push your code to GitHub:")
    print("   git add .")
    print("   git commit -m 'Add PostgreSQL support for Render deployment'")
    print("   git push origin main")
    print()
    print("2. 🌐 Deploy on Render.com:")
    print("   • Go to https://render.com")
    print("   • Sign up with GitHub")
    print("   • Click 'New' → 'Web Service'")
    print("   • Connect your GitHub repository")
    print("   • Select your AgriQuest repository")
    print("   • Use these settings:")
    print("     - Build Command: pip install -r requirements.txt")
    print("     - Start Command: python run.py")
    print("     - Environment: Python 3")
    print()
    print("3. 🔧 Add Environment Variables on Render:")
    print("   • Go to your service → Environment")
    print("   • Add DATABASE_URL with your Railway connection string")
    print("   • Add FLASK_ENV = production")
    print("   • Add SECRET_KEY (generate a random string)")
    print()
    print("4. 🎉 Deploy!")
    print("   • Click 'Create Web Service'")
    print("   • Wait for deployment to complete")
    print("   • Your app will be available at the provided URL")

def main():
    """Main setup function"""
    print_banner()
    
    # Step 1: Setup Railway database
    connection_string = setup_railway_database()
    if not connection_string:
        return
    
    # Step 2: Test connection
    if not test_connection(connection_string):
        print("\n❌ Setup failed. Please check your connection string.")
        return
    
    # Step 3: Create .env file
    create_env_file(connection_string)
    
    # Step 4: Run migration
    if not run_migration(connection_string):
        print("\n❌ Migration failed. Please check the error messages above.")
        return
    
    # Step 5: Create Render configuration
    create_render_config()
    
    # Step 6: Print deployment instructions
    print_deployment_instructions()
    
    print("\n🎉 PostgreSQL setup completed successfully!")
    print("✅ Your app is now ready for Render.com deployment!")

if __name__ == "__main__":
    main()
