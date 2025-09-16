#!/usr/bin/env python3
"""
AgriQuest - Final Agriculture Courses Update
This script will update your system with proper BS Agriculture courses
Run this once your Render app is working properly
"""

import os
import sys
import requests
import json
import time

def get_app_url():
    """Get the app URL from user"""
    print("🌐 AgriQuest App Configuration")
    print("=" * 50)
    print("Please provide your Render app URL.")
    print("Example: https://your-app-name.onrender.com")
    print()
    
    url = input("Enter your Render app URL: ").strip()
    if not url.startswith('http'):
        url = 'https://' + url
    
    return url

def test_app_connection(base_url):
    """Test if the app is accessible"""
    print(f"\n🔍 Testing connection to {base_url}...")
    
    try:
        response = requests.get(f"{base_url}/", timeout=10)
        if response.status_code == 200:
            print("   ✅ App is accessible")
            return True
        else:
            print(f"   ❌ App returned status code: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Connection failed: {e}")
        return False

def login_to_app(base_url):
    """Login to the app and get session"""
    print("\n🔐 Logging in to your app...")
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", 
                               json=login_data, 
                               timeout=10)
        if response.status_code == 200:
            print("   ✅ Login successful")
            return response.cookies
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Login error: {e}")
        return None

def clear_existing_subjects(base_url, cookies):
    """Clear existing subjects via API"""
    print("\n🗑️  Clearing existing subjects...")
    
    try:
        # Get all subjects first
        response = requests.get(f"{base_url}/api/admin/subjects", 
                              cookies=cookies, timeout=10)
        if response.status_code == 200:
            subjects = response.json().get('subjects', [])
            print(f"   📊 Found {len(subjects)} existing subjects")
            
            # Delete each subject
            deleted_count = 0
            for subject in subjects:
                try:
                    delete_response = requests.delete(
                        f"{base_url}/api/admin/subjects/{subject['id']}", 
                        cookies=cookies, timeout=10)
                    if delete_response.status_code == 200:
                        print(f"   ✅ Deleted: {subject['name']}")
                        deleted_count += 1
                    else:
                        print(f"   ❌ Failed to delete {subject['name']}")
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Error deleting {subject['name']}: {e}")
            
            print(f"   📊 Deleted {deleted_count} subjects")
        else:
            print(f"   ❌ Failed to get subjects: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error clearing subjects: {e}")

def create_new_subjects(base_url, cookies):
    """Create new BS Agriculture subjects"""
    print("\n📚 Creating new BS Agriculture subjects...")
    
    subjects = [
        # Year 1 - Introductory Agriculture Courses
        {
            'name': 'Introduction to Agriculture',
            'description': 'Overview of agriculture, its importance, and basic concepts in agricultural science.',
            'year': 1,
            'code': 'AGRI-101'
        },
        {
            'name': 'Fundamentals of Crop Science I',
            'description': 'Basic principles of crop production, plant growth, and development.',
            'year': 1,
            'code': 'AGRI-102'
        },
        {
            'name': 'Fundamentals of Soil Science I',
            'description': 'Introduction to soil properties, composition, and basic soil management.',
            'year': 1,
            'code': 'AGRI-103'
        },
        {
            'name': 'Introduction to Animal Science',
            'description': 'Basic concepts of animal production, nutrition, and husbandry.',
            'year': 1,
            'code': 'AGRI-104'
        },
        
        # Year 2 - Core Agriculture Courses
        {
            'name': 'Fundamentals of Crop Science II',
            'description': 'Advanced crop production techniques, breeding, and biotechnology.',
            'year': 2,
            'code': 'AGRI-201'
        },
        {
            'name': 'Soil Science II',
            'description': 'Advanced soil chemistry, fertility, and sustainable soil management.',
            'year': 2,
            'code': 'AGRI-202'
        },
        {
            'name': 'Animal Science II',
            'description': 'Advanced animal nutrition, breeding, and production systems.',
            'year': 2,
            'code': 'AGRI-203'
        },
        {
            'name': 'General Entomology',
            'description': 'Study of insects, their role in agriculture, and pest management.',
            'year': 2,
            'code': 'AGRI-204'
        },
        {
            'name': 'Plant Pathology (Intro)',
            'description': 'Introduction to plant diseases, their causes, and management strategies.',
            'year': 2,
            'code': 'AGRI-205'
        },
        {
            'name': 'Agricultural Extension & Communication (Intro)',
            'description': 'Principles of agricultural extension, communication, and rural development.',
            'year': 2,
            'code': 'AGRI-206'
        }
    ]
    
    created_count = 0
    for subject in subjects:
        try:
            response = requests.post(f"{base_url}/api/admin/subjects", 
                                   json=subject, 
                                   cookies=cookies, 
                                   timeout=10)
            if response.status_code == 200:
                print(f"   ✅ Created: {subject['name']} (Year {subject['year']})")
                created_count += 1
            else:
                print(f"   ❌ Failed to create {subject['name']}: {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error creating {subject['name']}: {e}")
    
    print(f"   📊 Created {created_count} out of {len(subjects)} subjects")
    return created_count

def create_sample_quizzes(base_url, cookies):
    """Create sample quizzes for each subject"""
    print("\n📝 Creating sample quizzes...")
    
    try:
        # Get all subjects
        response = requests.get(f"{base_url}/api/admin/subjects", 
                              cookies=cookies, timeout=10)
        if response.status_code != 200:
            print("   ❌ Failed to get subjects")
            return
        
        subjects = response.json().get('subjects', [])
        print(f"   📊 Found {len(subjects)} subjects")
        
        # Create a sample quiz for each subject
        quiz_count = 0
        for subject in subjects:
            quiz_data = {
                'title': f'{subject["name"]} - Quiz 1',
                'description': f'Basic quiz for {subject["name"]}',
                'questions': [
                    {
                        'question': f'What is the main focus of {subject["name"]}?',
                        'options': ['Option A', 'Option B', 'Option C', 'Option D'],
                        'correct': 0
                    },
                    {
                        'question': f'Which of the following is important in {subject["name"]}?',
                        'options': ['Theory only', 'Practical application', 'Both theory and practice', 'None of the above'],
                        'correct': 2
                    }
                ]
            }
            
            try:
                response = requests.post(
                    f"{base_url}/api/teacher/subjects/{subject['id']}/quizzes", 
                    json=quiz_data, 
                    cookies=cookies, 
                    timeout=10)
                if response.status_code == 200:
                    print(f"   ✅ Created quiz for: {subject['name']}")
                    quiz_count += 1
                else:
                    print(f"   ❌ Failed to create quiz for {subject['name']}: {response.text}")
            except requests.exceptions.RequestException as e:
                print(f"   ❌ Error creating quiz for {subject['name']}: {e}")
        
        print(f"   📊 Created {quiz_count} quizzes")
        
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error getting subjects: {e}")

def main():
    """Main function"""
    print("🌱 AgriQuest - Final Agriculture Courses Update")
    print("=" * 60)
    print("This will update your deployed app with proper BS Agriculture courses.")
    print("Make sure your Render app is running and accessible before proceeding.")
    print()
    
    # Get app URL
    base_url = get_app_url()
    
    # Test connection
    if not test_app_connection(base_url):
        print("\n❌ Cannot connect to your app. Please check:")
        print("   1. Your app URL is correct")
        print("   2. Your Render app is deployed and running")
        print("   3. Your app is not showing 502 errors")
        print("\nTry again once your app is working properly.")
        return
    
    # Login
    cookies = login_to_app(base_url)
    if not cookies:
        print("❌ Cannot proceed without login")
        return
    
    # Clear existing subjects
    clear_existing_subjects(base_url, cookies)
    
    # Create new subjects
    created_count = create_new_subjects(base_url, cookies)
    
    if created_count > 0:
        # Create sample quizzes
        create_sample_quizzes(base_url, cookies)
        
        print("\n🎉 Course update completed successfully!")
        print("✅ All existing subjects removed")
        print("✅ 10 new BS Agriculture subjects created")
        print("✅ Subjects organized by year (1st and 2nd year)")
        print("✅ Sample quizzes created for each subject")
        
        print("\n📚 New Subjects:")
        print("Year 1:")
        print("  1. Introduction to Agriculture")
        print("  2. Fundamentals of Crop Science I")
        print("  3. Fundamentals of Soil Science I")
        print("  4. Introduction to Animal Science")
        print("Year 2:")
        print("  5. Fundamentals of Crop Science II")
        print("  6. Soil Science II")
        print("  7. Animal Science II")
        print("  8. General Entomology")
        print("  9. Plant Pathology (Intro)")
        print("  10. Agricultural Extension & Communication (Intro)")
        
        print(f"\n🌐 Visit your app at: {base_url}")
        print("   Login with: admin / admin123")
    else:
        print("❌ No subjects were created. Please check your app and try again.")

if __name__ == "__main__":
    main()
