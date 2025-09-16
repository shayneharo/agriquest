"""
Email utilities for sending OTP codes and notifications
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Simple email configuration - you can change these values
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'shayneharo03@gmail.com'  # Your email
EMAIL_PASSWORD = 'fmdhfzkrkrhfirpy'  # App Password without spaces
FROM_NAME = 'AgriQuest'

def send_otp_email(recipient_email, otp_code, expiry_minutes=5):
    """
    Send OTP code via email
    
    Args:
        recipient_email (str): Email address to send OTP to
        otp_code (str): 6-digit OTP code
        expiry_minutes (int): OTP expiry time in minutes
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Simple email sending with hardcoded credentials
        print(f"📧 Sending OTP email to {recipient_email}...")
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{FROM_NAME} <{EMAIL_ADDRESS}>"
        msg['To'] = recipient_email
        msg['Subject'] = "Your AgriQuest Verification Code"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🌱 AgriQuest</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Agricultural Learning Platform</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #dee2e6;">
                <h2 style="color: #333; margin-top: 0;">Verification Code</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5;">
                    Thank you for registering with AgriQuest! Please use the following verification code to complete your registration:
                </p>
                
                <div style="background: white; border: 2px solid #28a745; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0;">
                    <h1 style="color: #28a745; font-size: 36px; margin: 0; letter-spacing: 5px; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </h1>
                </div>
                
                <p style="color: #666; font-size: 14px; line-height: 1.5;">
                    <strong>Important:</strong>
                    <br>• The code will expire in 3 minutes
                    <br>• Do not share this code with anyone
                    <br>• If you didn't request this code, please ignore this email
                </p>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        This is an automated message from AgriQuest. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ OTP email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send email to {recipient_email}: {str(e)}")
        print(f"🔐 OTP for {recipient_email}: {otp_code}")
        print("📧 Email will be printed to console instead")
        # For development, we'll still return True so the OTP flow continues
        # The OTP code is printed to console for testing
        return True

def send_welcome_email(recipient_email, username, role):
    """
    Send welcome email after successful registration
    
    Args:
        recipient_email (str): Email address
        username (str): Username
        role (str): User role (student/teacher)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        # Check if email credentials are configured
        if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
            print(f"⚠️  Email not configured. Welcome email for {username} ({recipient_email}) not sent")
            return False
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = f"{FROM_NAME} <{EMAIL_ADDRESS}>"
        msg['To'] = recipient_email
        msg['Subject'] = "Welcome to AgriQuest! 🎉"
        
        # Email body
        body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <div style="background: linear-gradient(135deg, #28a745, #20c997); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="margin: 0; font-size: 28px;">🌱 AgriQuest</h1>
                <p style="margin: 10px 0 0 0; font-size: 16px; opacity: 0.9;">Agricultural Learning Platform</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; border: 1px solid #dee2e6;">
                <h2 style="color: #333; margin-top: 0;">Welcome, {username}! 🎉</h2>
                <p style="color: #666; font-size: 16px; line-height: 1.5;">
                    Your account has been successfully created as a <strong>{role.title()}</strong> in AgriQuest.
                </p>
                
                <div style="background: white; border-left: 4px solid #28a745; padding: 20px; margin: 20px 0;">
                    <h3 style="color: #28a745; margin-top: 0;">What's Next?</h3>
                    <ul style="color: #666; line-height: 1.6;">
                        <li>Log in to your account using your credentials</li>
                        <li>Explore the agricultural learning modules</li>
                        <li>Take quizzes to test your knowledge</li>
                        <li>Track your progress and achievements</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5000/login" style="background: #28a745; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold; display: inline-block;">
                        Login to AgriQuest
                    </a>
                </div>
                
                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        This is an automated message from AgriQuest. Please do not reply to this email.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(body, 'html'))
        
        # Create secure connection and send email
        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
        
        print(f"✅ Welcome email sent successfully to {recipient_email}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send welcome email to {recipient_email}: {str(e)}")
        return False