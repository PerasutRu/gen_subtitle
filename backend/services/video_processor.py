import os
import subprocess
import platform
from pathlib import Path
from moviepy.editor import VideoFileClip
import asyncio
from concurrent.futures import ThreadPoolExecutor

class VideoProcessor:
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=2)
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
    
    async def embed_subtitles(self, video_path: Path, srt_path: Path, output_path: Path) -> Path:
        """ฝัง subtitle เข้ากับวิดีโอด้วย ffmpeg"""
        try:
            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self._embed_subtitles_ffmpeg,
                str(video_path),
                str(srt_path),
                str(output_path)
            )
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ไม่สามารถฝัง subtitle ได้: {str(e)}")
    
    def _embed_subtitles_ffmpeg(self, video_path: str, srt_path: str, output_path: str):
        """Helper function to embed subtitles using ffmpeg - optimized for speed"""
        try:
            # Fast and simple subtitle style for Thai text
            simple_style = (
                "FontSize=24,"              # Good readable size
                "PrimaryColour=&Hffffff,"   # White text
                "OutlineColour=&H000000,"   # Black outline
                "Outline=2,"                # Simple outline
                "Alignment=2,"              # Bottom center
                "MarginV=30"                # Bottom margin
            )
            
            # Fast ffmpeg command - prioritize speed over quality
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles='{srt_path}':force_style='{simple_style}'",
                '-c:a', 'copy',             # Copy audio (no re-encoding)
                '-c:v', 'libx264',          # Video codec
                '-preset', 'ultrafast',     # Fastest encoding preset
                '-crf', '23',               # Balanced quality/speed
                '-threads', '0',            # Use all available CPU cores
                '-y',                       # Overwrite output
                output_path
            ]
            
            print(f"Running fast ffmpeg command for subtitle embedding...")
            
            # Run ffmpeg command with timeout
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=600  # 10 minute timeout
            )
            
            print(f"Fast ffmpeg completed successfully")
            
        except subprocess.TimeoutExpired:
            print("ffmpeg timeout - trying simpler method")
            self._embed_subtitles_simple(video_path, srt_path, output_path)
        except subprocess.CalledProcessError as e:
            print(f"ffmpeg error: {e.stderr}")
            # Try simpler method
            try:
                print("Trying simpler method...")
                self._embed_subtitles_simple(video_path, srt_path, output_path)
            except Exception as fallback_error:
                raise Exception(f"ffmpeg ล้มเหลว: {e.stderr}")
        except FileNotFoundError:
            raise Exception("ไม่พบ ffmpeg กรุณาติดตั้ง ffmpeg ก่อน")
        except Exception as e:
            raise Exception(f"การฝัง subtitle ล้มเหลว: {str(e)}")
    
    def _embed_subtitles_simple(self, video_path: str, srt_path: str, output_path: str):
        """Ultra-simple and fast subtitle embedding"""
        try:
            # Minimal ffmpeg command for maximum speed
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles='{srt_path}'",  # Use default subtitle style
                '-c:a', 'copy',                    # Copy audio
                '-c:v', 'libx264',                 # Video codec
                '-preset', 'veryfast',             # Very fast preset
                '-crf', '25',                      # Lower quality for speed
                '-threads', '0',                   # Use all cores
                '-y',
                output_path
            ]
            
            print(f"Running ultra-simple ffmpeg command...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout
            )
            
            print(f"Simple ffmpeg completed successfully")
            
        except Exception as e:
            print(f"Simple ffmpeg failed: {str(e)}")
            raise Exception(f"Simple ffmpeg ล้มเหลว: {str(e)}")
    
    def _embed_subtitles_fallback(self, video_path: str, srt_path: str, output_path: str):
        """Fast fallback method for subtitle embedding"""
        try:
            # Single fast fallback method
            cmd = [
                'ffmpeg',
                '-i', video_path,
                '-vf', f"subtitles='{srt_path}'",  # Minimal subtitle filter
                '-c:a', 'copy',                    # Copy audio
                '-c:v', 'libx264',                 # Video codec
                '-preset', 'superfast',            # Fastest preset
                '-crf', '28',                      # Lower quality for speed
                '-threads', '0',                   # Use all cores
                '-y',
                output_path
            ]
            
            print(f"Running fast fallback method...")
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=180  # 3 minute timeout
            )
            
            print(f"Fast fallback completed successfully")
            
        except Exception as e:
            print(f"Fast fallback failed: {str(e)}")
            raise Exception(f"Fast fallback ล้มเหลว: {str(e)}")
    
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