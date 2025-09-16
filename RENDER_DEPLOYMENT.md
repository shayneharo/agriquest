# AgriQuest - Render Deployment

## 🚀 Quick Deploy to Render

### 1. Push to GitHub
```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### 2. Deploy on Render
1. Go to [Render.com](https://render.com)
2. Sign up with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Select your AgriQuest repository

### 3. Configure Render Service
- **Build Command**: `pip install -r requirements.txt && python migrate_to_postgresql.py`
- **Start Command**: `python run.py`
- **Environment**: Python 3

### 4. Add Environment Variables
In your Render service settings, add:
- `DATABASE_URL`: Your Render PostgreSQL connection string (Internal Database URL)
- `FLASK_ENV`: `production`
- `SECRET_KEY`: Generate a random string

### 5. Deploy!
Click "Create Web Service" and wait for deployment.

## 📊 Database Migration

The migration will happen automatically during deployment:
- ✅ Creates PostgreSQL schema
- ✅ Migrates all SQLite data
- ✅ Sets up indexes and constraints
- ✅ Preserves all user data

## 🔧 Troubleshooting

### Migration Issues
- Check that DATABASE_URL is set correctly
- Ensure PostgreSQL database is accessible
- Check build logs for migration errors

### Application Issues
- Verify all environment variables are set
- Check application logs for errors
- Ensure port is set to 5000 or use PORT environment variable

## 📱 Access Your App

Once deployed, your app will be available at:
`https://your-app-name.onrender.com`

## 🎯 Features

- ✅ Role-based access (Admin, Teacher, Student)
- ✅ Quiz management system
- ✅ User management
- ✅ Subject management
- ✅ Real-time notifications
- ✅ PostgreSQL database
- ✅ Production-ready deployment
