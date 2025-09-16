"""
OTP Utilities
Handles OTP generation, validation, and storage with enhanced security
"""

import random
import string
import time
import hashlib
import secrets
from datetime import datetime, timedelta
import sqlite3
from .email_utils import send_otp_email, send_welcome_email

def generate_otp(length=6):
    """
    Generate a cryptographically secure random OTP
    Uses secrets module for better security than random
    """
    if length < 4 or length > 8:
        length = 6  # Default to 6 digits for security
    
    # Generate secure random number
    min_val = 10 ** (length - 1)
    max_val = (10 ** length) - 1
    return str(secrets.randbelow(max_val - min_val + 1) + min_val)

def generate_otp_alternative(length=6):
    """
    Alternative OTP generation using string digits
    """
    return ''.join(secrets.choice(string.digits) for _ in range(length))

def hash_otp(otp_code, phone):
    """
    Hash OTP with phone number as salt for additional security
    """
    salt = phone + "agriquest_salt_2024"  # Add application-specific salt
    return hashlib.sha256((otp_code + salt).encode()).hexdigest()

def verify_otp_hash(otp_code, phone, stored_hash):
    """
    Verify OTP against stored hash
    """
    computed_hash = hash_otp(otp_code, phone)
    return computed_hash == stored_hash

def create_otp_table():
    """Create OTP table with enhanced security features"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Check if otp_codes table exists and has the required columns
    c.execute("PRAGMA table_info(otp_codes)")
    columns = [column[1] for column in c.fetchall()]
    
    if not columns:
        # Create new table with enhanced security features
        c.execute('''CREATE TABLE otp_codes
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      phone TEXT NOT NULL,
                      otp_hash TEXT NOT NULL,
                      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                      expires_at DATETIME NOT NULL,
                      used BOOLEAN DEFAULT FALSE,
                      attempt_count INTEGER DEFAULT 0,
                      max_attempts INTEGER DEFAULT 3)''')
    else:
        # Check if we need to migrate from email to phone
        if 'email' in columns and 'phone' not in columns:
            # Rename email column to phone
            c.execute("ALTER TABLE otp_codes RENAME COLUMN email TO phone")
        elif 'phone' not in columns:
            # Add phone column if it doesn't exist
            c.execute("ALTER TABLE otp_codes ADD COLUMN phone TEXT")
        
        # Add new security columns if they don't exist
        if 'otp_hash' not in columns:
            c.execute("ALTER TABLE otp_codes ADD COLUMN otp_hash TEXT")
        if 'attempt_count' not in columns:
            c.execute("ALTER TABLE otp_codes ADD COLUMN attempt_count INTEGER DEFAULT 0")
        if 'max_attempts' not in columns:
            c.execute("ALTER TABLE otp_codes ADD COLUMN max_attempts INTEGER DEFAULT 3")
        
        # Remove old otp_code column if it exists (we now use otp_hash)
        if 'otp_code' in columns:
            # Check if otp_codes_new already exists and drop it first
            c.execute("DROP TABLE IF EXISTS otp_codes_new")
            
            # SQLite doesn't support DROP COLUMN directly, so we need to recreate the table
            c.execute('''CREATE TABLE otp_codes_new
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          phone TEXT NOT NULL,
                          otp_hash TEXT NOT NULL,
                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                          expires_at DATETIME NOT NULL,
                          used BOOLEAN DEFAULT FALSE,
                          attempt_count INTEGER DEFAULT 0,
                          max_attempts INTEGER DEFAULT 3)''')
            
            # Copy data from old table to new table, handling NULL otp_hash values
            c.execute('''INSERT INTO otp_codes_new (id, phone, otp_hash, created_at, expires_at, used, attempt_count, max_attempts)
                         SELECT id, phone, 
                                CASE 
                                    WHEN otp_hash IS NULL OR otp_hash = '' THEN 'migrated_' || id
                                    ELSE otp_hash 
                                END as otp_hash,
                                created_at, expires_at, used, 
                                COALESCE(attempt_count, 0) as attempt_count,
                                COALESCE(max_attempts, 3) as max_attempts
                         FROM otp_codes''')
            
            # Drop old table and rename new table
            c.execute("DROP TABLE otp_codes")
            c.execute("ALTER TABLE otp_codes_new RENAME TO otp_codes")
    
    conn.commit()
    conn.close()

def store_otp(phone, otp_code, expiry_minutes=5):
    """Store OTP hash in database with expiry time and security features"""
    create_otp_table()
    
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Invalidate any existing OTPs for this phone
    c.execute("UPDATE otp_codes SET used = TRUE WHERE phone = ?", (phone,))
    
    # Calculate expiry time
    expires_at = datetime.now() + timedelta(minutes=expiry_minutes)
    
    # Hash the OTP for secure storage
    otp_hash = hash_otp(otp_code, phone)
    
    # Store new OTP hash with security features
    c.execute("""INSERT INTO otp_codes (phone, otp_hash, expires_at, attempt_count, max_attempts) 
                 VALUES (?, ?, ?, 0, 3)""",
              (phone, otp_hash, expires_at))
    
    conn.commit()
    conn.close()
    
    # Return the plain OTP for sending (not stored in plaintext)
    return otp_code

def validate_otp(phone, otp_code):
    """
    Validate OTP with enhanced security features including retry limits
    Returns (is_valid, error_message)
    """
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Get the most recent unused OTP for this phone
    c.execute("""SELECT otp_hash, expires_at, attempt_count, max_attempts FROM otp_codes 
                 WHERE phone = ? AND used = FALSE 
                 ORDER BY created_at DESC LIMIT 1""", (phone,))
    
    result = c.fetchone()
    
    if not result:
        conn.close()
        return False, "No valid OTP found for this phone number"
    
    stored_hash, expires_at, attempt_count, max_attempts = result
    
    # Check if max attempts exceeded
    if attempt_count >= max_attempts:
        conn.close()
        return False, "Maximum OTP attempts exceeded. Please request a new OTP"
    
    # Check if OTP has expired
    if datetime.now() >= datetime.fromisoformat(expires_at):
        conn.close()
        return False, "OTP has expired. Please request a new OTP"
    
    # Verify OTP hash
    if verify_otp_hash(otp_code, phone, stored_hash):
        # Mark OTP as used
        c.execute("UPDATE otp_codes SET used = TRUE WHERE phone = ? AND otp_hash = ?",
                  (phone, stored_hash))
        conn.commit()
        conn.close()
        return True, "OTP verified successfully"
    else:
        # Increment attempt count
        c.execute("""UPDATE otp_codes SET attempt_count = attempt_count + 1 
                     WHERE phone = ? AND otp_hash = ?""",
                  (phone, stored_hash))
        conn.commit()
        conn.close()
        
        remaining_attempts = max_attempts - (attempt_count + 1)
        if remaining_attempts > 0:
            return False, f"Invalid OTP. {remaining_attempts} attempts remaining"
        else:
            return False, "Maximum OTP attempts exceeded. Please request a new OTP"

def mark_otp_used(phone, otp_code):
    """Mark OTP as used (legacy function - now handled in validate_otp)"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Find OTP by hash
    otp_hash = hash_otp(otp_code, phone)
    c.execute("UPDATE otp_codes SET used = TRUE WHERE phone = ? AND otp_hash = ?",
              (phone, otp_hash))
    
    conn.commit()
    conn.close()

def cleanup_expired_otps():
    """Remove expired OTPs from database"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    c.execute("DELETE FROM otp_codes WHERE expires_at < ?", (datetime.now(),))
    
    conn.commit()
    conn.close()

def get_otp_attempts_remaining(phone):
    """Get remaining OTP attempts for a phone number"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    c.execute("""SELECT attempt_count, max_attempts FROM otp_codes 
                 WHERE phone = ? AND used = FALSE 
                 ORDER BY created_at DESC LIMIT 1""", (phone,))
    
    result = c.fetchone()
    conn.close()
    
    if not result:
        return 3  # Default max attempts
    
    attempt_count, max_attempts = result
    return max(0, max_attempts - attempt_count)

def is_otp_rate_limited(phone, max_requests_per_hour=5):
    """Check if phone number is rate limited for OTP requests"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Count OTP requests in the last hour
    one_hour_ago = datetime.now() - timedelta(hours=1)
    c.execute("""SELECT COUNT(*) FROM otp_codes 
                 WHERE phone = ? AND created_at > ?""", (phone, one_hour_ago))
    
    count = c.fetchone()[0]
    conn.close()
    
    return count >= max_requests_per_hour

def migrate_otp_table():
    """Migrate OTP table from email to phone if needed"""
    conn = sqlite3.connect('agriquest.db')
    c = conn.cursor()
    
    # Check if table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='otp_codes'")
    if c.fetchone():
        # Check current structure
        c.execute("PRAGMA table_info(otp_codes)")
        columns = [column[1] for column in c.fetchall()]
        
        if 'email' in columns and 'phone' not in columns:
            # Drop the old table and create new one
            c.execute("DROP TABLE otp_codes")
            c.execute('''CREATE TABLE otp_codes
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          phone TEXT NOT NULL,
                          otp_code TEXT NOT NULL,
                          created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                          expires_at DATETIME NOT NULL,
                          used BOOLEAN DEFAULT FALSE)''')
    
    conn.commit()
    conn.close()

def send_otp_via_email(email, otp_code, expiry_minutes=5):
    """
    Send OTP code via email
    
    Args:
        email (str): Email address
        otp_code (str): OTP code
        expiry_minutes (int): OTP expiry time in minutes
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        return send_otp_email(email, otp_code, expiry_minutes)
    except Exception as e:
        print(f"❌ Error sending email OTP to {email}: {str(e)}")
        print(f"🔐 OTP for {email}: {otp_code}")
        return False


def send_welcome_notifications(email, username, role):
    """
    Send welcome notifications via email after successful registration
    
    Args:
        email (str): Email address
        username (str): Username
        role (str): User role
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    email_sent = False
    
    # Send welcome email
    try:
        email_sent = send_welcome_email(email, username, role)
    except Exception as e:
        print(f"❌ Error sending welcome email to {email}: {str(e)}")
    
    return email_sent
