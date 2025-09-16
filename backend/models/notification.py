"""
Notification Model for AgriQuest v2.0

This module handles all notification-related database operations including
creation, retrieval, marking as read, and deletion of notifications for
users across all roles (Admin, Teacher, Student).

Classes:
    Notification: Main class for notification operations

Methods:
    create_notification: Create a new notification
    get_user_notifications: Get notifications for a specific user
    mark_as_read: Mark a notification as read
    mark_all_as_read: Mark all notifications as read for a user
    delete_notification: Delete a specific notification
    get_unread_count: Get count of unread notifications for a user

Author: AgriQuest Development Team
Version: 2.0
"""

from ..config.database import get_db_connection
import sqlite3

class Notification:
    @staticmethod
    def create_notification(user_id, title, message, notification_type='info'):
        """Create a new notification for a user"""
        conn = get_db_connection()
        try:
            conn.execute("""
                INSERT INTO notifications (user_id, title, message, type, created_at) 
                VALUES (?, ?, ?, ?, datetime('now'))
            """, (user_id, title, message, notification_type))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error creating notification: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_user_notifications(user_id, limit=50, offset=0):
        """Get notifications for a specific user"""
        conn = get_db_connection()
        try:
            notifications = conn.execute("""
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ? OFFSET ?
            """, (user_id, limit, offset)).fetchall()
            return [dict(notification) for notification in notifications]
        except sqlite3.Error as e:
            print(f"Error getting notifications: {e}")
            return []
        finally:
            conn.close()
    
    @staticmethod
    def mark_as_read(notification_id, user_id):
        """Mark a specific notification as read"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE notifications 
                SET is_read = 1 
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error marking notification as read: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def mark_all_as_read(user_id):
        """Mark all notifications as read for a user"""
        conn = get_db_connection()
        try:
            conn.execute("""
                UPDATE notifications 
                SET is_read = 1 
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error marking all notifications as read: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def delete_notification(notification_id, user_id):
        """Delete a specific notification"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM notifications 
                WHERE id = ? AND user_id = ?
            """, (notification_id, user_id))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error deleting notification: {e}")
            return False
        finally:
            conn.close()
    
    @staticmethod
    def get_unread_count(user_id):
        """Get count of unread notifications for a user"""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM notifications 
                WHERE user_id = ? AND is_read = 0
            """, (user_id,))
            count = cursor.fetchone()[0]
            return count
        except sqlite3.Error as e:
            print(f"Error getting unread count: {e}")
            return 0
        finally:
            conn.close()
    
    @staticmethod
    def get_recent_notifications(user_id, limit=5):
        """Get recent notifications for dashboard display"""
        conn = get_db_connection()
        try:
            notifications = conn.execute("""
                SELECT * FROM notifications 
                WHERE user_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (user_id, limit)).fetchall()
            return [dict(notification) for notification in notifications]
        except sqlite3.Error as e:
            print(f"Error getting recent notifications: {e}")
            return []
        finally:
            conn.close()