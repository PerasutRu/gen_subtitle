"""
Database service for storing session quota data
"""
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict
import json

class Database:
    def __init__(self, db_path: str = None):
        if db_path is None:
            backend_dir = Path(__file__).parent.parent
            db_path = backend_dir / "data" / "sessions.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """สร้างตารางในฐานข้อมูล"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ตาราง users
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TEXT NOT NULL,
                custom_limits TEXT
            )
        """)
        
        # ตาราง sessions (เพิ่ม user_id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                user_id INTEGER,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # ตาราง videos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_id TEXT NOT NULL,
                file_size_mb REAL NOT NULL,
                duration_seconds REAL NOT NULL,
                uploaded_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # ตาราง activity_logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                username TEXT,
                activity_type TEXT NOT NULL,
                file_id TEXT,
                details TEXT,
                status TEXT NOT NULL DEFAULT 'success',
                error_message TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES sessions (session_id)
            )
        """)
        
        # สร้าง index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON videos (session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_username 
            ON users (username)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_session 
            ON activity_logs (session_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_type 
            ON activity_logs (activity_type)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_activity_created 
            ON activity_logs (created_at)
        """)
        
        conn.commit()
        
        # สร้าง admin user เริ่มต้น (ถ้ายังไม่มี)
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = cursor.fetchone()[0]
        
        if admin_count == 0:
            # สร้าง admin user เริ่มต้น
            # username: admin, password: admin123
            from .auth_service import auth_service
            password_hash = auth_service.hash_password("admin123")
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
            """, ("admin", password_hash, "admin", now))
            
            conn.commit()
            print("✅ Created default admin user (username: admin, password: admin123)")
        
        conn.close()
    
    def create_session(self, session_id: str) -> bool:
        """สร้าง session ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT OR IGNORE INTO sessions (session_id, created_at, last_activity)
                VALUES (?, ?, ?)
            """, (session_id, now, now))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error creating session: {e}")
            return False
    
    def get_session(self, session_id: str) -> Optional[Dict]:
        """ดึงข้อมูล session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, created_at, last_activity
                FROM sessions
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    "session_id": row[0],
                    "created_at": row[1],
                    "last_activity": row[2]
                }
            return None
        except Exception as e:
            print(f"Error getting session: {e}")
            return None
    
    def add_video(self, session_id: str, file_id: str, file_size_mb: float, duration_seconds: float) -> bool:
        """เพิ่มวิดีโอเข้า session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # เพิ่มวิดีโอ
            cursor.execute("""
                INSERT INTO videos (session_id, file_id, file_size_mb, duration_seconds, uploaded_at)
                VALUES (?, ?, ?, ?, ?)
            """, (session_id, file_id, file_size_mb, duration_seconds, now))
            
            # อัปเดต last_activity
            cursor.execute("""
                UPDATE sessions
                SET last_activity = ?
                WHERE session_id = ?
            """, (now, session_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding video: {e}")
            return False
    
    def get_session_videos(self, session_id: str) -> List[Dict]:
        """ดึงรายการวิดีโอของ session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT file_id, file_size_mb, duration_seconds, uploaded_at
                FROM videos
                WHERE session_id = ?
                ORDER BY uploaded_at DESC
            """, (session_id,))
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "file_id": row[0],
                    "file_size_mb": row[1],
                    "duration_seconds": row[2],
                    "uploaded_at": row[3]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting videos: {e}")
            return []
    
    def get_session_usage(self, session_id: str) -> Dict:
        """ดึงข้อมูลการใช้งานของ session"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as video_count,
                    COALESCE(SUM(duration_seconds), 0) as total_duration
                FROM videos
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                "videos_count": row[0],
                "total_duration": row[1]
            }
        except Exception as e:
            print(f"Error getting usage: {e}")
            return {"videos_count": 0, "total_duration": 0}
    
    def delete_session(self, session_id: str) -> bool:
        """ลบ session และวิดีโอทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ลบวิดีโอ
            cursor.execute("DELETE FROM videos WHERE session_id = ?", (session_id,))
            videos_deleted = cursor.rowcount
            
            # ลบ session
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            sessions_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            # Return True แม้ว่าไม่มี session (idempotent)
            # ถ้าไม่มี session ก็ถือว่าลบสำเร็จแล้ว
            print(f"✅ Deleted session {session_id}: {sessions_deleted} sessions, {videos_deleted} videos")
            return True
        except Exception as e:
            print(f"❌ Error deleting session {session_id}: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_all_sessions(self) -> List[Dict]:
        """ดึงรายการ session ทั้งหมด (สำหรับ admin)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    s.session_id,
                    s.created_at,
                    s.last_activity,
                    COUNT(v.id) as video_count,
                    COALESCE(SUM(v.duration_seconds), 0) as total_duration
                FROM sessions s
                LEFT JOIN videos v ON s.session_id = v.session_id
                GROUP BY s.session_id
                ORDER BY s.last_activity DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "session_id": row[0],
                    "created_at": row[1],
                    "last_activity": row[2],
                    "videos_count": row[3],  # Changed to match other endpoints
                    "total_duration": row[4]
                }
                for row in rows
            ]
        except Exception as e:
            print(f"Error getting all sessions: {e}")
            return []
    
    def clear_all_sessions(self) -> bool:
        """ลบ session ทั้งหมด (สำหรับ admin reset)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM videos")
            cursor.execute("DELETE FROM sessions")
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error clearing all sessions: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """ดึงสถิติการใช้งานทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # จำนวน session
            cursor.execute("SELECT COUNT(*) FROM sessions")
            total_sessions = cursor.fetchone()[0]
            
            # จำนวนวิดีโอทั้งหมด
            cursor.execute("SELECT COUNT(*) FROM videos")
            total_videos = cursor.fetchone()[0]
            
            # ระยะเวลารวม
            cursor.execute("SELECT COALESCE(SUM(duration_seconds), 0) FROM videos")
            total_duration = cursor.fetchone()[0]
            
            # ขนาดไฟล์รวม
            cursor.execute("SELECT COALESCE(SUM(file_size_mb), 0) FROM videos")
            total_size = cursor.fetchone()[0]
            
            conn.close()
            
            return {
                "total_sessions": total_sessions,
                "total_videos": total_videos,
                "total_duration_seconds": total_duration,
                "total_duration_minutes": round(total_duration / 60, 2),
                "total_size_mb": round(total_size, 2),
                "total_size_gb": round(total_size / 1024, 2)
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    # ==================== User Management ====================
    
    def create_user(self, username: str, password_hash: str, role: str = "user") -> bool:
        """สร้าง user ใหม่"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO users (username, password_hash, role, created_at)
                VALUES (?, ?, ?, ?)
            """, (username, password_hash, role, now))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            # Username already exists
            return False
        except Exception as e:
            print(f"Error creating user: {e}")
            return False
    
    def get_user(self, username: str) -> Optional[Dict]:
        """ดึงข้อมูล user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, password_hash, role, created_at, custom_limits
                FROM users
                WHERE username = ?
            """, (username,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                user_data = {
                    "id": row[0],
                    "username": row[1],
                    "password_hash": row[2],
                    "role": row[3],
                    "created_at": row[4]
                }
                
                # Parse custom_limits JSON if exists
                if row[5]:
                    try:
                        user_data["custom_limits"] = json.loads(row[5])
                    except:
                        user_data["custom_limits"] = None
                else:
                    user_data["custom_limits"] = None
                
                return user_data
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    def get_all_users(self) -> List[Dict]:
        """ดึงรายการ user ทั้งหมด"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, username, role, created_at, custom_limits
                FROM users
                ORDER BY created_at DESC
            """)
            
            rows = cursor.fetchall()
            conn.close()
            
            users = []
            for row in rows:
                user_data = {
                    "id": row[0],
                    "username": row[1],
                    "role": row[2],
                    "created_at": row[3]
                }
                
                # Parse custom_limits JSON if exists
                if row[4]:
                    try:
                        user_data["custom_limits"] = json.loads(row[4])
                    except:
                        user_data["custom_limits"] = None
                else:
                    user_data["custom_limits"] = None
                
                users.append(user_data)
            
            return users
        except Exception as e:
            print(f"Error getting users: {e}")
            return []
    
    def delete_user(self, username: str) -> bool:
        """ลบ user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM users WHERE username = ?", (username,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user: {e}")
            return False
    
    def update_user_role(self, username: str, role: str) -> bool:
        """อัปเดต role ของ user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET role = ?
                WHERE username = ?
            """, (role, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating user role: {e}")
            return False
    
    # ==================== Custom Limits Management ====================
    
    def get_user_limits(self, username: str) -> Optional[Dict]:
        """ดึง custom limits ของ user"""
        user = self.get_user(username)
        if user:
            return user.get("custom_limits")
        return None
    
    def set_user_limits(self, username: str, limits: Dict) -> bool:
        """ตั้งค่า custom limits ให้ user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            limits_json = json.dumps(limits)
            
            cursor.execute("""
                UPDATE users
                SET custom_limits = ?
                WHERE username = ?
            """, (limits_json, username))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error setting user limits: {e}")
            return False
    
    def delete_user_limits(self, username: str) -> bool:
        """ลบ custom limits ของ user (ใช้ default)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users
                SET custom_limits = NULL
                WHERE username = ?
            """, (username,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting user limits: {e}")
            return False
    
    # ==================== Activity Logging ====================
    
    def log_activity(
        self,
        session_id: str,
        activity_type: str,
        file_id: Optional[str] = None,
        details: Optional[Dict] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> bool:
        """บันทึก activity log (with duplicate prevention)"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()
            
            # Extract username from session_id if possible
            username = None
            if session_id.startswith("user_"):
                username = session_id.replace("user_", "")
            
            # Convert details to JSON
            details_json = json.dumps(details) if details else None
            
            # Check for duplicate within last 5 seconds (prevent React StrictMode duplicates)
            # Calculate 5 seconds ago in ISO format
            from datetime import timedelta
            five_seconds_ago = (datetime.now() - timedelta(seconds=5)).isoformat()
            
            cursor.execute("""
                SELECT id FROM activity_logs 
                WHERE session_id = ? 
                AND activity_type = ? 
                AND file_id = ?
                AND status = ?
                AND created_at > ?
                LIMIT 1
            """, (session_id, activity_type, file_id, status, five_seconds_ago))
            
            existing = cursor.fetchone()
            
            if existing:
                # Duplicate detected, skip logging
                print(f"⚠️ Duplicate activity log prevented: {activity_type} for {file_id}")
                conn.close()
                return True
            
            # Insert new log
            cursor.execute("""
                INSERT INTO activity_logs 
                (session_id, username, activity_type, file_id, details, status, error_message, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (session_id, username, activity_type, file_id, details_json, status, error_message, now))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error logging activity: {e}")
            return False
    
    def get_activities(
        self,
        limit: int = 50,
        offset: int = 0,
        activity_type: Optional[str] = None,
        session_id: Optional[str] = None,
        username: Optional[str] = None,
        status: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None
    ) -> Dict:
        """ดึง activity logs พร้อม filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query with filters
            where_clauses = []
            params = []
            
            if activity_type:
                where_clauses.append("activity_type = ?")
                params.append(activity_type)
            
            if session_id:
                where_clauses.append("session_id = ?")
                params.append(session_id)
            
            if username:
                where_clauses.append("username = ?")
                params.append(username)
            
            if status:
                where_clauses.append("status = ?")
                params.append(status)
            
            if date_from:
                where_clauses.append("created_at >= ?")
                params.append(date_from)
            
            if date_to:
                where_clauses.append("created_at <= ?")
                params.append(date_to)
            
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"
            
            # Get total count
            cursor.execute(f"SELECT COUNT(*) FROM activity_logs WHERE {where_sql}", params)
            total = cursor.fetchone()[0]
            
            # Get activities with pagination
            query = f"""
                SELECT id, session_id, username, activity_type, file_id, 
                       details, status, error_message, created_at
                FROM activity_logs
                WHERE {where_sql}
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(query, params + [limit, offset])
            
            rows = cursor.fetchall()
            conn.close()
            
            activities = []
            for row in rows:
                activity = {
                    "id": row[0],
                    "session_id": row[1],
                    "username": row[2],
                    "activity_type": row[3],
                    "file_id": row[4],
                    "status": row[6],
                    "error_message": row[7],
                    "created_at": row[8]
                }
                
                # Parse details JSON
                if row[5]:
                    try:
                        activity["details"] = json.loads(row[5])
                    except:
                        activity["details"] = {}
                else:
                    activity["details"] = {}
                
                activities.append(activity)
            
            return {
                "total": total,
                "activities": activities,
                "limit": limit,
                "offset": offset
            }
        except Exception as e:
            print(f"Error getting activities: {e}")
            return {"total": 0, "activities": [], "limit": limit, "offset": offset}
    
    def get_activity_stats(self) -> Dict:
        """ดึงสถิติ activities"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total activities
            cursor.execute("SELECT COUNT(*) FROM activity_logs")
            total_activities = cursor.fetchone()[0]
            
            # Activities by type
            cursor.execute("""
                SELECT activity_type, COUNT(*) as count
                FROM activity_logs
                GROUP BY activity_type
            """)
            by_type = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Success rate
            cursor.execute("""
                SELECT status, COUNT(*) as count
                FROM activity_logs
                GROUP BY status
            """)
            by_status = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Provider usage (from details JSON)
            cursor.execute("""
                SELECT details FROM activity_logs 
                WHERE activity_type IN ('transcribe', 'translate')
                AND details IS NOT NULL
            """)
            provider_counts = {"openai": 0, "botnoi": 0}
            language_counts = {}
            
            for row in cursor.fetchall():
                try:
                    details = json.loads(row[0])
                    if "provider" in details:
                        provider = details["provider"]
                        provider_counts[provider] = provider_counts.get(provider, 0) + 1
                    if "target_language" in details:
                        lang = details["target_language"]
                        language_counts[lang] = language_counts.get(lang, 0) + 1
                except:
                    pass
            
            # Recent activities (last 7 days)
            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM activity_logs
                WHERE created_at >= datetime('now', '-7 days')
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """)
            recent_by_date = [{"date": row[0], "count": row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                "total_activities": total_activities,
                "by_type": by_type,
                "by_status": by_status,
                "provider_usage": provider_counts,
                "language_usage": language_counts,
                "recent_by_date": recent_by_date
            }
        except Exception as e:
            print(f"Error getting activity stats: {e}")
            return {}

# Global instance
db = Database()
