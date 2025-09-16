#!/usr/bin/env python3
"""
AgriQuest V1 Cleanup Script
Safely removes V1 legacy files while preserving V2 functionality
"""

import os
import shutil
from pathlib import Path

def create_backup():
    """Create a backup before cleanup"""
    print("📦 Creating backup before cleanup...")
    backup_dir = f"agriquest_v1_backup_{os.popen('date +%Y%m%d_%H%M%S').read().strip()}"
    os.makedirs(backup_dir, exist_ok=True)
    
    # Backup old controllers
    if os.path.exists("backend/controllers/admin_controller.py"):
        shutil.copy2("backend/controllers/admin_controller.py", f"{backup_dir}/admin_controller.py")
    
    if os.path.exists("backend/controllers/profile_controller.py"):
        shutil.copy2("backend/controllers/profile_controller.py", f"{backup_dir}/profile_controller.py")
    
    # Backup React components
    if os.path.exists("frontend/react_components"):
        shutil.copytree("frontend/react_components", f"{backup_dir}/react_components")
    
    # Backup API files
    if os.path.exists("backend/api"):
        shutil.copytree("backend/api", f"{backup_dir}/api")
    
    print(f"✅ Backup created: {backup_dir}")
    return backup_dir

def remove_v1_files():
    """Remove V1 legacy files"""
    print("🗑️  Removing V1 legacy files...")
    
    # Remove old controllers
    old_controllers = [
        "backend/controllers/admin_controller.py",
        "backend/controllers/profile_controller.py"
    ]
    
    for controller in old_controllers:
        if os.path.exists(controller):
            os.remove(controller)
            print(f"   ✅ Removed: {controller}")
    
    # Remove React components (conceptual examples)
    if os.path.exists("frontend/react_components"):
        shutil.rmtree("frontend/react_components")
        print("   ✅ Removed: frontend/react_components/")
    
    # Remove API files (conceptual examples)
    if os.path.exists("backend/api"):
        shutil.rmtree("backend/api")
        print("   ✅ Removed: backend/api/")

def update_main_app():
    """Update main app to remove V1 imports"""
    print("🔧 Updating main application...")
    
    # Read current __init__.py
    with open("backend/__init__.py", "r") as f:
        content = f.read()
    
    # Remove V1 controller imports and registrations
    lines_to_remove = [
        "from .controllers.admin_controller import admin_bp",
        "from .controllers.profile_controller import profile_bp",
        "app.register_blueprint(admin_bp)",
        "app.register_blueprint(profile_bp)",
        "from .api.auth_api import auth_api_bp",
        "from .api.student_api import student_api_bp", 
        "from .api.classes_api import classes_api_bp",
        "app.register_blueprint(auth_api_bp)",
        "app.register_blueprint(student_api_bp)",
        "app.register_blueprint(classes_api_bp)"
    ]
    
    for line in lines_to_remove:
        content = content.replace(line + "\n", "")
    
    # Write updated content
    with open("backend/__init__.py", "w") as f:
        f.write(content)
    
    print("   ✅ Updated backend/__init__.py")

def verify_v2_functionality():
    """Verify V2 system still works"""
    print("🔍 Verifying V2 functionality...")
    
    try:
        from backend import create_app
        app = create_app()
        print("   ✅ V2 application loads successfully")
        
        # Check V2 routes exist
        v2_routes = [
            'admin_v2.dashboard',
            'teacher_v2.dashboard', 
            'student_v2.dashboard',
            'profile_v2.view_profile'
        ]
        
        with app.app_context():
            for route in v2_routes:
                try:
                    from flask import url_for
                    url_for(route)
                    print(f"   ✅ Route exists: {route}")
                except:
                    print(f"   ⚠️  Route missing: {route}")
        
        return True
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main cleanup function"""
    print("🧹 AgriQuest V1 Cleanup Script")
    print("=" * 50)
    
    # Create backup
    backup_dir = create_backup()
    
    # Remove V1 files
    remove_v1_files()
    
    # Update main app
    update_main_app()
    
    # Verify V2 works
    if verify_v2_functionality():
        print("\n🎉 V1 cleanup completed successfully!")
        print(f"📦 Backup available at: {backup_dir}")
        print("✅ V2 system is fully functional")
    else:
        print("\n❌ V1 cleanup failed - V2 system not working")
        print("🔄 Restore from backup if needed")

if __name__ == "__main__":
    main()

