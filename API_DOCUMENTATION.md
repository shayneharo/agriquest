# AgriQuest API Documentation v2.0

## Overview

The AgriQuest API provides comprehensive REST endpoints for a role-based agricultural learning platform. The API supports three user types: Admin (Adviser), Teacher, and Student, each with specific permissions and functionality.

## Base URL
```
http://localhost:5000/api
```

## Authentication

All API endpoints (except login and register) require authentication via session-based authentication. Include the session cookie in requests after logging in.

## Response Format

All API responses follow this format:
```json
{
  "message": "Success message",
  "data": { ... },
  "error": "Error message (if applicable)"
}
```

## Error Codes

- `400` - Bad Request (validation errors)
- `401` - Unauthorized (authentication required)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `409` - Conflict (duplicate resource)
- `500` - Internal Server Error

---

## Authentication APIs

### POST /auth/login
User login endpoint.

**Request Body:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "full_name": "Administrator",
    "email": "admin@example.com"
  }
}
```

### POST /auth/register
User registration endpoint (teacher, student only).

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "role": "teacher|student",
  "email": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "message": "Registration successful"
}
```

### POST /auth/logout
User logout endpoint.

**Response:**
```json
{
  "message": "Logout successful"
}
```

### POST /auth/change-password
Change user password.

**Request Body:**
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

### GET /auth/profile
Get user profile.

**Response:**
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "full_name": "Administrator",
    "email": "admin@example.com",
    "profile_picture": null,
    "last_login": "2025-09-16T14:30:00",
    "created_at": "2025-09-16T10:00:00"
  }
}
```

### PUT /auth/profile
Update user profile.

**Request Body:**
```json
{
  "full_name": "string",
  "email": "string"
}
```

**Response:**
```json
{
  "message": "Profile updated successfully"
}
```

---

## Admin APIs

### User Management

#### GET /admin/users
List all users (teachers + students).

**Query Parameters:**
- `role` (optional): Filter by role (teacher|student)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "teacher1",
      "role": "teacher",
      "full_name": "John Teacher",
      "email": "teacher1@example.com",
      "is_active": true,
      "created_at": "2025-09-16T10:00:00"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "total_pages": 3
}
```

#### POST /admin/users
Add new teacher/student.

**Request Body:**
```json
{
  "username": "string",
  "password": "string",
  "role": "teacher|student",
  "email": "string",
  "full_name": "string"
}
```

**Response:**
```json
{
  "message": "Teacher created successfully"
}
```

#### DELETE /admin/users/:id
Remove teacher/student.

**Response:**
```json
{
  "message": "User deleted successfully"
}
```

#### GET /admin/users/search
Search users.

**Query Parameters:**
- `query`: Search query (required)
- `role` (optional): Filter by role

**Response:**
```json
{
  "users": [
    {
      "id": 1,
      "username": "teacher1",
      "role": "teacher",
      "full_name": "John Teacher",
      "email": "teacher1@example.com"
    }
  ],
  "total": 1
}
```

### Subject Management

#### GET /admin/subjects
List all subjects.

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "Crop Science",
      "description": "Study of crop production and management",
      "created_by": 1,
      "created_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### POST /admin/subjects
Create subject.

**Request Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Response:**
```json
{
  "message": "Subject created successfully"
}
```

#### PUT /admin/subjects/:id
Update subject.

**Request Body:**
```json
{
  "name": "string",
  "description": "string"
}
```

**Response:**
```json
{
  "message": "Subject updated successfully"
}
```

#### DELETE /admin/subjects/:id
Remove subject.

**Response:**
```json
{
  "message": "Subject deleted successfully"
}
```

### Teacher Invitations

#### POST /admin/subjects/:id/invite-teacher
Invite teacher to manage subject.

**Request Body:**
```json
{
  "teacher_id": 1
}
```

**Response:**
```json
{
  "message": "Invitation sent successfully"
}
```

#### GET /admin/invitations
View sent invitations.

**Response:**
```json
{
  "invitations": [
    {
      "id": 1,
      "teacher_id": 2,
      "subject_id": 1,
      "status": "pending",
      "invited_at": "2025-09-16T10:00:00",
      "teacher_name": "teacher1",
      "teacher_full_name": "John Teacher",
      "subject_name": "Crop Science"
    }
  ]
}
```

### Student Weakness Tracking

#### GET /admin/students/:id/weakness
View a student's weak areas.

**Response:**
```json
{
  "student": {
    "id": 1,
    "username": "student1",
    "full_name": "Jane Student"
  },
  "weaknesses": [
    {
      "id": 1,
      "user_id": 1,
      "subject_id": 1,
      "weakness_type": "conceptual_understanding",
      "description": "Struggles with basic concepts",
      "created_at": "2025-09-16T10:00:00",
      "subject_name": "Crop Science"
    }
  ],
  "statistics": {
    "total_weaknesses": 5,
    "by_subject": [
      {
        "subject_name": "Crop Science",
        "weakness_count": 3
      }
    ]
  }
}
```

### Notifications

#### GET /admin/notifications
View notifications.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "title": "New User Registered",
      "message": "A new teacher has registered",
      "type": "info",
      "is_read": false,
      "created_at": "2025-09-16T10:00:00"
    }
  ],
  "unread_count": 5,
  "page": 1,
  "per_page": 20
}
```

---

## Teacher APIs

### Subject Management

#### GET /teacher/subjects
List subjects teacher is assigned to.

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "Crop Science",
      "description": "Study of crop production",
      "created_by": 1,
      "status": "accepted",
      "accepted_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### POST /teacher/subjects/:id/accept
Accept admin invitation to manage subject.

**Response:**
```json
{
  "message": "Invitation accepted successfully"
}
```

#### GET /teacher/subjects/:id/students
View students in subject.

**Response:**
```json
{
  "students": [
    {
      "id": 1,
      "username": "student1",
      "full_name": "Jane Student",
      "status": "approved",
      "approved_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### POST /teacher/subjects/:id/students/:studentId/approve
Approve student request to join subject.

**Response:**
```json
{
  "message": "Enrollment approved successfully"
}
```

#### DELETE /teacher/subjects/:id/students/:studentId
Remove student from subject.

**Response:**
```json
{
  "message": "Student removed successfully"
}
```

### Quiz Management

#### POST /teacher/subjects/:id/quizzes
Create quiz for subject.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "beginner|intermediate|advanced",
  "time_limit": 30,
  "deadline": "2025-09-20T23:59:59"
}
```

**Response:**
```json
{
  "message": "Quiz created successfully"
}
```

#### GET /teacher/subjects/:id/quizzes
View quizzes in subject.

**Response:**
```json
{
  "quizzes": [
    {
      "id": 1,
      "title": "Crop Science Quiz 1",
      "description": "Basic concepts quiz",
      "difficulty_level": "beginner",
      "time_limit": 30,
      "deadline": "2025-09-20T23:59:59",
      "created_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### PUT /teacher/quizzes/:id
Update quiz.

**Request Body:**
```json
{
  "title": "string",
  "description": "string",
  "difficulty_level": "beginner|intermediate|advanced",
  "time_limit": 30,
  "deadline": "2025-09-20T23:59:59"
}
```

**Response:**
```json
{
  "message": "Quiz updated successfully"
}
```

#### DELETE /teacher/quizzes/:id
Delete quiz.

**Response:**
```json
{
  "message": "Quiz deleted successfully"
}
```

### Student Monitoring

#### GET /teacher/subjects/:id/weakest-students
View weakest students in subject.

**Query Parameters:**
- `limit` (optional): Number of students to return (default: 10)

**Response:**
```json
{
  "students": [
    {
      "id": 1,
      "username": "student1",
      "full_name": "Jane Student",
      "weakness_count": 5
    }
  ]
}
```

#### GET /teacher/students/search
Search for students.

**Query Parameters:**
- `query`: Search query (required)

**Response:**
```json
{
  "students": [
    {
      "id": 1,
      "username": "student1",
      "full_name": "Jane Student",
      "email": "student1@example.com"
    }
  ],
  "total": 1
}
```

### Notifications

#### GET /teacher/notifications
View notifications.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "title": "New Quiz Available",
      "message": "A new quiz is now available",
      "type": "info",
      "is_read": false,
      "created_at": "2025-09-16T10:00:00"
    }
  ],
  "unread_count": 3,
  "page": 1,
  "per_page": 20
}
```

#### GET /teacher/pending-requests
View pending enrollment requests.

**Response:**
```json
{
  "requests": [
    {
      "id": 1,
      "student_id": 2,
      "subject_id": 1,
      "status": "pending",
      "requested_at": "2025-09-16T10:00:00",
      "student_name": "student1",
      "student_full_name": "Jane Student",
      "subject_name": "Crop Science"
    }
  ]
}
```

---

## Student APIs

### Enrollment

#### GET /student/subjects
List enrolled subjects.

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "Crop Science",
      "description": "Study of crop production",
      "created_by": 1,
      "status": "approved",
      "approved_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### GET /student/subjects/search
Search for available subjects.

**Query Parameters:**
- `query`: Search query (required)

**Response:**
```json
{
  "subjects": [
    {
      "id": 1,
      "name": "Crop Science",
      "description": "Study of crop production",
      "is_enrolled": true
    }
  ],
  "total": 1
}
```

#### POST /student/subjects/:id/request
Request to join subject.

**Response:**
```json
{
  "message": "Enrollment request submitted successfully"
}
```

#### DELETE /student/subjects/:id/leave
Leave subject.

**Response:**
```json
{
  "message": "Left subject successfully"
}
```

### Quiz

#### GET /student/subjects/:id/quizzes
List quizzes (only if enrolled).

**Response:**
```json
{
  "quizzes": [
    {
      "id": 1,
      "title": "Crop Science Quiz 1",
      "description": "Basic concepts quiz",
      "difficulty_level": "beginner",
      "time_limit": 30,
      "deadline": "2025-09-20T23:59:59",
      "is_open": true,
      "created_at": "2025-09-16T10:00:00"
    }
  ]
}
```

#### POST /student/quizzes/:id/submit
Submit quiz answers.

**Request Body:**
```json
{
  "answers": [1, 2, 3, 4, 1]
}
```

**Response:**
```json
{
  "message": "Quiz submitted successfully",
  "score": 4,
  "total_questions": 5,
  "percentage": 80.0
}
```

#### GET /student/quizzes/:id/result
View quiz result.

**Response:**
```json
{
  "quiz": {
    "id": 1,
    "title": "Crop Science Quiz 1",
    "subject_id": 1
  },
  "result": {
    "id": 1,
    "user_id": 1,
    "quiz_id": 1,
    "score": 4,
    "total_questions": 5,
    "timestamp": "2025-09-16T10:00:00"
  }
}
```

### Weakness Tracking

#### GET /student/weakness
View personal weak areas.

**Query Parameters:**
- `subject_id` (optional): Filter by subject

**Response:**
```json
{
  "weaknesses": [
    {
      "id": 1,
      "user_id": 1,
      "subject_id": 1,
      "weakness_type": "conceptual_understanding",
      "description": "Struggles with basic concepts",
      "created_at": "2025-09-16T10:00:00",
      "subject_name": "Crop Science"
    }
  ],
  "statistics": {
    "total_weaknesses": 5,
    "by_subject": [
      {
        "subject_name": "Crop Science",
        "weakness_count": 3
      }
    ]
  }
}
```

### Notifications

#### GET /student/notifications
View notifications.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "notifications": [
    {
      "id": 1,
      "user_id": 1,
      "title": "New Quiz Available",
      "message": "A new quiz is now available",
      "type": "info",
      "is_read": false,
      "created_at": "2025-09-16T10:00:00"
    }
  ],
  "unread_count": 2,
  "page": 1,
  "per_page": 20
}
```

#### GET /student/quiz-history
Get student's quiz history.

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 20)

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "user_id": 1,
      "quiz_id": 1,
      "score": 4,
      "total_questions": 5,
      "timestamp": "2025-09-16T10:00:00",
      "quiz_title": "Crop Science Quiz 1",
      "subject_name": "Crop Science"
    }
  ],
  "page": 1,
  "per_page": 20
}
```

---

## Role-Based Access Control

### Admin (Adviser)
- Full access to all endpoints
- Can manage users, subjects, and system settings
- Can invite teachers to subjects
- Can view all student weaknesses and analytics

### Teacher
- Can manage assigned subjects only
- Can create and manage quizzes for assigned subjects
- Can approve/reject student enrollment requests
- Can view student performance and weaknesses
- Cannot access admin-only endpoints

### Student
- Can enroll in subjects (with teacher approval)
- Can take quizzes for enrolled subjects only
- Can view personal weaknesses and quiz history
- Cannot access teacher or admin endpoints

---

## Database Schema

### Core Tables
- `users` - User accounts and profiles
- `subjects` - Subject/course information
- `quizzes` - Quiz definitions
- `questions` - Quiz questions and answers
- `results` - Quiz attempt results

### Relationship Tables
- `subject_teachers` - Teacher-subject assignments
- `student_subjects` - Student enrollment in subjects
- `notifications` - User notifications
- `weaknesses` - Student weakness tracking

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

```json
{
  "error": "Detailed error message",
  "code": "ERROR_CODE"
}
```

Common error scenarios:
- Invalid credentials (401)
- Insufficient permissions (403)
- Resource not found (404)
- Validation errors (400)
- Duplicate resources (409)

---

## Rate Limiting

Currently no rate limiting is implemented, but it's recommended for production use.

---

## Security Considerations

1. **Authentication**: Session-based authentication
2. **Authorization**: Role-based access control
3. **Input Validation**: All inputs are validated
4. **SQL Injection**: Parameterized queries used
5. **Password Security**: Passwords are hashed using Werkzeug

---

## Testing

Test the API using tools like:
- Postman
- curl
- Insomnia
- HTTPie

Example curl command:
```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'
```

