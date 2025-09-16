"""
API package for AgriQuest v2.0

This package contains all REST API endpoints organized by functionality:
- auth_api: Authentication endpoints
- admin_api: Admin management endpoints  
- teacher_api: Teacher functionality endpoints
- student_api: Student functionality endpoints

Author: AgriQuest Development Team
Version: 2.0
"""

from .auth_api import auth_api
from .admin_api import admin_api
from .teacher_api import teacher_api
from .student_api import student_api

__all__ = ['auth_api', 'admin_api', 'teacher_api', 'student_api']

