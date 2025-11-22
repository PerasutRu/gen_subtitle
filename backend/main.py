from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from typing import List, Optional
from pydantic import BaseModel

from services.video_processor import VideoProcessor
from services.transcription_service import TranscriptionService
from services.translation_service import TranslationService
from services.botnoi_service import BotnoiService
from services.session_manager import session_manager
from services.auth_service import auth_service
from services.database import db
from models.subtitle_models import SubtitleResponse, TranslationRequest
from datetime import datetime

load_dotenv()

# Security
security = HTTPBearer()

# Pydantic models
class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "user"

app = FastAPI(title="Video Subtitle Generator API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
video_processor = VideoProcessor()
transcription_service = TranscriptionService()
translation_service = TranslationService()

# Initialize Botnoi service (optional)
botnoi_service = None
try:
    botnoi_service = BotnoiService()
except ValueError:
    print("Botnoi service not initialized (BOTNOI_API_KEY not found)")

# Create upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

# ==================== Auth Middleware ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """ตรวจสอบ JWT token และดึงข้อมูล user"""
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    username = payload.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return user

async def get_current_admin(current_user: dict = Depends(get_current_user)):
    """ตรวจสอบว่าเป็น admin หรือไม่"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# ==================== Public Endpoints ====================

@app.get("/")
async def root():
    return {"message": "Video Subtitle Generator API"}

@app.post("/auth/login")
async def login(request: LoginRequest):
    """Login และรับ JWT token"""
    user = db.get_user(request.username)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not auth_service.verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    # สร้าง JWT token
    access_token = auth_service.create_access_token(
        data={"sub": user["username"], "role": user["role"]}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    }

@app.get("/auth/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    """ดึงข้อมูล user ปัจจุบัน"""
    return {
        "username": current_user["username"],
        "role": current_user["role"],
        "created_at": current_user["created_at"]
    }

# ==================== Protected Endpoints ====================

@app.get("/limits")
async def get_limits(current_user: dict = Depends(get_current_user)):
    """ดึงค่า limits และ quota ปัจจุบัน"""
    return session_manager.get_limits()

@app.get("/session/{session_id}/usage")
async def get_session_usage(session_id: str, current_user: dict = Depends(get_current_user)):
    """ดึงข้อมูลการใช้งานของ session"""
    usage = session_manager.get_session_usage(session_id)
    # Get limits for this specific session (custom or default)
    limits = session_manager.get_limits_for_session(session_id)
    return {
        "usage": usage,
        "limits": limits
    }

# ==================== Admin Endpoints ====================

@app.post("/admin/register")
async def admin_register_user(
    request: RegisterRequest,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] สร้าง user ใหม่"""
    # Hash password
    password_hash = auth_service.hash_password(request.password)
    
    # สร้าง user
    success = db.create_user(request.username, password_hash, request.role)
    
    if not success:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    return {
        "message": f"สร้าง user {request.username} สำเร็จ",
        "username": request.username,
        "role": request.role
    }

@app.get("/admin/users")
async def admin_get_users(current_admin: dict = Depends(get_current_admin)):
    """[Admin] ดึงรายการ user ทั้งหมด"""
    users = db.get_all_users()
    return {
        "total": len(users),
        "users": users
    }

@app.delete("/admin/user/{username}")
async def admin_delete_user(
    username: str,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] ลบ user"""
    if username == current_admin["username"]:
        raise HTTPException(status_code=400, detail="Cannot delete yourself")
    
    success = db.delete_user(username)
    if success:
        return {"message": f"ลบ user {username} สำเร็จ"}
    else:
        raise HTTPException(status_code=500, detail="ไม่สามารถลบ user ได้")

@app.get("/admin/sessions")
async def admin_get_all_sessions(current_admin: dict = Depends(get_current_admin)):
    """[Admin] ดึงรายการ session ทั้งหมด"""
    sessions = session_manager.get_all_sessions()
    return {
        "total": len(sessions),
        "sessions": sessions
    }

@app.get("/admin/stats")
async def admin_get_stats(current_admin: dict = Depends(get_current_admin)):
    """[Admin] ดึงสถิติการใช้งานทั้งหมด"""
    stats = session_manager.get_stats()
    limits = session_manager.get_limits()
    return {
        "stats": stats,
        "limits": limits
    }

@app.delete("/admin/session/{session_id}")
async def admin_delete_session(
    session_id: str,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] ลบ session เฉพาะ"""
    success = session_manager.clear_session(session_id)
    if success:
        return {"message": f"ลบ session {session_id} สำเร็จ"}
    else:
        raise HTTPException(status_code=500, detail="ไม่สามารถลบ session ได้")

@app.post("/admin/reset")
async def admin_reset_all(current_admin: dict = Depends(get_current_admin)):
    """[Admin] Reset ลบ session ทั้งหมด"""
    success = session_manager.clear_all_sessions()
    if success:
        return {
            "message": "Reset สำเร็จ ลบ session ทั้งหมดแล้ว",
            "timestamp": datetime.now().isoformat()
        }
    else:
        raise HTTPException(status_code=500, detail="ไม่สามารถ reset ได้")

@app.post("/admin/reload-limits")
async def admin_reload_limits(current_admin: dict = Depends(get_current_admin)):
    """[Admin] โหลดค่า limits ใหม่จาก config file"""
    session_manager.reload_limits()
    return {
        "message": "โหลดค่า limits ใหม่สำเร็จ",
        "limits": session_manager.get_limits()
    }

@app.get("/admin/user/{username}/limits")
async def admin_get_user_limits(
    username: str,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] ดู custom limits ของ user"""
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    custom_limits = user.get("custom_limits")
    default_limits = session_manager.get_limits()
    
    return {
        "username": username,
        "custom_limits": custom_limits,
        "default_limits": default_limits,
        "active_limits": custom_limits if custom_limits else default_limits
    }

@app.put("/admin/user/{username}/limits")
async def admin_set_user_limits(
    username: str,
    limits: dict,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] ตั้งค่า custom limits ให้ user"""
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Validate limits
    required_fields = ["maxVideos", "maxDurationMinutes", "maxFileSizeMB"]
    for field in required_fields:
        if field not in limits:
            raise HTTPException(status_code=400, detail=f"Missing field: {field}")
        if not isinstance(limits[field], (int, float)) or limits[field] <= 0:
            raise HTTPException(status_code=400, detail=f"Invalid value for {field}")
    
    # Set custom limits
    success = db.set_user_limits(username, limits)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to set user limits")
    
    return {
        "message": f"ตั้งค่า limits สำหรับ {username} สำเร็จ",
        "username": username,
        "custom_limits": limits
    }

@app.delete("/admin/user/{username}/limits")
async def admin_delete_user_limits(
    username: str,
    current_admin: dict = Depends(get_current_admin)
):
    """[Admin] ลบ custom limits ของ user (ใช้ default)"""
    user = db.get_user(username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    success = db.delete_user_limits(username)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete user limits")
    
    return {
        "message": f"ลบ custom limits สำหรับ {username} สำเร็จ (ใช้ default limits)",
        "username": username
    }

@app.get("/user/session")
async def get_user_session(current_user: dict = Depends(get_current_user)):
    """ดึง session ของ user ปัจจุบัน"""
    # Use username as session_id for persistence
    username = current_user["username"]
    session_id = f"user_{username}"
    
    # Get or create session
    session_manager.get_or_create_session(session_id)
    
    # Get usage
    usage = session_manager.get_session_usage(session_id)
    
    # Get limits for this specific user (custom or default)
    limits = session_manager.get_limits_for_session(session_id)
    
    return {
        "session_id": session_id,
        "username": username,
        "usage": usage,
        "limits": limits
    }

@app.post("/upload-video")
async def upload_video(
    file: UploadFile = File(...),
    session_id: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user)
):
    """อัปโหลดไฟล์วิดีโอและแปลงเป็น MP3 พร้อมตรวจสอบ quota"""
    try:
        # Use username-based session for persistence
        username = current_user["username"]
        if not session_id:
            session_id = f"user_{username}"
        
        # Get or create session
        session_manager.get_or_create_session(session_id)
        
        # Validate file type
        limits = session_manager.get_limits()
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in limits["allowedExtensions"]:
            allowed = ", ".join(limits["allowedExtensions"])
            raise HTTPException(
                status_code=400, 
                detail=f"ไฟล์ต้องเป็น {allowed} เท่านั้น"
            )
        
        # Check file size (read file to get size)
        file_content = await file.read()
        file_size_mb = len(file_content) / (1024 * 1024)
        
        # Validate file size first (before checking duration)
        can_upload, error_msg = session_manager.can_upload(session_id, file_size_mb)
        if not can_upload:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        video_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        # Save uploaded file
        with open(video_path, "wb") as buffer:
            buffer.write(file_content)
        
        # Get video duration
        try:
            video_info = video_processor.get_video_info(video_path)
            duration_seconds = video_info["duration"]
        except Exception as e:
            print(f"Warning: Could not get video duration: {e}")
            duration_seconds = 0
        
        # Check duration limit
        if duration_seconds > 0:
            can_upload, error_msg = session_manager.can_upload(
                session_id, 
                file_size_mb, 
                duration_seconds
            )
            if not can_upload:
                # Remove uploaded file if quota exceeded
                video_path.unlink()
                raise HTTPException(status_code=400, detail=error_msg)
        
        # Add to session tracking
        session_manager.add_video(session_id, file_id, file_size_mb, duration_seconds)
        
        # Convert to MP3
        mp3_path = await video_processor.convert_to_mp3(video_path, file_id)
        
        # Get updated usage
        usage = session_manager.get_session_usage(session_id)
        
        return {
            "file_id": file_id,
            "session_id": session_id,
            "original_filename": file.filename,
            "video_path": str(video_path),
            "mp3_path": str(mp3_path),
            "duration_seconds": duration_seconds,
            "file_size_mb": round(file_size_mb, 2),
            "usage": usage,
            "message": "อัปโหลดและแปลงเป็น MP3 สำเร็จ"
        }
        
    except HTTPException:
        # Re-raise HTTPException as-is (don't wrap it)
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Upload error: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.get("/download-mp3/{file_id}")
async def download_mp3(file_id: str):
    """ดาวน์โหลดไฟล์ MP3"""
    mp3_path = UPLOAD_DIR / f"{file_id}.mp3"
    
    if not mp3_path.exists():
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ MP3")
    
    return FileResponse(
        path=mp3_path,
        filename=f"{file_id}.mp3",
        media_type="audio/mpeg"
    )

@app.post("/transcribe/{file_id}")
async def transcribe_audio(file_id: str, provider: str = Form("openai")):
    """แกะเสียงจากไฟล์ MP3 เป็นข้อความพร้อม timestamp
    
    Args:
        file_id: ID ของไฟล์
        provider: ผู้ให้บริการ ('openai' หรือ 'botnoi')
    """
    try:
        mp3_path = UPLOAD_DIR / f"{file_id}.mp3"
        
        if not mp3_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์ MP3")
        
        print(f"Starting transcription for file: {mp3_path} with provider: {provider}")
        
        # Select service based on provider
        if provider.lower() == "botnoi":
            if not botnoi_service:
                raise HTTPException(status_code=400, detail="Botnoi service ไม่พร้อมใช้งาน กรุณาตั้งค่า BOTNOI_API_KEY")
            result = await botnoi_service.transcribe_with_timestamps(mp3_path)
        else:
            # Default to OpenAI
            result = await transcription_service.transcribe_with_timestamps(mp3_path)
        
        print(f"Transcription completed, saving SRT file")
        
        # Save SRT file
        srt_path = UPLOAD_DIR / f"{file_id}_original.srt"
        await transcription_service.save_srt(result, srt_path)
        
        return {
            "file_id": file_id,
            "provider": provider,
            "transcription": result,
            "srt_path": str(srt_path),
            "message": f"แกะเสียงสำเร็จด้วย {provider}"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Transcription API error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.post("/translate")
async def translate_subtitles(
    file_id: str = Form(...),
    target_language: str = Form(...),
    style_prompt: Optional[str] = Form(None),
    provider: str = Form("openai")
):
    """แปลซับไตเติ้ลเป็นภาษาต่างๆ
    
    Args:
        file_id: ID ของไฟล์
        target_language: ภาษาเป้าหมาย
        style_prompt: คำแนะนำสไตล์การแปล (optional)
        provider: ผู้ให้บริการ ('openai' หรือ 'botnoi')
    """
    try:
        srt_path = UPLOAD_DIR / f"{file_id}_original.srt"
        
        if not srt_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์ SRT ต้นฉบับ")
        
        # Parse SRT file
        segments = transcription_service.parse_srt_file(srt_path)
        
        # Translate based on provider
        if provider.lower() == "botnoi":
            if not botnoi_service:
                raise HTTPException(status_code=400, detail="Botnoi service ไม่พร้อมใช้งาน กรุณาตั้งค่า BOTNOI_API_KEY")
            translated_segments = await botnoi_service.translate_segments(
                segments, 
                target_language,
                style_prompt
            )
        else:
            # Use OpenAI translation service
            translated_srt = await translation_service.translate_srt(
                srt_path, 
                target_language,
                style_prompt
            )
            # Save and return
            output_path = UPLOAD_DIR / f"{file_id}_{target_language}.srt"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(translated_srt)
            
            return {
                "file_id": file_id,
                "target_language": target_language,
                "provider": provider,
                "translated_srt_path": str(output_path),
                "message": f"แปลเป็น {target_language} สำเร็จด้วย {provider}"
            }
        
        # For Botnoi, generate SRT from translated segments
        translated_srt = transcription_service._generate_srt_content(translated_segments)
        
        # Save translated SRT
        output_path = UPLOAD_DIR / f"{file_id}_{target_language}.srt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_srt)
        
        return {
            "file_id": file_id,
            "target_language": target_language,
            "provider": provider,
            "translated_srt_path": str(output_path),
            "message": f"แปลเป็น {target_language} สำเร็จด้วย {provider}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.get("/download-srt/{file_id}/{language}")
async def download_srt(file_id: str, language: str = "original"):
    """ดาวน์โหลดไฟล์ SRT"""
    srt_path = UPLOAD_DIR / f"{file_id}_{language}.srt"
    
    if not srt_path.exists():
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์ SRT")
    
    return FileResponse(
        path=srt_path,
        filename=f"subtitle_{language}.srt",
        media_type="application/x-subrip",
        headers={
            "Content-Disposition": f"attachment; filename=subtitle_{language}.srt"
        }
    )

@app.post("/embed-subtitles")
async def embed_subtitles(request: dict):
    """ฝัง subtitle เข้ากับวิดีโอ (hard subtitle) พร้อมตัวเลือกการปรับแต่งฟอนต์"""
    try:
        file_id = request.get("file_id")
        language = request.get("language", "original")
        subtitle_type = request.get("type", "hard")  # "hard" or "soft"
        
        # Speed preset option for hard subtitle
        speed_preset = request.get("speed_preset", "balanced")  # fast, balanced, quality
        
        # Font customization options (with defaults)
        font_name = request.get("font_name", "TH Sarabun New")  # รองรับภาษาไทย
        font_size = request.get("font_size", 20)  # ขนาดเล็กลง
        bold = request.get("bold", True)
        outline = request.get("outline", 1.5)  # ขอบบางลง
        shadow = request.get("shadow", 1.0)
        font_color = request.get("font_color", "white")
        outline_color = request.get("outline_color", "black")
        
        if not file_id:
            raise HTTPException(status_code=400, detail="file_id is required")
        
        # Find original video file
        video_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
        video_path = None
        for file_path in video_files:
            if file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.wmv']:
                video_path = file_path
                break
        
        if not video_path or not video_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์วิดีโอต้นฉบับ")
        
        # Check SRT file
        srt_path = UPLOAD_DIR / f"{file_id}_{language}.srt"
        if not srt_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์ SRT")
        
        # Create output path
        suffix = "_hard" if subtitle_type == "hard" else "_soft"
        output_filename = f"{file_id}_{language}{suffix}.mp4"
        output_path = UPLOAD_DIR / output_filename
        
        # Embed subtitles
        if subtitle_type == "soft":
            await video_processor.embed_subtitles_soft(video_path, srt_path, output_path)
        else:
            await video_processor.embed_subtitles(
                video_path, srt_path, output_path,
                speed_preset=speed_preset,
                font_name=font_name,
                font_size=font_size,
                bold=bold,
                outline=outline,
                shadow=shadow,
                font_color=font_color,
                outline_color=outline_color
            )
        
        return {
            "file_id": file_id,
            "language": language,
            "type": subtitle_type,
            "speed_preset": speed_preset if subtitle_type == "hard" else None,
            "font_settings": {
                "font_name": font_name,
                "font_size": font_size,
                "bold": bold,
                "outline": outline,
                "shadow": shadow,
                "font_color": font_color,
                "outline_color": outline_color
            } if subtitle_type == "hard" else None,
            "output_path": str(output_path),
            "output_filename": output_filename,
            "message": f"ฝัง {subtitle_type} subtitle สำเร็จ"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Embed subtitles error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.get("/download-video/{file_id}/{language}/{subtitle_type}")
async def download_video_with_subtitles(file_id: str, language: str = "original", subtitle_type: str = "hard"):
    """ดาวน์โหลดวิดีโอที่ฝัง subtitle แล้ว"""
    # Find the embedded video file
    suffix = "_hard" if subtitle_type == "hard" else "_soft"
    video_files = list(UPLOAD_DIR.glob(f"{file_id}_{language}{suffix}.*"))
    
    if not video_files:
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์วิดีโอที่ฝัง subtitle แล้ว")
    
    video_path = video_files[0]
    
    return FileResponse(
        path=video_path,
        filename=f"video_{subtitle_type}_subtitles_{language}.mp4",
        media_type="video/mp4",
        headers={
            "Content-Disposition": f"attachment; filename=video_{subtitle_type}_subtitles_{language}.mp4"
        }
    )

@app.get("/stream-video/{file_id}")
async def stream_video(file_id: str, request: Request):
    """Stream วิดีโอต้นฉบับสำหรับ video player"""
    # Find original video file
    video_files = list(UPLOAD_DIR.glob(f"{file_id}.*"))
    video_path = None
    for file_path in video_files:
        if file_path.suffix.lower() in ['.mp4', '.mov', '.avi', '.mkv', '.wmv']:
            video_path = file_path
            break
    
    if not video_path or not video_path.exists():
        raise HTTPException(status_code=404, detail="ไม่พบไฟล์วิดีโอ")
    
    # Get file size
    file_size = video_path.stat().st_size
    
    # Handle range requests for video streaming
    range_header = request.headers.get("range")
    
    if range_header:
        # Parse range header
        range_match = range_header.replace("bytes=", "").split("-")
        start = int(range_match[0])
        end = int(range_match[1]) if range_match[1] else file_size - 1
        
        # Read chunk
        chunk_size = end - start + 1
        
        def iterfile():
            with open(video_path, "rb") as f:
                f.seek(start)
                yield f.read(chunk_size)
        
        headers = {
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(chunk_size),
            "Content-Type": "video/mp4",
        }
        
        return StreamingResponse(iterfile(), status_code=206, headers=headers)
    
    # Return full file if no range requested
    return FileResponse(
        path=video_path,
        media_type="video/mp4"
    )

@app.post("/update-srt/{file_id}")
async def update_srt(file_id: str, request: dict):
    """อัปเดตไฟล์ SRT ด้วย segments ที่แก้ไขแล้ว"""
    try:
        segments = request.get("segments", [])
        
        if not segments:
            raise HTTPException(status_code=400, detail="segments is required")
        
        # Generate SRT content from segments
        srt_content = ""
        for i, segment in enumerate(segments, 1):
            start_time = format_srt_time(segment["start"])
            end_time = format_srt_time(segment["end"])
            text = segment["text"]
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{text}\n\n"
        
        # Save updated SRT file
        srt_path = UPLOAD_DIR / f"{file_id}_original.srt"
        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        return {
            "file_id": file_id,
            "segments_count": len(segments),
            "srt_path": str(srt_path),
            "message": "อัปเดต SRT สำเร็จ"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

def format_srt_time(seconds):
    """แปลงเวลาจาก seconds เป็นรูปแบบ SRT (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)