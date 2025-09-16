#!/usr/bin/env python3
"""
AgriQuest - Migrate to Render PostgreSQL Database
Simple script to migrate your SQLite data to your existing Render PostgreSQL database
"""

import os
import sys

def main():
    print("🚀 AgriQuest - Migrate to Render PostgreSQL")
    print("=" * 50)
    print()
    print("📋 To get your Render PostgreSQL connection string:")
    print("1. Go to https://dashboard.render.com")
    print("2. Click on your PostgreSQL database service")
    print("3. Go to the 'Info' tab")
    print("4. Copy the 'Internal Database URL'")
    print()
    
    # Get connection string from user
    connection_string = input("🔗 Paste your Render PostgreSQL connection string: ").strip()
    
    if not connection_string:
        print("❌ No connection string provided.")
        return
    
    if not connection_string.startswith("postgresql://"):
        print("❌ Invalid format. Should start with 'postgresql://'")
        return
    
    # Set environment variable
    os.environ['DATABASE_URL'] = connection_string
    
    print("\n🔍 Testing connection...")
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
        
        print("✅ Connection successful!")
        print(f"📊 PostgreSQL version: {version}")
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return
    
    print("\n🔄 Running migration...")
    try:
        # Import and run the migration script
        import migrate_to_postgresql
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return
    
    print("\n📝 Creating .env file...")
    env_content = f"""# AgriQuest Environment Variables for Render
DATABASE_URL={connection_string}
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ .env file created")
    
    print("\n🎉 Migration completed!")
    print("✅ Your data has been migrated to Render PostgreSQL")
    print("✅ You can now deploy to Render.com")
    print()
    print("📋 Next steps:")
    print("1. Add DATABASE_URL to your Render web service environment variables")
    print("2. Deploy your application to Render")
    print("3. Your app will use PostgreSQL instead of SQLite")

if __name__ == "__main__":
    main()
