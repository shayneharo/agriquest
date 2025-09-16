#!/usr/bin/env python3
"""
Check if the AgriQuest system is working
"""

import requests
import psycopg2
from urllib.parse import urlparse

def get_database_connection():
    """Get database connection"""
    database_url = "postgresql://agriquest_user:45dtkZoHWC8uPDaj7nDPXG8qONxWxwIs@dpg-d34guuur433s73cjpo60-a.singapore-postgres.render.com/agriquest"
    
    if database_url and database_url.startswith('postgresql://'):
        url = urlparse(database_url)
        return psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
    else:
        return None

def check_database():
    """Check database status"""
    print("🔍 Checking database status...")
    
    try:
        conn = get_database_connection()
        if not conn:
            print("   ❌ Database connection failed")
            return False
        
        cursor = conn.cursor()
        
        # Check subjects
        cursor.execute("SELECT COUNT(*) FROM subjects")
        subject_count = cursor.fetchone()[0]
        print(f"   ✅ Subjects: {subject_count} found")
        
        # Check users
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"   ✅ Users: {user_count} found")
        
        # Check quizzes
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        quiz_count = cursor.fetchone()[0]
        print(f"   ✅ Quizzes: {quiz_count} found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"   ❌ Database error: {e}")
        return False

def check_render_app():
    """Check if Render app is accessible"""
    print("\n🌐 Checking Render app status...")
    
    app_urls = [
        "https://agriquest.onrender.com",
        "https://agriquest-ia.onrender.com"
    ]
    
    for url in app_urls:
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"   ✅ App is working: {url}")
                return True
            else:
                print(f"   ❌ App returned {response.status_code}: {url}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ App not accessible: {url} - {e}")
    
    return False

def main():
    """Main function"""
    print("🌱 AgriQuest System Status Check")
    print("=" * 50)
    
    # Check database
    db_working = check_database()
    
    # Check Render app
    app_working = check_render_app()
    
    print("\n📊 System Status Summary:")
    print(f"   Database: {'✅ Working' if db_working else '❌ Not Working'}")
    print(f"   Render App: {'✅ Working' if app_working else '❌ Not Working'}")
    
    if db_working and app_working:
        print("\n🎉 Your system is fully working!")
        print("   ✅ Database is connected and has data")
        print("   ✅ Render app is accessible")
        print("   ✅ You can login and use the system")
    elif db_working and not app_working:
        print("\n⚠️  Database is working but app is not accessible")
        print("   ✅ Your data is safe in the database")
        print("   ❌ Users cannot access the website")
        print("   💡 Check your Render deployment")
    elif not db_working and app_working:
        print("\n⚠️  App is accessible but database has issues")
        print("   ❌ Database connection problems")
        print("   💡 Check your database configuration")
    else:
        print("\n❌ System is not working")
        print("   ❌ Both database and app have issues")
        print("   💡 Check your Render deployment and database")

if __name__ == "__main__":
    main()
