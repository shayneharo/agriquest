#!/usr/bin/env python3
"""
AgriQuest - Render Deployment Script
Handles migration and deployment to Render
"""

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
