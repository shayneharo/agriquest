"""
Performance Testing with Locust
Load testing for AgriQuest application
"""

from locust import HttpUser, task, between
import random
import json

class AgriQuestUser(HttpUser):
    """Simulate user behavior on AgriQuest"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    def on_start(self):
        """Called when a user starts"""
        self.login()
    
    def login(self):
        """Login as a test user"""
        response = self.client.post("/login", data={
            "username": "testuser",
            "password": "TestPassword123!"
        })
        
        if response.status_code == 200:
            # Extract session cookie
            self.cookies = response.cookies
    
    @task(3)
    def view_dashboard(self):
        """View dashboard (most common action)"""
        self.client.get("/", cookies=self.cookies)
    
    @task(2)
    def view_classes(self):
        """View available classes"""
        self.client.get("/classes", cookies=self.cookies)
    
    @task(1)
    def view_quizzes(self):
        """View quizzes"""
        self.client.get("/", cookies=self.cookies)
    
    @task(1)
    def take_quiz(self):
        """Take a quiz"""
        # Get a random quiz ID
        quiz_id = random.randint(1, 10)
        self.client.get(f"/quiz/{quiz_id}", cookies=self.cookies)
    
    @task(1)
    def submit_quiz(self):
        """Submit quiz answers"""
        quiz_id = random.randint(1, 10)
        answers = {
            "question_1": "1",
            "question_2": "2",
            "question_3": "3"
        }
        self.client.post(f"/quiz/{quiz_id}/submit", data=answers, cookies=self.cookies)
    
    @task(1)
    def view_results(self):
        """View quiz results"""
        self.client.get("/results", cookies=self.cookies)
    
    @task(1)
    def view_analytics(self):
        """View analytics"""
        self.client.get("/analytics", cookies=self.cookies)

class TeacherUser(HttpUser):
    """Simulate teacher behavior"""
    
    wait_time = between(2, 5)
    
    def on_start(self):
        """Login as teacher"""
        response = self.client.post("/login", data={
            "username": "teacher",
            "password": "Teacher123!"
        })
        
        if response.status_code == 200:
            self.cookies = response.cookies
    
    @task(3)
    def view_teacher_dashboard(self):
        """View teacher dashboard"""
        self.client.get("/", cookies=self.cookies)
    
    @task(2)
    def create_quiz(self):
        """Create a new quiz"""
        quiz_data = {
            "title": f"Test Quiz {random.randint(1, 1000)}",
            "description": "Performance test quiz",
            "subject_id": "1",
            "difficulty_level": "beginner",
            "time_limit": "30"
        }
        self.client.post("/create_quiz", data=quiz_data, cookies=self.cookies)
    
    @task(1)
    def manage_classes(self):
        """Manage classes"""
        self.client.get("/my_classes", cookies=self.cookies)
    
    @task(1)
    def view_analytics(self):
        """View teacher analytics"""
        self.client.get("/analytics", cookies=self.cookies)

class AnonymousUser(HttpUser):
    """Simulate anonymous user behavior"""
    
    wait_time = between(1, 2)
    
    @task(5)
    def view_login_page(self):
        """View login page"""
        self.client.get("/login")
    
    @task(3)
    def view_register_page(self):
        """View registration page"""
        self.client.get("/register")
    
    @task(2)
    def attempt_login(self):
        """Attempt login with random credentials"""
        username = f"user{random.randint(1, 1000)}"
        password = f"password{random.randint(1, 1000)}"
        
        self.client.post("/login", data={
            "username": username,
            "password": password
        })
    
    @task(1)
    def attempt_registration(self):
        """Attempt registration"""
        user_data = {
            "username": f"newuser{random.randint(1, 10000)}",
            "password": "NewPassword123!",
            "email": f"user{random.randint(1, 10000)}@example.com",
            "phone": f"+1234567{random.randint(100, 999)}",
            "role": "student"
        }
        self.client.post("/register", data=user_data)

class APIUser(HttpUser):
    """Simulate API usage"""
    
    wait_time = between(0.5, 1.5)
    
    def on_start(self):
        """Get API token"""
        response = self.client.post("/api/auth/login", json={
            "username": "testuser",
            "password": "TestPassword123!"
        })
        
        if response.status_code == 200:
            data = response.json()
            self.token = data.get("access_token")
            self.headers = {"Authorization": f"Bearer {self.token}"}
    
    @task(3)
    def get_quizzes(self):
        """Get quizzes via API"""
        self.client.get("/api/quizzes", headers=self.headers)
    
    @task(2)
    def get_user_profile(self):
        """Get user profile via API"""
        self.client.get("/api/user/profile", headers=self.headers)
    
    @task(1)
    def get_analytics(self):
        """Get analytics via API"""
        self.client.get("/api/analytics", headers=self.headers)
    
    @task(1)
    def create_quiz_api(self):
        """Create quiz via API"""
        quiz_data = {
            "title": f"API Quiz {random.randint(1, 1000)}",
            "description": "API test quiz",
            "subject_id": 1,
            "difficulty_level": "beginner",
            "time_limit": 30
        }
        self.client.post("/api/quizzes", json=quiz_data, headers=self.headers)

# Performance test scenarios
class HighLoadTest(HttpUser):
    """High load test scenario"""
    
    wait_time = between(0.1, 0.5)  # Very fast requests
    
    @task(10)
    def rapid_requests(self):
        """Make rapid requests"""
        self.client.get("/health")
    
    @task(5)
    def rapid_login_attempts(self):
        """Rapid login attempts"""
        self.client.post("/login", data={
            "username": f"user{random.randint(1, 1000)}",
            "password": "wrongpassword"
        })

class StressTest(HttpUser):
    """Stress test scenario"""
    
    wait_time = between(0.05, 0.2)  # Extremely fast requests
    
    @task(20)
    def stress_requests(self):
        """Stress test requests"""
        self.client.get("/")
    
    @task(10)
    def stress_database(self):
        """Stress test database operations"""
        self.client.get("/classes")
    
    @task(5)
    def stress_file_operations(self):
        """Stress test file operations"""
        self.client.get("/static/style.css")

