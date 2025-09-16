#!/usr/bin/env python3
"""
AgriQuest - Deploy to Render with PostgreSQL Migration
This script prepares your app for Render deployment with automatic migration
"""

import os
import shutil
from pathlib import Path

def create_render_files():
    """Create files needed for Render deployment"""
    print("📋 Creating Render deployment files...")
    
    # Create render.yaml
    render_config = """services:
  - type: web
    name: agriquest
    env: python
    buildCommand: |
      pip install -r requirements.txt
      python migrate_to_postgresql.py
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
    
    print("✅ render.yaml created")
    
    # Create Procfile for alternative deployment
    procfile = """web: python run.py
release: python migrate_to_postgresql.py
"""
    
    with open('Procfile', 'w') as f:
        f.write(procfile)
    
    print("✅ Procfile created")
    
    # Update .gitignore
    gitignore_additions = """
# Environment variables
.env
.env.local
.env.production

# Database files
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
    
    if os.path.exists('.gitignore'):
        with open('.gitignore', 'a') as f:
            f.write(gitignore_additions)
    else:
        with open('.gitignore', 'w') as f:
            f.write(gitignore_additions)
    
    print("✅ .gitignore updated")

def create_deployment_script():
    """Create a deployment script that handles migration"""
    deployment_script = """#!/usr/bin/env python3
\"\"\"
AgriQuest - Render Deployment Script
Handles migration and deployment to Render
\"\"\"

import os
import sys
import subprocess

def main():
    print("🚀 AgriQuest - Render Deployment")
    print("=" * 40)
    
    # Check if DATABASE_URL is set
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL not set!")
        print("Please set DATABASE_URL in your Render environment variables")
        sys.exit(1)
    
    # Run migration
    print("🔄 Running database migration...")
    try:
        result = subprocess.run([sys.executable, 'migrate_to_postgresql.py'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Migration completed successfully!")
        else:
            print(f"❌ Migration failed: {result.stderr}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Migration error: {e}")
        sys.exit(1)
    
    # Start the application
    print("🚀 Starting AgriQuest application...")
    from app import app
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

if __name__ == "__main__":
    main()
"""
    
    with open('deploy.py', 'w') as f:
        f.write(deployment_script)
    
    print("✅ deploy.py created")

def create_readme():
    """Create deployment README"""
    readme = """# AgriQuest - Render Deployment

## 🚀 Quick Deploy to Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy on Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Select your AgriQuest repository

### 3. Configure Render Service
- **Build Command**: `pip install -r requirements.txt && python migrate_to_postgresql.py`
- **Start Command**: `python run.py`
- **Environment**: Python 3

### 4. Add Environment Variables
In your Render service settings, add:
- `DATABASE_URL`: Your Render PostgreSQL connection string (Internal Database URL)
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a random string

### 5. Deploy!
Click "Create Web Service" and wait for deployment.

## 📊 Database Migration

The migration will happen automatically during deployment:
- ✅ Creates PostgreSQL schema
- ✅ Migrates all SQLite data
- ✅ Sets up indexes and constraints
- ✅ Preserves all user data

## 🔧 Troubleshooting

### Migration Issues
- Check that DATABASE_URL is set correctly
- Ensure PostgreSQL database is accessible
- Check build logs for migration errors

### Application Issues
- Verify all environment variables are set
- Check application logs for errors
- Ensure port is set to 5000 or use PORT environment variable

## 📱 Access Your App

Once deployed, your app will be available at:
`https://your-app-name.onrender.com`

## 🎯 Features

- ✅ Role-based access (Admin, Teacher, Student)
- ✅ Quiz management system
- ✅ User management
- ✅ Subject management
- ✅ Real-time notifications
- ✅ PostgreSQL database
- ✅ Production-ready deployment
"""
    
    with open('RENDER_DEPLOYMENT.md', 'w') as f:
        f.write(readme)
    
    print("✅ RENDER_DEPLOYMENT.md created")

def main():
    """Main function"""
    print("🚀 AgriQuest - Prepare for Render Deployment")
    print("=" * 50)
    
    create_render_files()
    create_deployment_script()
    create_readme()
    
    print("\n🎉 Deployment files created successfully!")
    print("\n📋 Next steps:")
    print("1. Push your code to GitHub")
    print("2. Deploy on Render.com")
    print("3. Add DATABASE_URL environment variable")
    print("4. Your app will automatically migrate to PostgreSQL!")
    
    print("\n📖 See RENDER_DEPLOYMENT.md for detailed instructions")

if __name__ == "__main__":
    main()
