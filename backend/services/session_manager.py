"""
Session Manager for tracking video upload quotas per session
"""
import json
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime
import uuid
from .database import db

class SessionManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            # Get the backend directory path
            backend_dir = Path(__file__).parent.parent
            config_path = backend_dir / "config" / "limits.json"
        self.config_path = Path(config_path)
        self.limits = self._load_limits()
        self.db = db
    
    def _load_limits(self) -> dict:
        """โหลดค่า limits จาก config file"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # Default limits if config file not found
            return {
                "maxVideos": 10,
                "maxDurationMinutes": 10,
                "maxFileSizeMB": 500,
                "allowedFormats": ["video/mp4", "video/quicktime", "video/x-msvideo"],
                "allowedExtensions": [".mp4", ".mov", ".avi", ".mkv", ".wmv"]
            }
    
    def reload_limits(self):
        """โหลดค่า limits ใหม่ (สำหรับกรณีแก้ไข config)"""
        self.limits = self._load_limits()
    
    def get_or_create_session(self, session_id: Optional[str] = None) -> str:
        """สร้างหรือดึง session"""
        if not session_id:
            # Create new session with UUID
            session_id = str(uuid.uuid4())
        
        # Create session in database if not exists
        existing = self.db.get_session(session_id)
        if not existing:
            self.db.create_session(session_id)
        
        return session_id
    
    def get_session_usage(self, session_id: str) -> dict:
        """ดึงข้อมูลการใช้งานของ session"""
        usage = self.db.get_session_usage(session_id)
        
        return {
            "videos_count": usage["videos_count"],
            "total_duration": usage["total_duration"],
            "remaining_videos": self.limits["maxVideos"] - usage["videos_count"],
            "remaining_duration": (self.limits["maxDurationMinutes"] * 60) - usage["total_duration"]
        }
    
    def can_upload(self, session_id: str, file_size_mb: float, duration_seconds: float = 0) -> tuple[bool, str]:
        """
        เช็คว่าสามารถ upload ได้หรือไม่
        
        Returns:
            tuple: (can_upload: bool, error_message: str)
        """
        # Check file size
        if file_size_mb > self.limits["maxFileSizeMB"]:
            return False, f"ขนาดไฟล์เกิน {self.limits['maxFileSizeMB']} MB (ไฟล์ของคุณ: {file_size_mb:.2f} MB)"
        
        # Get session usage from database
        usage = self.db.get_session_usage(session_id)
        
        # Check video count
        if usage["videos_count"] >= self.limits["maxVideos"]:
            return False, f"คุณ upload ครบ {self.limits['maxVideos']} วิดีโอแล้ว"
        
        # Check duration (if provided)
        if duration_seconds > 0:
            max_duration = self.limits["maxDurationMinutes"] * 60
            if duration_seconds > max_duration:
                return False, f"ความยาววิดีโอเกิน {self.limits['maxDurationMinutes']} นาที (วิดีโอของคุณ: {duration_seconds/60:.2f} นาที)"
        
        return True, ""
    
    def add_video(self, session_id: str, file_id: str, file_size_mb: float, duration_seconds: float):
        """เพิ่มวิดีโอเข้า session"""
        # Ensure session exists
        self.get_or_create_session(session_id)
        
        # Add video to database
        self.db.add_video(session_id, file_id, file_size_mb, duration_seconds)
    
    def get_limits(self) -> dict:
        """ดึงค่า limits ปัจจุบัน"""
        return self.limits.copy()
    
    def clear_session(self, session_id: str):
        """ลบ session (สำหรับ testing หรือ reset)"""
        self.db.delete_session(session_id)
    
    def get_all_sessions(self):
        """ดึงรายการ session ทั้งหมด (สำหรับ admin)"""
        return self.db.get_all_sessions()
    
    def clear_all_sessions(self):
        """ลบ session ทั้งหมด (สำหรับ admin)"""
        return self.db.clear_all_sessions()
    
    def get_stats(self):
        """ดึงสถิติการใช้งาน (สำหรับ admin)"""
        return self.db.get_stats()

# Global instance
session_manager = SessionManager()
