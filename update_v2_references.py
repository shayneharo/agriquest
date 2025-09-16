#!/usr/bin/env python3
"""
Update all V2 references to clean names
"""

import os
import re

def update_file(file_path, replacements):
    """Update a file with multiple replacements"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        for old, new in replacements.items():
            content = content.replace(old, new)
        
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
            return True
        else:
            print(f"⏭️  No changes: {file_path}")
            return False
    except Exception as e:
        print(f"❌ Error updating {file_path}: {e}")
        return False

def main():
    """Main update function"""
    print("🔄 Updating V2 references to clean names...")
    
    # Define replacements
    replacements = {
        'admin_v2': 'admin',
        'teacher_v2': 'teacher', 
        'student_v2': 'student',
        'profile_v2': 'profile'
    }
    
    # Files to update
    files_to_update = [
        'backend/controllers/admin_controller.py',
        'backend/controllers/teacher_controller.py', 
        'backend/controllers/student_controller.py',
        'backend/controllers/profile_controller.py'
    ]
    
    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_file(file_path, replacements):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎉 Updated {updated_count} files successfully!")
    
    # Check for any remaining V2 references
    print("\n🔍 Checking for remaining V2 references...")
    remaining_v2 = []
    
    for file_path in files_to_update:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'v2' in content.lower():
                    remaining_v2.append(file_path)
    
    if remaining_v2:
        print("⚠️  Remaining V2 references found in:")
        for file_path in remaining_v2:
            print(f"   - {file_path}")
    else:
        print("✅ No remaining V2 references found!")

if __name__ == "__main__":
    main()

