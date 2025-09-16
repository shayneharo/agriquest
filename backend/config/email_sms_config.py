"""
Email and SMS configuration settings
"""
import os

# Email Configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', '587')),
    'email_address': os.getenv('EMAIL_ADDRESS', ''),
    'email_password': os.getenv('EMAIL_PASSWORD', ''),
    'from_name': os.getenv('FROM_NAME', 'AgriQuest'),
    'enabled': bool(os.getenv('EMAIL_ADDRESS') and os.getenv('EMAIL_PASSWORD'))
}

# SMS Configuration
SMS_CONFIG = {
    'service': os.getenv('SMS_SERVICE', 'console'),  # console, twilio, textbelt
    'twilio_account_sid': os.getenv('TWILIO_ACCOUNT_SID', ''),
    'twilio_auth_token': os.getenv('TWILIO_AUTH_TOKEN', ''),
    'twilio_phone_number': os.getenv('TWILIO_PHONE_NUMBER', ''),
    'textbelt_api_key': os.getenv('TEXTBELT_API_KEY', 'textbelt'),
    'enabled': bool(
        (os.getenv('TWILIO_ACCOUNT_SID') and os.getenv('TWILIO_AUTH_TOKEN') and os.getenv('TWILIO_PHONE_NUMBER')) or
        (os.getenv('SMS_SERVICE') == 'textbelt')
    )
}

def get_email_status():
    """Get email configuration status"""
    if EMAIL_CONFIG['enabled']:
        return f"✅ Email configured ({EMAIL_CONFIG['email_address']})"
    else:
        return "⚠️  Email not configured (set EMAIL_ADDRESS and EMAIL_PASSWORD)"

def get_sms_status():
    """Get SMS configuration status"""
    if SMS_CONFIG['enabled']:
        if SMS_CONFIG['service'] == 'twilio':
            return f"✅ SMS configured (Twilio: {SMS_CONFIG['twilio_phone_number']})"
        elif SMS_CONFIG['service'] == 'textbelt':
            return "✅ SMS configured (TextBelt)"
        else:
            return "✅ SMS configured (Console mode)"
    else:
        return "⚠️  SMS not configured (set SMS_SERVICE and credentials)"

def print_configuration_status():
    """Print current email and SMS configuration status"""
    print("\n" + "="*60)
    print("📧 EMAIL & SMS CONFIGURATION STATUS")
    print("="*60)
    print(f"Email: {get_email_status()}")
    print(f"SMS:   {get_sms_status()}")
    print("="*60)
    
    if not EMAIL_CONFIG['enabled']:
        print("\n📧 To enable email sending, set these environment variables:")
        print("   export EMAIL_ADDRESS='your-email@gmail.com'")
        print("   export EMAIL_PASSWORD='your-app-password'")
        print("   export SMTP_SERVER='smtp.gmail.com'")
        print("   export SMTP_PORT='587'")
    
    if not SMS_CONFIG['enabled']:
        print("\n📱 To enable SMS sending, choose one option:")
        print("\n   Option 1 - Twilio (Recommended):")
        print("   export SMS_SERVICE='twilio'")
        print("   export TWILIO_ACCOUNT_SID='your-account-sid'")
        print("   export TWILIO_AUTH_TOKEN='your-auth-token'")
        print("   export TWILIO_PHONE_NUMBER='+1234567890'")
        print("\n   Option 2 - TextBelt (Free tier):")
        print("   export SMS_SERVICE='textbelt'")
        print("   export TEXTBELT_API_KEY='textbelt'")
    
    print("\n💡 For Gmail, use App Passwords instead of your regular password")
    print("   https://support.google.com/accounts/answer/185833")
    print("="*60)

