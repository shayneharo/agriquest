# PostgreSQL Setup Guide for AgriQuest

## 🚀 Quick Setup Options

### Option 1: Railway (Recommended - Free)
1. Go to [Railway.app](https://railway.app)
2. Sign up with GitHub
3. Click "New Project" → "Database" → "PostgreSQL"
4. Copy the connection string
5. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://postgres:password@host:port/railway"
   ```

### Option 2: Supabase (Free)
1. Go to [Supabase.com](https://supabase.com)
2. Create a new project
3. Go to Settings → Database
4. Copy the connection string
5. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://postgres:password@host:port/postgres"
   ```

### Option 3: Neon (Free)
1. Go to [Neon.tech](https://neon.tech)
2. Create a new project
3. Copy the connection string
4. Set environment variable:
   ```bash
   export DATABASE_URL="postgresql://username:password@host:port/database"
   ```

## 🔄 Migration Steps

1. **Set up PostgreSQL database** (using one of the options above)

2. **Set the DATABASE_URL environment variable:**
   ```bash
   export DATABASE_URL="your_postgresql_connection_string"
   ```

3. **Run the migration script:**
   ```bash
   python3 migrate_to_postgresql.py
   ```

4. **Test the migration:**
   ```bash
   python3 -c "
   import os
   from backend.config.database import get_db_connection
   
   # Set DATABASE_URL for testing
   os.environ['DATABASE_URL'] = 'your_postgresql_connection_string'
   
   conn = get_db_connection()
   cursor = conn.cursor()
   cursor.execute('SELECT COUNT(*) FROM users')
   count = cursor.fetchone()[0]
   print(f'✅ PostgreSQL working! Found {count} users')
   conn.close()
   "
   ```

5. **Start your application:**
   ```bash
   python3 run.py
   ```

## 🔧 Environment Variables

Create a `.env` file in your project root:
```env
DATABASE_URL=postgresql://username:password@host:port/database
```

## 🎯 Benefits of PostgreSQL

- **Better Performance**: Faster queries and better indexing
- **Advanced Features**: JSON support, full-text search, etc.
- **Scalability**: Handles larger datasets better
- **Production Ready**: Industry standard for production applications
- **ACID Compliance**: Better data integrity

## 🆘 Troubleshooting

### Connection Issues
- Check if DATABASE_URL is set correctly
- Verify database credentials
- Ensure database is accessible from your IP

### Migration Issues
- Make sure PostgreSQL database is empty
- Check if all required tables exist
- Verify data types match between SQLite and PostgreSQL

### Application Issues
- Restart your application after setting DATABASE_URL
- Check logs for connection errors
- Verify psycopg2 is installed

## 📊 Current Status

- ✅ **SQLite**: Working perfectly for development
- ✅ **PostgreSQL Support**: Ready to use
- ✅ **Migration Script**: Created and ready
- ✅ **Auto-detection**: App automatically switches to PostgreSQL when DATABASE_URL is set

Your application will continue working with SQLite until you set the DATABASE_URL environment variable!
