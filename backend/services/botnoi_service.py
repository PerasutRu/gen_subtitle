import os
import httpx
from pathlib import Path
from typing import List, Optional
import asyncio
from models.subtitle_models import SubtitleSegment, TranscriptionResult

class BotnoiService:
    def __init__(self):
        api_key = os.getenv("BOTNOI_API_KEY")
        if not api_key:
            raise ValueError("BOTNOI_API_KEY environment variable is required")
        self.api_key = api_key
        self.base_url = "https://api-voice.botnoi.ai/api/genai"
        self.headers = {
            "botnoi-token": api_key  # ใช้ lowercase ตาม API docs
        }
    
    async def transcribe_with_timestamps(self, audio_path: Path) -> TranscriptionResult:
        """ใช้ Botnoi Gensub API แกะเสียงพร้อม timestamp"""
        try:
            async with httpx.AsyncClient(timeout=300.0) as client:
                # Step 1: Upload file using /gensub_upload
                print(f"[Botnoi] Uploading file: {audio_path}")
                print(f"[Botnoi] API Key: {self.api_key[:10]}...")
                print(f"[Botnoi] Base URL: {self.base_url}")
                
                with open(audio_path, "rb") as audio_file:
                    # ตาม API docs ต้องส่ง parameters เหล่านี้
                    files = {
                        "audio_file": (audio_path.name, audio_file, "audio/mpeg")
                    }
                    
                    data = {
                        "max_duration": "10",  # Maximum chunk duration in seconds
                        "max_silence": "0.3",  # Maximum silence allowed in seconds
                        "language": "th",  # Language used for transcription
                        "srt": "yes"  # Set to 'yes' for SRT response
                    }
                    
                    # Try the exact URL from the API docs
                    url = f"{self.base_url}/gensub_upload"
                    print(f"[Botnoi] POST URL: {url}")
                    print(f"[Botnoi] Headers: {self.headers}")
                    print(f"[Botnoi] Data: {data}")
                    
                    upload_response = await client.post(
                        url,
                        headers=self.headers,
                        files=files,
                        data=data
                    )
                    
                    print(f"[Botnoi] Response status: {upload_response.status_code}")
                    print(f"[Botnoi] Response body: {upload_response.text[:500]}...")
                    
                    upload_response.raise_for_status()
                    upload_data = upload_response.json()
                
                print(f"[Botnoi] Upload data keys: {upload_data.keys()}")
                
                # Parse response - Botnoi returns SRT format in 'text' field
                if "data" in upload_data and "text" in upload_data["data"]:
                    srt_text = upload_data["data"]["text"]
                    print(f"[Botnoi] Got SRT text, length: {len(srt_text)}")
                    
                    # Parse SRT text to segments
                    segments = self._parse_srt_to_segments(srt_text)
                else:
                    # Try to parse segments from other formats
                    segments = self._parse_botnoi_segments(upload_data)
                
                if not segments:
                    raise Exception(f"ไม่สามารถ parse segments จาก response: {upload_data}")
                
                # Extract full text
                full_text = " ".join([seg.text for seg in segments])
                
                print(f"[Botnoi] Parsed {len(segments)} segments")
                
                return TranscriptionResult(
                    text=full_text,
                    segments=segments,
                    language="th"  # Botnoi primarily supports Thai
                )
                
        except httpx.HTTPStatusError as e:
            error_detail = f"Botnoi API error: {e.response.status_code} - {e.response.text}"
            print(f"[Botnoi] {error_detail}")
            raise Exception(error_detail)
        except Exception as e:
            error_msg = f"การแกะเสียงด้วย Botnoi ล้มเหลว: {str(e)}"
            print(f"[Botnoi] {error_msg}")
            raise Exception(error_msg)
    
    def _parse_botnoi_segments(self, response_data: dict) -> List[SubtitleSegment]:
        """แปลง response จาก Botnoi เป็น SubtitleSegment"""
        segments = []
        
        print(f"[Botnoi] Parsing response data keys: {response_data.keys()}")
        
        # Try different possible response formats
        # Format 1: Direct segments array
        if "segments" in response_data:
            print(f"[Botnoi] Found 'segments' key")
            for seg in response_data["segments"]:
                segments.append(SubtitleSegment(
                    start=float(seg.get("start", 0)),
                    end=float(seg.get("end", 0)),
                    text=seg.get("text", "").strip()
                ))
        
        # Format 2: Result contains segments
        elif "result" in response_data:
            print(f"[Botnoi] Found 'result' key")
            result = response_data["result"]
            
            if isinstance(result, list):
                for seg in result:
                    if isinstance(seg, dict):
                        segments.append(SubtitleSegment(
                            start=float(seg.get("start", 0)),
                            end=float(seg.get("end", 0)),
                            text=seg.get("text", "").strip()
                        ))
            elif isinstance(result, dict) and "segments" in result:
                for seg in result["segments"]:
                    segments.append(SubtitleSegment(
                        start=float(seg.get("start", 0)),
                        end=float(seg.get("end", 0)),
                        text=seg.get("text", "").strip()
                    ))
        
        # Format 3: Data contains segments
        elif "data" in response_data:
            print(f"[Botnoi] Found 'data' key")
            data = response_data["data"]
            if isinstance(data, dict) and "segments" in data:
                for seg in data["segments"]:
                    segments.append(SubtitleSegment(
                        start=float(seg.get("start", 0)),
                        end=float(seg.get("end", 0)),
                        text=seg.get("text", "").strip()
                    ))
        
        # Format 4: Transcript with words/timestamps
        elif "transcript" in response_data:
            print(f"[Botnoi] Found 'transcript' key")
            transcript = response_data["transcript"]
            if isinstance(transcript, list):
                for item in transcript:
                    segments.append(SubtitleSegment(
                        start=float(item.get("start", 0)),
                        end=float(item.get("end", 0)),
                        text=item.get("text", item.get("word", "")).strip()
                    ))
        
        print(f"[Botnoi] Parsed {len(segments)} segments")
        return segments
    
    async def translate_text(self, text: str, target_language: str) -> str:
        """แปลข้อความด้วย Botnoi /translate API"""
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # ตาม API docs ต้องส่ง JSON body
                payload = {
                    "language": self._map_language_code(target_language),
                    "native_style": True,
                    "simple_style": True,
                    "text": text
                }
                
                print(f"[Botnoi] Translating to {target_language}: {text[:50]}...")
                
                response = await client.post(
                    f"{self.base_url}/translate",
                    headers={
                        **self.headers,
                        "Content-Type": "application/json"
                    },
                    json=payload
                )
                
                print(f"[Botnoi] Translate response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                print(f"[Botnoi] Translate response keys: {data.keys()}")
                
                # Extract translated text from response
                if "data" in data and "text" in data["data"]:
                    return data["data"]["text"]
                elif "text" in data:
                    return data["text"]
                elif "result" in data:
                    return data["result"]
                else:
                    raise Exception(f"ไม่พบข้อความแปลใน response: {data}")
                    
        except httpx.HTTPStatusError as e:
            error_msg = f"Botnoi translate API error: {e.response.status_code} - {e.response.text}"
            print(f"[Botnoi] {error_msg}")
            raise Exception(error_msg)
        except Exception as e:
            error_msg = f"การแปลด้วย Botnoi ล้มเหลว: {str(e)}"
            print(f"[Botnoi] {error_msg}")
            raise Exception(error_msg)
    
    def _parse_srt_to_segments(self, srt_text: str) -> List[SubtitleSegment]:
        """แปลง SRT text เป็น SubtitleSegment list"""
        segments = []
        
        try:
            # Split by double newline to get each subtitle block
            blocks = srt_text.strip().split('\n\n')
            
            for block in blocks:
                lines = block.strip().split('\n')
                if len(lines) >= 3:
                    # Line 0: index
                    # Line 1: timestamp
                    # Line 2+: text
                    
                    timestamp_line = lines[1]
                    # Format: 00:00:00,000 --> 00:00:02,858
                    if '-->' in timestamp_line:
                        start_str, end_str = timestamp_line.split('-->')
                        start_str = start_str.strip()
                        end_str = end_str.strip()
                        
                        # Convert to seconds
                        start_seconds = self._srt_time_to_seconds(start_str)
                        end_seconds = self._srt_time_to_seconds(end_str)
                        
                        # Join text lines
                        text = '\n'.join(lines[2:])
                        
                        segments.append(SubtitleSegment(
                            start=start_seconds,
                            end=end_seconds,
                            text=text.strip()
                        ))
            
            print(f"[Botnoi] Parsed {len(segments)} segments from SRT")
            return segments
            
        except Exception as e:
            print(f"[Botnoi] Error parsing SRT: {str(e)}")
            return []
    
    def _srt_time_to_seconds(self, time_str: str) -> float:
        """แปลงเวลาจากรูปแบบ SRT (HH:MM:SS,mmm) เป็นวินาที"""
        try:
            time_part, ms_part = time_str.split(',')
            h, m, s = map(int, time_part.split(':'))
            ms = int(ms_part)
            return h * 3600 + m * 60 + s + ms / 1000
        except Exception as e:
            print(f"[Botnoi] Error parsing time {time_str}: {str(e)}")
            return 0.0
    
    def _map_language_code(self, language: str) -> str:
        """แปลง language code ให้ตรงกับ Botnoi API"""
        language_map = {
            "english": "english",
            "lao": "lao",
            "myanmar": "myanmar",
            "khmer": "khmer",
            "vietnamese": "vietnamese",
            "thai": "thai"
        }
        return language_map.get(language.lower(), language)
    
    async def translate_segments(self, segments: List[SubtitleSegment], target_language: str, style_prompt: Optional[str] = None) -> List[SubtitleSegment]:
        """แปลแต่ละ segment"""
        translated_segments = []
        
        for segment in segments:
            try:
                translated_text = await self.translate_text(segment.text, target_language)
                translated_segments.append(SubtitleSegment(
                    start=segment.start,
                    end=segment.end,
                    text=translated_text.strip()
                ))
            except Exception as e:
                # If translation fails, keep original text
                print(f"Warning: Failed to translate segment: {str(e)}")
                translated_segments.append(segment)
        
        return translated_segments
