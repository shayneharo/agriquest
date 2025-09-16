"""
Database configuration for Render.com deployment
"""
import os
import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from urllib.parse import urlparse

def get_db_connection():
    """Get database connection based on environment"""
    database_url = os.getenv('DATABASE_URL')
    
    if database_url and database_url.startswith('postgres://'):
        # Parse the URL
        url = urlparse(database_url)
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        conn.cursor_factory = DictCursor
        return conn
    else:
        # Fallback to SQLite for local development
        conn = sqlite3.connect('agriquest.db')
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    """Initialize the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'student',
            email VARCHAR(255) UNIQUE,
            phone VARCHAR(20),
            full_name VARCHAR(100),
            profile_picture VARCHAR(255),
            is_active BOOLEAN DEFAULT TRUE,
            email_verified BOOLEAN DEFAULT FALSE,
            phone_verified BOOLEAN DEFAULT FALSE,
            last_login TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Add other table creation statements here...
    
    conn.commit()
    conn.close()