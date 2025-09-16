# 🌱 AgriQuest v2.0 API Documentation

## Overview

This document provides comprehensive API documentation for AgriQuest v2.0, a role-based agricultural learning platform. The API supports three user types: Admin/Adviser, Subject Teacher, and Student.

## Base URL
```
http://localhost:5000
```

## Authentication

All API endpoints require authentication via session-based login. Users must be logged in to access protected routes.

## User Roles

- **Admin/Adviser**: Full system management capabilities
- **Teacher**: Subject-specific management and student oversight
- **Student**: Learning and enrollment focused functionality

---

## 🔐 Authentication Endpoints

### Login
- **POST** `/login`
- **Description**: Authenticate user and create session
- **Body**: `{ "username": "string", "password": "string" }`
- **Response**: Redirect to appropriate dashboard based on role

### Logout
- **GET** `/logout`
- **Description**: End user session
- **Response**: Redirect to login page

### Register
- **POST** `/register`
- **Description**: Register new user with email verification
- **Body**: `{ "username": "string", "password": "string", "email": "string", "full_name": "string", "role": "student|teacher" }`
- **Response**: Success message with OTP verification required

---

## 👨‍💼 Admin/Adviser Endpoints

### Dashboard
- **GET** `/admin_v2/dashboard`
- **Description**: Main admin dashboard with system overview
- **Access**: Admin only
- **Response**: Dashboard with statistics and recent activity

### User Management
- **GET** `/admin_v2/users`
- **Description**: View all users with filtering options
- **Query Parameters**: `role`, `search`
- **Access**: Admin only

- **POST** `/admin_v2/users/create`
- **Description**: Create new user
- **Body**: `{ "username": "string", "password": "string", "role": "string", "email": "string", "full_name": "string" }`
- **Access**: Admin only

- **POST** `/admin_v2/users/<user_id>/toggle_status`
- **Description**: Activate/deactivate user account
- **Access**: Admin only

### Subject Management
- **GET** `/admin_v2/subjects`
- **Description**: View all subjects
- **Access**: Admin only

- **POST** `/admin_v2/subjects/create`
- **Description**: Create new subject
- **Body**: `{ "name": "string", "description": "string" }`
- **Access**: Admin only

- **POST** `/admin_v2/subjects/<subject_id>/edit`
- **Description**: Update subject information
- **Body**: `{ "name": "string", "description": "string" }`
- **Access**: Admin only

### Teacher Invitations
- **POST** `/admin_v2/subjects/<subject_id>/invite_teacher`
- **Description**: Invite teacher to manage subject
- **Body**: `{ "teacher_id": "integer" }`
- **Access**: Admin only

### Weakness Tracking
- **GET** `/admin_v2/weaknesses`
- **Description**: View student weaknesses across subjects
- **Query Parameters**: `subject_id`, `search`
- **Access**: Admin only

### Search
- **GET** `/admin_v2/search`
- **Description**: Search for users and subjects
- **Query Parameters**: `q` (query), `role`
- **Access**: Admin only

### Notifications
- **GET** `/admin_v2/notifications`
- **Description**: View admin notifications
- **Access**: Admin only

- **POST** `/admin_v2/notifications/<notification_id>/read`
- **Description**: Mark notification as read
- **Access**: Admin only

---

## 👨‍🏫 Teacher Endpoints

### Dashboard
- **GET** `/teacher_v2/dashboard`
- **Description**: Main teacher dashboard
- **Access**: Teacher only
- **Response**: Dashboard with assigned subjects and pending requests

### Invitations
- **GET** `/teacher_v2/invitations`
- **Description**: View pending subject invitations
- **Access**: Teacher only

- **POST** `/teacher_v2/invitations/<subject_id>/accept`
- **Description**: Accept subject invitation
- **Access**: Teacher only

- **POST** `/teacher_v2/invitations/<subject_id>/reject`
- **Description**: Reject subject invitation
- **Access**: Teacher only

### Subject Management
- **GET** `/teacher_v2/subjects`
- **Description**: View assigned subjects
- **Access**: Teacher only

- **GET** `/teacher_v2/subjects/<subject_id>`
- **Description**: View subject details and manage students
- **Access**: Teacher only

### Student Management
- **POST** `/teacher_v2/subjects/<subject_id>/approve_student/<student_id>`
- **Description**: Approve student enrollment request
- **Access**: Teacher only

- **POST** `/teacher_v2/subjects/<subject_id>/reject_student/<student_id>`
- **Description**: Reject student enrollment request
- **Access**: Teacher only

### Weakness Tracking
- **GET** `/teacher_v2/weaknesses`
- **Description**: View student weaknesses in assigned subjects
- **Query Parameters**: `subject_id`
- **Access**: Teacher only

### Search
- **GET** `/teacher_v2/search`
- **Description**: Search for students
- **Query Parameters**: `q` (query)
- **Access**: Teacher only

---

## 🎓 Student Endpoints

### Dashboard
- **GET** `/student_v2/dashboard`
- **Description**: Main student dashboard
- **Access**: Student only
- **Response**: Dashboard with enrolled subjects and upcoming quizzes

### Subject Management
- **GET** `/student_v2/subjects`
- **Description**: Browse all subjects and enrollment status
- **Access**: Student only

- **POST** `/student_v2/subjects/<subject_id>/enroll`
- **Description**: Request enrollment in subject
- **Access**: Student only

- **POST** `/student_v2/subjects/<subject_id>/withdraw`
- **Description**: Withdraw from subject
- **Access**: Student only

- **GET** `/student_v2/my_subjects`
- **Description**: View enrolled subjects
- **Access**: Student only

### Quiz Access
- **GET** `/student_v2/subjects/<subject_id>/quizzes`
- **Description**: View quizzes for enrolled subject
- **Access**: Student only

### Weakness Tracking
- **GET** `/student_v2/weaknesses`
- **Description**: View personal weaknesses
- **Query Parameters**: `subject_id`
- **Access**: Student only

- **POST** `/student_v2/weaknesses/add`
- **Description**: Add personal weakness
- **Body**: `{ "subject_id": "integer", "weakness_type": "string", "description": "string" }`
- **Access**: Student only

- **POST** `/student_v2/weaknesses/<weakness_id>/delete`
- **Description**: Delete personal weakness
- **Access**: Student only

### Search
- **GET** `/student_v2/search`
- **Description**: Search for subjects
- **Query Parameters**: `q` (query)
- **Access**: Student only

---

## 👤 Profile Management Endpoints

### Profile Viewing
- **GET** `/profile_v2/view`
- **Description**: View user profile
- **Access**: All authenticated users

### Profile Editing
- **GET** `/profile_v2/edit`
- **Description**: Edit profile form
- **Access**: All authenticated users

- **POST** `/profile_v2/edit`
- **Description**: Update profile information
- **Body**: `{ "full_name": "string", "email": "string" }`
- **Access**: All authenticated users

### Password Management
- **GET** `/profile_v2/change_password`
- **Description**: Change password form
- **Access**: All authenticated users

- **POST** `/profile_v2/change_password`
- **Description**: Change user password
- **Body**: `{ "current_password": "string", "new_password": "string", "confirm_password": "string" }`
- **Access**: All authenticated users

### Avatar Upload
- **POST** `/profile_v2/upload_avatar`
- **Description**: Upload profile picture
- **Body**: Form data with `profile_picture` file
- **Access**: All authenticated users
- **Response**: JSON with success status and file path

### Notifications
- **GET** `/profile_v2/notifications`
- **Description**: View user notifications
- **Access**: All authenticated users

- **POST** `/profile_v2/notifications/<notification_id>/read`
- **Description**: Mark notification as read
- **Access**: All authenticated users

- **POST** `/profile_v2/notifications/mark_all_read`
- **Description**: Mark all notifications as read
- **Access**: All authenticated users

---

## 📊 API Response Formats

### Success Response
```json
{
    "success": true,
    "message": "Operation completed successfully",
    "data": { ... }
}
```

### Error Response
```json
{
    "success": false,
    "error": "Error message describing what went wrong"
}
```

### Notification Response
```json
{
    "id": 1,
    "title": "Notification Title",
    "message": "Notification message content",
    "type": "info|success|warning|error",
    "is_read": false,
    "created_at": "2024-01-01T12:00:00Z"
}
```

---

## 🔒 Security Considerations

- All endpoints require authentication
- Role-based access control enforced
- Input validation and sanitization
- SQL injection prevention
- XSS protection
- CSRF protection for state-changing operations

---

## 📝 Error Codes

- **200**: Success
- **302**: Redirect (after successful operations)
- **400**: Bad Request (validation errors)
- **401**: Unauthorized (not logged in)
- **403**: Forbidden (insufficient permissions)
- **404**: Not Found
- **500**: Internal Server Error

---

## 🚀 Getting Started

1. **Start the application**: `python3 run.py`
2. **Access the application**: `http://localhost:5000`
3. **Login as admin**: Use `admin` / `admin123`
4. **Create users**: Use admin dashboard to add teachers and students
5. **Invite teachers**: Assign teachers to subjects
6. **Student enrollment**: Students can request enrollment in subjects

---

## 📚 Additional Resources

- [Database Schema Documentation](DATABASE_SCHEMA_V2.md)
- [User Guide](USER_GUIDE_V2.md)
- [Deployment Guide](DEPLOYMENT_GUIDE_V2.md)
- [Troubleshooting Guide](TROUBLESHOOTING_V2.md)

---

**Version**: 2.0  
**Last Updated**: September 2024  
**Author**: AgriQuest Development Team

