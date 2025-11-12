import os
import subprocess
import platform
from pathlib import Path
from moviepy.editor import VideoFileClip
import asyncio
from concurrent.futures import ThreadPoolExecutor

class VideoProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)  # Increased workers
        self.thai_fonts = self._get_thai_fonts()
    
    def _get_thai_fonts(self):
        """Get available Thai fonts on the system - simplified"""
        # Return simple list without testing
        return ["Tahoma", "Arial", "DejaVu Sans"]  # Common fonts that work well with Thai
    
    def _get_best_thai_font(self):
        """Get the best available Thai font - simplified"""
        # Skip font testing for speed, use system default
        return "Arial"  # Use Arial as it's widely available and works with Thai
    
    async def convert_to_mp3(self, video_path: Path, file_id: str) -> Path:
        """แปลงไฟล์วิดีโอเป็น MP3"""
        try:
            mp3_path = video_path.parent / f"{file_id}.mp3"
            
            # Run conversion in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._convert_video_to_mp3,
                str(video_path),
                str(mp3_path)
            )
            
            return mp3_path
            
        except Exception as e:
            raise Exception(f"ไม่สามารถแปลงไฟล์เป็น MP3 ได้: {str(e)}")
    
    def _convert_video_to_mp3(self, video_path: str, mp3_path: str):
        """Helper function to convert video to MP3"""
        try:
            video = VideoFileClip(video_path)
            audio = video.audio
            audio.write_audiofile(mp3_path, verbose=False, logger=None)
            audio.close()
            video.close()
        except Exception as e:
            raise Exception(f"การแปลงไฟล์ล้มเหลว: {str(e)}")
    
    async def embed_subtitles(
        self, 
        video_path: Path, 
        srt_path: Path, 
        output_path: Path, 
        speed_preset: str = "balanced",
        font_name: str = "TH Sarabun New",
        font_size: int = 20,
        bold: bool = True,
        outline: float = 1.5,
        shadow: float = 1.0,
        font_color: str = "white",
        outline_color: str = "black"
    ) -> Path:
        """ฝัง subtitle เข้ากับวิดีโอด้วย ffmpeg พร้อมตัวเลือกการปรับแต่งฟอนต์
        
        Args:
            video_path: ไฟล์วิดีโอต้นฉบับ
            srt_path: ไฟล์ subtitle
            output_path: ไฟล์ output
            speed_preset: ความเร็วในการ encode ('fast', 'balanced', 'quality')
            font_name: ชื่อฟอนต์ (default: TH Sarabun New - รองรับภาษาไทย)
            font_size: ขนาดฟอนต์ (default: 20)
            bold: ตัวหนา (default: True)
            outline: ความหนาของขอบ (default: 1.5)
            shadow: ความเข้มของเงา (default: 1.0)
            font_color: สีตัวอักษร (default: white)
            outline_color: สีขอบ (default: black)
        """
        try:
            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._embed_subtitles_ffmpeg,
                str(video_path),
                str(srt_path),
                str(output_path),
                speed_preset,
                font_name,
                font_size,
                bold,
                outline,
                shadow,
                font_color,
                outline_color
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ไม่สามารถฝัง subtitle ได้: {str(e)}")
    
    def _embed_subtitles_ffmpeg(
        self, 
        video_path: str, 
        srt_path: str, 
        output_path: str,
        speed_preset: str = "balanced",
        font_name: str = "TH Sarabun New",
        font_size: int = 20,
        bold: bool = True,
        outline: float = 1.5,
        shadow: float = 1.0,
        font_color: str = "white",
        outline_color: str = "black"
    ):
        """Helper function to embed subtitles using ffmpeg - with customizable Thai font support"""
        import time
        start_time = time.time()
        
        # Speed preset configurations
        preset_configs = {
            "fast": {
                "ffmpeg_preset": "ultrafast",
                "crf": "25",
                "timeout": 180,
                "description": "เร็วที่สุด (คุณภาพปานกลาง)"
            },
            "balanced": {
                "ffmpeg_preset": "veryfast",
                "crf": "23",
                "timeout": 300,
                "description": "สมดุล (แนะนำ)"
            },
            "quality": {
                "ffmpeg_preset": "fast",
                "crf": "20",
                "timeout": 600,
                "description": "คุณภาพสูง (ช้ากว่า)"
            }
        }
        
        config = preset_configs.get(speed_preset, preset_configs["balanced"])
        
        # Color mapping for ASS format (AABBGGRR)
        color_map = {
            "white": "&H00FFFFFF",
            "black": "&H00000000",
            "yellow": "&H0000FFFF",
            "cyan": "&H00FFFF00",
            "green": "&H0000FF00",
            "magenta": "&H00FF00FF",
            "red": "&H000000FF",
            "blue": "&H00FF0000"
        }
        
        primary_color = color_map.get(font_color.lower(), "&H00FFFFFF")
        outline_col = color_map.get(outline_color.lower(), "&H00000000")
        bold_value = 1 if bold else 0
        
        try:
            print(f"\n{'='*60}")
            print(f"Starting subtitle embedding...")
            print(f"Video: {video_path}")
            print(f"SRT: {srt_path}")
            print(f"Output: {output_path}")
            print(f"Speed Preset: {speed_preset} - {config['description']}")
            print(f"Font Settings: {font_name}, Size: {font_size}, Bold: {bold}")
            print(f"Outline: {outline}, Shadow: {shadow}")
            print(f"{'='*60}\n")
            
            # Subtitle style with customizable Thai font support
            # Using ASS format for better Thai language support
            subtitle_style = (
                f"subtitles='{srt_path}':force_style='"
                f"FontName={font_name},"          # ฟอนต์ที่รองรับภาษาไทย
                f"FontSize={font_size},"          # ขนาดฟอนต์
                f"PrimaryColour={primary_color}," # สีตัวอักษร
                f"OutlineColour={outline_col},"   # สีขอบ
                f"BackColour=&H80000000,"         # พื้นหลังโปร่งแสง
                f"Bold={bold_value},"             # ตัวหนา
                f"Outline={outline},"             # ความหนาของขอบ
                f"Shadow={shadow},"               # เงา
                f"MarginV=20,"                    # ระยะห่างจากขอบล่าง
                f"Alignment=2"                    # จัดกลางด้านล่าง
                "'"
            )
            
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', subtitle_style,             # ใช้สไตล์ที่ปรับแต่งได้
                '-c:a', 'copy',                    # Copy audio (no re-encoding)
                '-c:v', 'libx264',                 # Video codec
                '-preset', config['ffmpeg_preset'], # Speed preset
                '-crf', config['crf'],             # Quality
                '-threads', '0',                   # Use all available CPU cores
                '-y',                              # Overwrite output
                output_path
            ]
            
            print(f"Running ffmpeg with customized subtitle style...")
            print(f"Font: {font_name}, Size: {font_size}, Bold: {bold}, Outline: {outline}, Shadow: {shadow}")
            print(f"Using preset: {config['ffmpeg_preset']}, CRF: {config['crf']}")
            
            # Run ffmpeg command with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=config['timeout']
            )
            
            elapsed_time = time.time() - start_time
            print(f"\n{'='*60}")
            print(f"✅ Subtitle embedding completed successfully!")
            print(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
            print(f"{'='*60}\n")
            
        except subprocess.TimeoutExpired:
            print("ffmpeg timeout - trying faster preset")
            if speed_preset != "fast":
                self._embed_subtitles_ffmpeg(
                    video_path, srt_path, output_path, "fast",
                    font_name, font_size, bold, outline, shadow, font_color, outline_color
                )
            else:
                raise Exception("การฝัง subtitle timeout แม้ใช้ preset เร็วที่สุด")
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error: {e.stderr}")
            # Try faster preset if not already using fast
            if speed_preset != "fast":
                try:
                    print("Trying faster preset...")
                    self._embed_subtitles_ffmpeg(
                        video_path, srt_path, output_path, "fast",
                        font_name, font_size, bold, outline, shadow, font_color, outline_color
                    )
                except Exception as fallback_error:
                    raise Exception(f"ffmpeg ล้มเหลว: {e.stderr}")
            else:
                raise Exception(f"ffmpeg ล้มเหลว: {e.stderr}")
        except FileNotFoundError:
            raise Exception("ไม่พบ ffmpeg กรุณาติดตั้ง ffmpeg ก่อน")
        except Exception as e:
            raise Exception(f"การฝัง subtitle ล้มเหลว: {str(e)}")
    

    async def embed_subtitles_soft(self, video_path: Path, srt_path: Path, output_path: Path) -> Path:
        """ฝัง subtitle แบบ soft subtitle (ไม่เผาลงในวิดีโอ)"""
        try:
            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._embed_subtitles_soft_ffmpeg,
                str(video_path),
                str(srt_path),
                str(output_path)
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ไม่สามารถฝัง soft subtitle ได้: {str(e)}")
    
    def _embed_subtitles_soft_ffmpeg(self, video_path: str, srt_path: str, output_path: str):
        """Helper function to embed soft subtitles using ffmpeg"""
        try:
            # Build ffmpeg command for soft subtitles
            cmd = [
                'ffmpeg',
                '-i', video_path,          # Input video
                '-i', srt_path,            # Input subtitle
                '-c:v', 'copy',            # Copy video without re-encoding
                '-c:a', 'copy',            # Copy audio without re-encoding
                '-c:s', 'mov_text',        # Subtitle codec for MP4
                '-metadata:s:s:0', 'language=th',  # Set subtitle language
                '-y',                      # Overwrite output file
                output_path
            ]
            
            print(f"Running ffmpeg soft subtitle command: {' '.join(cmd)}")
            
            # Run ffmpeg command
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            print(f"ffmpeg soft subtitle completed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error: {e.stderr}")
            raise Exception(f"ffmpeg ล้มเหลว: {e.stderr}")
        except FileNotFoundError:
            raise Exception("ไม่พบ ffmpeg กรุณาติดตั้ง ffmpeg ก่อน")
        except Exception as e:
            raise Exception(f"การฝัง soft subtitle ล้มเหลว: {str(e)}")

    def get_video_info(self, video_path: Path) -> dict:
        """ดึงข้อมูลของไฟล์วิดีโอ"""
        try:
            video = VideoFileClip(str(video_path))
            info = {
                "duration": video.duration,
                "fps": video.fps,
                "size": video.size,
                "audio_fps": video.audio.fps if video.audio else None
            }
            video.close()
            return info
        except Exception as e:
            raise Exception(f"ไม่สามารถดึงข้อมูลวิดีโอได้: {str(e)}")