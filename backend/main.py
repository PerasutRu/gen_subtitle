from fastapi import FastAPI, File, UploadFile, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
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
from services.botnoi_service import BotnoiService
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

# Initialize Botnoi service (optional)
botnoi_service = None
try:
    botnoi_service = BotnoiService()
except ValueError:
    print("Botnoi service not initialized (BOTNOI_API_KEY not found)")

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