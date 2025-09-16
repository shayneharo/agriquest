#!/usr/bin/env python3
"""
Fix template paths in controllers to match actual template locations
"""

import os
import re

def fix_template_paths(file_path):
    """Fix template paths in a controller file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Replace template paths
        replacements = [
            ("'admin/", "'admin_"),
            ("'teacher/", "'teacher_"),
            ("'student/", "'student_"),
            ("'profile/", "'profile_"),
            ('"admin/', '"admin_'),
            ('"teacher/', '"teacher_'),
            ('"student/', '"student_'),
            ('"profile/', '"profile_')
        ]
        
        for old, new in replacements:
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
    """Main function"""
    print("🔧 Fixing template paths in controllers...")
    
    files_to_fix = [
        'backend/controllers/admin_controller.py',
        'backend/controllers/teacher_controller.py',
        'backend/controllers/student_controller.py',
        'backend/controllers/profile_controller.py'
    ]
    
    updated_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_template_paths(file_path):
                updated_count += 1
        else:
            print(f"⚠️  File not found: {file_path}")
    
    print(f"\n🎉 Updated {updated_count} files successfully!")

if __name__ == "__main__":
    main()

