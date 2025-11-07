import os
from pathlib import Path
from openai import OpenAI
from typing import List, Dict
import asyncio
from models.subtitle_models import SubtitleSegment, TranscriptionResult

class TranscriptionService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.client = OpenAI(api_key=api_key)
    
    async def transcribe_with_timestamps(self, audio_path: Path) -> TranscriptionResult:
        """ใช้ OpenAI ASR แกะเสียงพร้อม timestamp"""
        try:
            with open(audio_path, "rb") as audio_file:
                # Run transcription in thread pool to avoid blocking
                loop = asyncio.get_event_loop()
                
                def transcribe_audio():
                    return self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                        language="th"
                    )

                transcript = await loop.run_in_executor(None, transcribe_audio)
            
            # Convert segments to our format
            segments = []
            for segment in transcript.segments:
                segments.append(SubtitleSegment(
                    start=segment.start,
                    end=segment.end,
                    text=segment.text.strip()
                ))
            
            return TranscriptionResult(
                text=transcript.text,
                segments=segments,
                language=transcript.language
            )
            
        except Exception as e:
            raise Exception(f"การแกะเสียงล้มเหลว: {str(e)}")
    
    async def save_srt(self, transcription: TranscriptionResult, output_path: Path):
        """บันทึกผลลัพธ์เป็นไฟล์ SRT"""
        try:
            srt_content = self._generate_srt_content(transcription.segments)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(srt_content)
                
        except Exception as e:
            raise Exception(f"ไม่สามารถบันทึกไฟล์ SRT ได้: {str(e)}")
    
    def _generate_srt_content(self, segments: List[SubtitleSegment]) -> str:
        """สร้างเนื้อหาไฟล์ SRT"""
        srt_content = ""
        
        for i, segment in enumerate(segments, 1):
            start_time = self._seconds_to_srt_time(segment.start)
            end_time = self._seconds_to_srt_time(segment.end)
            
            srt_content += f"{i}\n"
            srt_content += f"{start_time} --> {end_time}\n"
            srt_content += f"{segment.text}\n\n"
        
        return srt_content
    
    def _seconds_to_srt_time(self, seconds: float) -> str:
        """แปลงวินาทีเป็นรูปแบบเวลาของ SRT"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"
    
    def parse_srt_file(self, srt_path: Path) -> List[SubtitleSegment]:
        """อ่านไฟล์ SRT และแปลงเป็น segments"""
        try:
            with open(srt_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            segments = []
            blocks = content.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Parse timestamp line
                    timestamp_line = lines[1]
                    start_str, end_str = timestamp_line.split(' --> ')
                    
                    start_seconds = self._srt_time_to_seconds(start_str)
                    end_seconds = self._srt_time_to_seconds(end_str)
                    
                    # Join text lines
                    text = '\n'.join(lines[2:])
                    
                    segments.append(SubtitleSegment(
                        start=start_seconds,
                        end=end_seconds,
                        text=text
                    ))
            
            return segments
            
        except Exception as e:
            raise Exception(f"ไม่สามารถอ่านไฟล์ SRT ได้: {str(e)}")
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        """แปลงเวลาจากรูปแบบ SRT เป็นวินาที"""
        time_part, ms_part = time_str.split(',')
        h, m, s = map(int, time_part.split(':'))
        ms = int(ms_part)
        
        return h * 3600 + m * 60 + s + ms / 1000