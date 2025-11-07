from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import shutil
import uuid
from pathlib import Path
from dotenv import load_dotenv
import asyncio
from typing import List, Optional

from services.video_processor import VideoProcessor
from services.transcription_service import TranscriptionService
from services.translation_service import TranslationService
from models.subtitle_models import SubtitleResponse, TranslationRequest

load_dotenv()

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

# Create upload directory
UPLOAD_DIR = Path(os.getenv("UPLOAD_DIR", "uploads"))
UPLOAD_DIR.mkdir(exist_ok=True)

@app.get("/")
async def root():
    return {"message": "Video Subtitle Generator API"}

@app.post("/upload-video")
async def upload_video(file: UploadFile = File(...)):
    """อัปโหลดไฟล์วิดีโอและแปลงเป็น MP3"""
    try:
        # Validate file type
        allowed_extensions = {'.mp4', '.mov', '.avi', '.mkv', '.wmv'}
        file_extension = Path(file.filename).suffix.lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="ไฟล์ต้องเป็น MP4, MOV, AVI, MKV หรือ WMV เท่านั้น")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        video_path = UPLOAD_DIR / f"{file_id}{file_extension}"
        
        # Save uploaded file
        with open(video_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Convert to MP3
        mp3_path = await video_processor.convert_to_mp3(video_path, file_id)
        
        return {
            "file_id": file_id,
            "original_filename": file.filename,
            "video_path": str(video_path),
            "mp3_path": str(mp3_path),
            "message": "อัปโหลดและแปลงเป็น MP3 สำเร็จ"
        }
        
    except Exception as e:
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
async def transcribe_audio(file_id: str):
    """แกะเสียงจากไฟล์ MP3 เป็นข้อความพร้อม timestamp"""
    try:
        mp3_path = UPLOAD_DIR / f"{file_id}.mp3"
        
        if not mp3_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์ MP3")
        
        print(f"Starting transcription for file: {mp3_path}")  # Add logging
        
        # Transcribe audio
        result = await transcription_service.transcribe_with_timestamps(mp3_path)
        
        print(f"Transcription completed, saving SRT file")  # Add logging
        
        # Save SRT file
        srt_path = UPLOAD_DIR / f"{file_id}_original.srt"
        await transcription_service.save_srt(result, srt_path)
        
        return {
            "file_id": file_id,
            "transcription": result,
            "srt_path": str(srt_path),
            "message": "แกะเสียงสำเร็จ"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Transcription API error: {str(e)}")  # Add logging
        raise HTTPException(status_code=500, detail=f"เกิดข้อผิดพลาด: {str(e)}")

@app.post("/translate")
async def translate_subtitles(request: TranslationRequest):
    """แปลซับไตเติ้ลเป็นภาษาต่างๆ"""
    try:
        srt_path = UPLOAD_DIR / f"{request.file_id}_original.srt"
        
        if not srt_path.exists():
            raise HTTPException(status_code=404, detail="ไม่พบไฟล์ SRT ต้นฉบับ")
        
        # Translate subtitles
        translated_srt = await translation_service.translate_srt(
            srt_path, 
            request.target_language,
            request.style_prompt
        )
        
        # Save translated SRT
        output_path = UPLOAD_DIR / f"{request.file_id}_{request.target_language}.srt"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_srt)
        
        return {
            "file_id": request.file_id,
            "target_language": request.target_language,
            "translated_srt_path": str(output_path),
            "message": f"แปลเป็น{request.target_language}สำเร็จ"
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
    """ฝัง subtitle เข้ากับวิดีโอ (hard subtitle)"""
    try:
        file_id = request.get("file_id")
        language = request.get("language", "original")
        subtitle_type = request.get("type", "hard")  # "hard" or "soft"
        
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
            await video_processor.embed_subtitles(video_path, srt_path, output_path)
        
        return {
            "file_id": file_id,
            "language": language,
            "type": subtitle_type,
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)