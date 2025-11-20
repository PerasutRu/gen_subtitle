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
        
        # ตาราง sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                last_activity TEXT NOT NULL
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
        
        # สร้าง index
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_session_id 
            ON videos (session_id)
        """)
        
        conn.commit()
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
            
            # ลบ session
            cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting session: {e}")
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
                    "video_count": row[3],
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

# Global instance
db = Database()
