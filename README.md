# 🌱 AgriQuest - Agricultural Learning Platform

A modern web application for agricultural education with interactive quizzes, class management, and user analytics.

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python3 run.py
```

**Access:** http://localhost:5000

## 🔑 Test Accounts

- **Teacher:** username='teacher', password='Teacher123!'
- **Student:** username='student', password='Student123!'

## ✨ Features

- **User Authentication** (Email + SMS OTP)
- **Role-Based Access** (Student, Teacher, Admin)
- **Interactive Quizzes** (Create, Take, Results)
- **Class Management** (Enrollment, Approval)
- **Analytics Dashboard** (Performance tracking)
- **Responsive Design** (Mobile-friendly)
- **Dark Mode** (Theme switching)
- **Hamburger Menu** (Modern navigation)

## 📚 Documentation

For detailed documentation, setup guides, and technical information, see:
**[CONSOLIDATED_DOCUMENTATION.md](CONSOLIDATED_DOCUMENTATION.md)**

## 🛠️ Configuration

### Email Setup
- Configure Gmail App Password in `backend/utils/email_utils.py`
- See: [GMAIL_APP_PASSWORD_SETUP.md](GMAIL_APP_PASSWORD_SETUP.md)

### SMS Setup
- Currently using console mode for testing
- Production: Twilio/TextBelt available

## 📱 Mobile Support

- **Responsive Design** (Mobile-first approach)
- **Touch-Friendly** interface
- **Hamburger Menu** (Collapsible navigation)
- **Progressive Web App** (Installable)

## 🎯 User Roles

### Students
- Browse and take quizzes
- Enroll in classes
- View performance analytics
- Track learning progress

### Teachers
- Create and manage quizzes
- Manage subjects
- Oversee class enrollments
- View student analytics

### Admins
- All teacher features
- User management
- System administration

## 🔧 Troubleshooting

### Common Issues
1. **Port 5000 in use** - Disable AirPlay Receiver in System Preferences
2. **Email not sending** - Check Gmail App Password setup
3. **OTP not working** - Verify email configuration

### Getting Help
- Check terminal logs for error messages
- Verify environment variables are set
- Test with provided test accounts

## 📄 License

This project is for educational purposes.

---

*Last Updated: $(date)*
*Status: ✅ Fully Functional*
*Version: 2.0 - Modern UI with Hamburger Menu*