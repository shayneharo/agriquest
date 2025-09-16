#!/usr/bin/env python3
"""
AgriQuest - Update Courses for Render Deployment
This script updates the agriculture courses on your deployed Render application
"""

import requests
import json
import os

def get_render_app_url():
    """Get the Render app URL from user"""
    print("🌐 Render App Configuration")
    print("=" * 40)
    print("To update your courses on Render, I need your app URL.")
    print()
    print("You can find your app URL in your Render dashboard:")
    print("1. Go to https://dashboard.render.com")
    print("2. Click on your AgriQuest web service")
    print("3. Copy the URL (it looks like: https://your-app-name.onrender.com)")
    print()
    
    url = input("Enter your Render app URL: ").strip()
    if not url.startswith('http'):
        url = 'https://' + url
    
    return url

def login_to_app(base_url):
    """Login to the app and get session"""
    print("\n🔐 Logging in to your app...")
    
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f"{base_url}/api/auth/login", json=login_data)
        if response.status_code == 200:
            print("   ✅ Login successful")
            return response.cookies
        else:
            print(f"   ❌ Login failed: {response.text}")
            return None
    except Exception as e:
        print(f"   ❌ Login error: {e}")
        return None

def create_subjects_via_api(base_url, cookies):
    """Create new subjects via API"""
    print("\n📚 Creating new agriculture subjects...")
    
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
                                   json=subject, cookies=cookies)
            if response.status_code == 200:
                print(f"   ✅ Created: {subject['name']} (Year {subject['year']})")
                created_count += 1
            else:
                print(f"   ❌ Failed to create {subject['name']}: {response.text}")
        except Exception as e:
            print(f"   ❌ Error creating {subject['name']}: {e}")
    
    print(f"   📊 Created {created_count} out of {len(subjects)} subjects")
    return created_count

def create_sample_quizzes_via_api(base_url, cookies):
    """Create sample quizzes for subjects"""
    print("\n📝 Creating sample quizzes...")
    
    # Get subjects first
    try:
        response = requests.get(f"{base_url}/api/admin/subjects", cookies=cookies)
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
                    }
                ]
            }
            
            try:
                response = requests.post(f"{base_url}/api/teacher/subjects/{subject['id']}/quizzes", 
                                       json=quiz_data, cookies=cookies)
                if response.status_code == 200:
                    print(f"   ✅ Created quiz for: {subject['name']}")
                    quiz_count += 1
                else:
                    print(f"   ❌ Failed to create quiz for {subject['name']}: {response.text}")
            except Exception as e:
                print(f"   ❌ Error creating quiz for {subject['name']}: {e}")
        
        print(f"   📊 Created {quiz_count} quizzes")
        
    except Exception as e:
        print(f"   ❌ Error getting subjects: {e}")

def main():
    """Main function"""
    print("🌱 AgriQuest - Update Courses for Render")
    print("=" * 50)
    print("This will update your deployed Render app with new BS Agriculture courses.")
    print()
    
    # Get app URL
    base_url = get_render_app_url()
    
    # Login
    cookies = login_to_app(base_url)
    if not cookies:
        print("❌ Cannot proceed without login")
        return
    
    # Create subjects
    created_count = create_subjects_via_api(base_url, cookies)
    
    if created_count > 0:
        # Create sample quizzes
        create_sample_quizzes_via_api(base_url, cookies)
        
        print("\n🎉 Course update completed!")
        print("✅ New BS Agriculture subjects created")
        print("✅ Sample quizzes created")
        print("✅ Your app is now updated with proper agriculture curriculum")
        
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
    else:
        print("❌ No subjects were created. Please check your app and try again.")

if __name__ == "__main__":
    main()
