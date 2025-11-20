import gradio as gr
import requests
import os
from pathlib import Path
import json
from typing import Optional, Tuple, List
import tempfile

# Backend API URL
API_URL = os.getenv("API_URL", "http://localhost:8000")

# Session state
class SessionState:
    def __init__(self):
        self.token = None
        self.user = None
        self.file_id = None
        self.session_id = None
        self.transcription = None
        self.video_path = None
        self.mp3_path = None
        self.limits = None
        self.usage = None
        
session = SessionState()

# ==================== Helper Functions ====================

def get_headers():
    """Get authorization headers"""
    if session.token:
        return {"Authorization": f"Bearer {session.token}"}
    return {}

def format_time(seconds):
    """Format seconds to HH:MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def get_limits():
    """Get system limits"""
    try:
        response = requests.get(
            f"{API_URL}/limits",
            headers=get_headers()
        )
        if response.status_code == 200:
            session.limits = response.json()
            return session.limits
        return None
    except Exception as e:
        print(f"Error getting limits: {e}")
        return None

def get_session_usage():
    """Get current session usage"""
    if not session.session_id:
        return None
    
    try:
        response = requests.get(
            f"{API_URL}/session/{session.session_id}/usage",
            headers=get_headers()
        )
        if response.status_code == 200:
            data = response.json()
            session.usage = data.get('usage', {})
            session.limits = data.get('limits', {})
            return session.usage
        return None
    except Exception as e:
        print(f"Error getting usage: {e}")
        return None

def format_quota_display():
    """Format quota information for display"""
    if not session.limits:
        get_limits()
    
    if not session.limits:
        return "ℹ️ ไม่สามารถโหลดข้อมูล quota ได้"
    
    limits = session.limits
    usage = session.usage or {}
    
    # Get limits from config
    max_videos = limits.get('maxVideosPerSession', limits.get('maxVideos', 10))
    
    # Get current usage
    video_count = usage.get('videos_count', 0)
    
    # Calculate percentage
    video_percent = (video_count / max_videos * 100) if max_videos > 0 else 0
    
    # Status indicator
    if video_percent < 70:
        icon = '🟢'
        status = 'เหลือเยอะ'
    elif video_percent < 90:
        icon = '🟡'
        status = 'ใกล้เต็ม'
    else:
        icon = '🔴'
        status = 'เต็มแล้ว!'
    
    quota_text = f"""
## 📊 Quota การใช้งาน

🎬 **จำนวนวิดีโอ:** {video_count}/{max_videos} ไฟล์ ({video_percent:.1f}%)  
{icon} {status}
"""
    return quota_text

# ==================== Authentication ====================

def login(username: str, password: str):
    """Login to the system"""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            data = response.json()
            session.token = data["access_token"]
            session.user = data["user"]
            
            # Get limits after login
            get_limits()
            quota_text = format_quota_display()
            
            welcome_msg = f"✅ ยินดีต้อนรับ **{session.user['username']}**!\n\nคุณสามารถเริ่มอัปโหลดวิดีโอได้เลย"
            
            return (
                gr.update(visible=False),  # Hide login
                gr.update(visible=True),   # Show main app
                welcome_msg,
                quota_text,
                f"👤 {session.user['username']}"
            )
        else:
            return (
                gr.update(visible=True),
                gr.update(visible=False),
                f"❌ เข้าสู่ระบบไม่สำเร็จ: {response.json().get('detail', 'Unknown error')}",
                "",
                ""
            )
    except Exception as e:
        return (
            gr.update(visible=True),
            gr.update(visible=False),
            f"❌ เกิดข้อผิดพลาด: {str(e)}",
            "",
            ""
        )

def logout():
    """Logout from the system"""
    session.token = None
    session.user = None
    session.file_id = None
    session.session_id = None
    session.transcription = None
    session.limits = None
    session.usage = None
    return (
        gr.update(visible=True),   # Show login
        gr.update(visible=False),  # Hide main app
        "👋 ออกจากระบบเรียบร้อยแล้ว",
        "",
        ""
    )

# ==================== Step 1: Upload Video ====================

def upload_video(video_file):
    """Upload video file"""
    if not video_file:
        return "❌ กรุณาเลือกไฟล์วิดีโอ", None, None, None, format_quota_display()
    
    try:
        # Check file size before uploading
        file_size_bytes = os.path.getsize(video_file)
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Get limits to check file size
        limits = session.limits or get_limits()
        max_size_mb = limits.get('maxFileSizeMB', 500) if limits else 500
        
        # Validate file size on client side first
        if file_size_mb > max_size_mb:
            error_msg = f"""
❌ **ไฟล์ใหญ่เกินไป!**

💾 **ขนาดไฟล์ของคุณ:** {file_size_mb:.2f} MB
📏 **ขนาดสูงสุดที่อนุญาต:** {max_size_mb} MB

⚠️ กรุณาเลือกไฟล์ที่มีขนาดเล็กกว่า {max_size_mb} MB
"""
            return error_msg, gr.update(visible=False), None, None, format_quota_display()
        
        with open(video_file, 'rb') as f:
            files = {'file': (Path(video_file).name, f, 'video/mp4')}
            data = {'session_id': session.session_id} if session.session_id else {}
            
            response = requests.post(
                f"{API_URL}/upload-video",
                files=files,
                data=data,
                headers=get_headers()
            )
        
        if response.status_code == 200:
            result = response.json()
            session.file_id = result['file_id']
            session.session_id = result['session_id']
            session.video_path = result['video_path']
            session.mp3_path = result['mp3_path']
            session.usage = result.get('usage', {})
            
            info = f"""
✅ **อัปโหลดสำเร็จ!**

📁 **ไฟล์:** {result['original_filename']}
⏱️ **ความยาว:** {format_time(result['duration_seconds'])}
💾 **ขนาด:** {result['file_size_mb']} MB

🎉 **พร้อมแกะเสียงแล้ว!** ไปที่ Tab "2️⃣ แกะเสียง" เพื่อดำเนินการต่อ
"""
            quota_text = format_quota_display()
            
            return info, gr.update(visible=True), video_file, result['mp3_path'], quota_text
        else:
            # Handle error responses
            try:
                error_detail = response.json().get('detail', 'Unknown error')
            except:
                error_detail = response.text or 'Unknown error'
            
            error_msg = f"""
❌ **อัปโหลดไม่สำเร็จ**

{error_detail}
"""
            return error_msg, gr.update(visible=False), None, None, format_quota_display()
            
    except requests.exceptions.RequestException as e:
        error_msg = f"""
❌ **เกิดข้อผิดพลาดในการเชื่อมต่อ**

ไม่สามารถเชื่อมต่อกับ backend server ได้
กรุณาตรวจสอบว่า backend กำลังทำงานอยู่

รายละเอียด: {str(e)}
"""
        return error_msg, gr.update(visible=False), None, None, format_quota_display()
    except Exception as e:
        import traceback
        traceback.print_exc()
        error_msg = f"""
❌ **เกิดข้อผิดพลาด**

{str(e)}
"""
        return error_msg, gr.update(visible=False), None, None, format_quota_display()

# ==================== Step 2: Transcription ====================

def transcribe_audio(provider: str):
    """Transcribe audio to text"""
    if not session.file_id:
        return "❌ กรุณาอัปโหลดวิดีโอก่อน", None, gr.update(visible=False)
    
    try:
        response = requests.post(
            f"{API_URL}/transcribe/{session.file_id}",
            data={"provider": provider},
            headers=get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            session.transcription = result['transcription']
            
            # Format transcription for display
            segments = session.transcription['segments']
            text_display = "\n\n".join([
                f"[{format_time(seg['start'])} - {format_time(seg['end'])}]\n{seg['text']}"
                for seg in segments
            ])
            
            info = f"✅ แกะเสียงสำเร็จด้วย {provider}!\n\n📝 จำนวน segments: {len(segments)}"
            
            return info, text_display, gr.update(visible=True)
        else:
            return f"❌ แกะเสียงไม่สำเร็จ: {response.json().get('detail', 'Unknown error')}", None, gr.update(visible=False)
            
    except Exception as e:
        return f"❌ เกิดข้อผิดพลาด: {str(e)}", None, gr.update(visible=False)

# ==================== Step 3: Edit Subtitles ====================

def get_subtitle_list():
    """Get subtitle segments as list for display and editing"""
    if not session.transcription:
        return [], ""
    
    segments = session.transcription['segments']
    
    # Create formatted list for display and editing
    subtitle_text = ""
    for i, seg in enumerate(segments):
        subtitle_text += f"[{i+1}] {format_time(seg['start'])} → {format_time(seg['end'])}\n"
        subtitle_text += f"{seg['text']}\n\n"
    
    return segments, subtitle_text

def parse_edited_subtitles(edited_text: str):
    """Parse edited subtitle text back to segments"""
    if not edited_text or not session.transcription:
        return None
    
    try:
        segments = []
        lines = edited_text.strip().split('\n')
        
        i = 0
        while i < len(lines):
            line = lines[i].strip()
            
            # Look for timestamp line [N] HH:MM:SS → HH:MM:SS
            if line.startswith('[') and '→' in line:
                # Extract index and timestamps
                parts = line.split(']', 1)
                if len(parts) < 2:
                    i += 1
                    continue
                
                timestamp_part = parts[1].strip()
                times = timestamp_part.split('→')
                if len(times) < 2:
                    i += 1
                    continue
                
                start_str = times[0].strip()
                end_str = times[1].strip()
                
                # Get the text (next line)
                i += 1
                if i < len(lines):
                    text = lines[i].strip()
                    
                    # Convert time strings back to seconds
                    start_seconds = time_str_to_seconds(start_str)
                    end_seconds = time_str_to_seconds(end_str)
                    
                    segments.append({
                        'start': start_seconds,
                        'end': end_seconds,
                        'text': text
                    })
            
            i += 1
        
        return segments
        
    except Exception as e:
        print(f"Error parsing edited subtitles: {e}")
        import traceback
        traceback.print_exc()
        return None

def time_str_to_seconds(time_str: str) -> float:
    """Convert HH:MM:SS to seconds"""
    try:
        parts = time_str.split(':')
        if len(parts) == 3:
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        return 0.0
    except:
        return 0.0

def get_video_file():
    """Download video file for Gradio player"""
    if not session.file_id or not session.video_path:
        return None
    
    try:
        # For local backend, use the video path directly if accessible
        if os.path.exists(session.video_path):
            return session.video_path
        
        # Otherwise, download from API
        response = requests.get(
            f"{API_URL}/stream-video/{session.file_id}",
            headers=get_headers(),
            stream=True
        )
        
        if response.status_code == 200:
            # Save to temp file
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"video_{session.file_id}.mp4")
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return temp_path
        else:
            print(f"Failed to download video: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"Error getting video file: {e}")
        import traceback
        traceback.print_exc()
        return None

def update_subtitle_text(segment_index: int, new_text: str):
    """Update a specific subtitle segment"""
    if not session.transcription or segment_index < 0:
        return "❌ ไม่พบข้อมูล subtitle", get_subtitle_list()[1]
    
    try:
        segments = session.transcription['segments']
        if segment_index >= len(segments):
            return "❌ ไม่พบ segment ที่ระบุ", get_subtitle_list()[1]
        
        # Update the segment
        segments[segment_index]['text'] = new_text
        
        # Refresh display
        _, subtitle_text = get_subtitle_list()
        
        return f"✅ อัปเดต segment #{segment_index + 1} สำเร็จ!", subtitle_text
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ เกิดข้อผิดพลาด: {str(e)}", get_subtitle_list()[1]

def save_edited_subtitles(edited_text: str):
    """Save edited subtitle text to backend"""
    if not session.file_id or not session.transcription:
        return "❌ ไม่มีข้อมูลที่จะบันทึก", edited_text
    
    try:
        # Parse edited text back to segments
        segments = parse_edited_subtitles(edited_text)
        
        if not segments:
            return "❌ ไม่สามารถแปลงข้อความที่แก้ไขได้ กรุณาตรวจสอบรูปแบบ", edited_text
        
        # Update session
        session.transcription['segments'] = segments
        
        # Send to backend
        response = requests.post(
            f"{API_URL}/update-srt/{session.file_id}",
            json={"segments": segments},
            headers=get_headers()
        )
        
        if response.status_code == 200:
            success_msg = f"""
✅ **บันทึกการแก้ไขสำเร็จ!**

📝 จำนวน segments: {len(segments)}

🎉 **พร้อมแปลภาษาแล้ว!** ไปที่ Tab "4️⃣ แปลภาษา" เพื่อดำเนินการต่อ
"""
            return success_msg, edited_text
        else:
            return f"❌ บันทึกไม่สำเร็จ: {response.json().get('detail', 'Unknown error')}", edited_text
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ เกิดข้อผิดพลาด: {str(e)}", edited_text

def refresh_subtitle_editor():
    """Refresh subtitle editor to original state"""
    _, subtitle_text = get_subtitle_list()
    return subtitle_text, "🔄 รีเฟรชเรียบร้อย"

def get_segment_at_index(index: int):
    """Get segment data at specific index"""
    if not session.transcription or index < 0:
        return "", 0.0, 0.0
    
    segments = session.transcription['segments']
    if index >= len(segments):
        return "", 0.0, 0.0
    
    seg = segments[index]
    return seg['text'], seg['start'], seg['end']

# ==================== Step 4: Translation ====================

def translate_subtitles(target_language: str, style_prompt: str, provider: str):
    """Translate subtitles"""
    if not session.file_id:
        return "❌ กรุณาทำขั้นตอนก่อนหน้านี้ให้เสร็จก่อน", None
    
    try:
        data = {
            "file_id": session.file_id,
            "target_language": target_language,
            "provider": provider
        }
        if style_prompt:
            data["style_prompt"] = style_prompt
        
        response = requests.post(
            f"{API_URL}/translate",
            data=data,
            headers=get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            
            info = f"✅ แปลเป็น {target_language} สำเร็จด้วย {provider}!"
            
            # Download the translated SRT file immediately
            srt_file = download_srt(target_language)
            
            return info, srt_file
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            return f"❌ แปลไม่สำเร็จ: {error_detail}", None
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ เกิดข้อผิดพลาด: {str(e)}", None

def download_srt(language: str):
    """Download SRT file"""
    if not session.file_id:
        return None
    
    try:
        response = requests.get(
            f"{API_URL}/download-srt/{session.file_id}/{language}",
            headers=get_headers(),
            stream=True
        )
        
        if response.status_code == 200:
            # Save to temp file
            import tempfile
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"subtitle_{session.file_id}_{language}.srt")
            
            with open(temp_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            # Verify file exists
            if os.path.exists(temp_path):
                return temp_path
            else:
                print(f"File not created: {temp_path}")
                return None
        else:
            error_msg = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            print(f"Download failed: {error_msg}")
            return None
            
    except Exception as e:
        print(f"Download error: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==================== Step 5: Embed Subtitles ====================

def embed_subtitles(
    language: str,
    subtitle_type: str,
    speed_preset: str,
    font_name: str,
    font_size: int,
    bold: bool,
    outline: float,
    shadow: float,
    font_color: str,
    outline_color: str
):
    """Embed subtitles into video"""
    if not session.file_id:
        return "❌ กรุณาทำขั้นตอนก่อนหน้านี้ให้เสร็จก่อน", None
    
    try:
        data = {
            "file_id": session.file_id,
            "language": language,
            "type": subtitle_type,
            "speed_preset": speed_preset,
            "font_name": font_name,
            "font_size": font_size,
            "bold": bold,
            "outline": outline,
            "shadow": shadow,
            "font_color": font_color,
            "outline_color": outline_color
        }
        
        response = requests.post(
            f"{API_URL}/embed-subtitles",
            json=data,
            headers=get_headers()
        )
        
        if response.status_code == 200:
            result = response.json()
            output_path = result['output_path']
            
            info = f"✅ ฝัง {subtitle_type} subtitle สำเร็จ!"
            
            # Check if file exists locally
            if os.path.exists(output_path):
                return info, output_path
            else:
                # Try to download the video
                try:
                    download_response = requests.get(
                        f"{API_URL}/download-video/{session.file_id}/{language}/{subtitle_type}",
                        headers=get_headers(),
                        stream=True
                    )
                    
                    if download_response.status_code == 200:
                        # Save to temp file
                        temp_dir = tempfile.gettempdir()
                        temp_path = os.path.join(temp_dir, f"embedded_{session.file_id}_{language}_{subtitle_type}.mp4")
                        
                        with open(temp_path, 'wb') as f:
                            for chunk in download_response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        
                        return info, temp_path
                    else:
                        return info + "\n⚠️ แต่ไม่สามารถดาวน์โหลดวิดีโอได้", None
                except Exception as download_error:
                    print(f"Download error: {download_error}")
                    return info + f"\n⚠️ ไม่สามารถดาวน์โหลดวิดีโอได้: {str(download_error)}", None
        else:
            error_detail = response.json().get('detail', 'Unknown error') if response.headers.get('content-type') == 'application/json' else response.text
            return f"❌ ฝัง subtitle ไม่สำเร็จ: {error_detail}", None
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        return f"❌ เกิดข้อผิดพลาด: {str(e)}", None

# ==================== UI ====================

def create_ui():
    with gr.Blocks(title="Video Subtitle Generator", theme=gr.themes.Soft()) as app:
        gr.Markdown("""
        # 🎬 Video Subtitle Generator
        ### แปลงวิดีโอเป็นซับไตเติ้ลหลายภาษาด้วย AI
        """)
        
        # Login Section
        with gr.Column(visible=True) as login_section:
            gr.Markdown("""
            ## 🔐 เข้าสู่ระบบ
            
            กรุณาเข้าสู่ระบบเพื่อใช้งาน Video Subtitle Generator
            """)
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("")
                with gr.Column(scale=2):
                    username_input = gr.Textbox(
                        label="Username", 
                        placeholder="กรอก username",
                        info="ใช้ username ที่ได้รับจาก admin"
                    )
                    password_input = gr.Textbox(
                        label="Password", 
                        type="password", 
                        placeholder="กรอก password",
                        info="ใช้ password ที่ได้รับจาก admin"
                    )
                    login_btn = gr.Button("🔓 เข้าสู่ระบบ", variant="primary", size="lg")
                    login_status = gr.Markdown("")
                with gr.Column(scale=1):
                    gr.Markdown("")
        
        # Main App Section
        with gr.Column(visible=False) as main_section:
            # Header with user info and quota
            with gr.Row():
                with gr.Column(scale=2):
                    user_display = gr.Markdown("👤 ผู้ใช้งาน")
                with gr.Column(scale=1):
                    logout_btn = gr.Button("🚪 ออกจากระบบ", variant="stop", size="sm")
            
            # Quota Display
            quota_display = gr.Markdown("", label="Quota")
            
            with gr.Tabs():
                # Tab 1: Upload Video
                with gr.Tab("1️⃣ อัปโหลดวิดีโอ"):
                    gr.Markdown("""
                    ### 📤 อัปโหลดไฟล์วิดีโอ
                    
                    **ขั้นตอน:**
                    1. เลือกไฟล์วิดีโอจากเครื่องของคุณ
                    2. กดปุ่ม "อัปโหลด"
                    3. รอให้ระบบแปลงเป็น MP3
                    4. ไปที่ Tab "2️⃣ แกะเสียง" เพื่อดำเนินการต่อ
                    """)
                    
                    # Display limits
                    def get_limits_display():
                        limits = session.limits or get_limits()
                        if limits:
                            max_size = limits.get('maxFileSizeMB', 500)
                            max_duration = limits.get('maxDurationMinutes', 10)
                            return f"""
**ข้อจำกัด:**
- 📏 ขนาดไฟล์สูงสุด: {max_size} MB
- ⏱️ ความยาววิดีโอสูงสุด: {max_duration} นาที
- 📁 รองรับไฟล์: MP4, MOV, AVI, MKV, WMV
"""
                        return "**รองรับไฟล์:** MP4, MOV, AVI, MKV, WMV"
                    
                    limits_display = gr.Markdown(get_limits_display())
                    video_input = gr.Video(label="เลือกไฟล์วิดีโอ")
                    upload_btn = gr.Button("📤 อัปโหลดและแปลง MP3", variant="primary", size="lg")
                    upload_status = gr.Markdown("")
                    
                    with gr.Accordion("📹 ตัวอย่างวิดีโอและไฟล์ MP3", open=False):
                        video_preview = gr.Video(label="ตัวอย่างวิดีโอ", visible=False)
                        audio_preview = gr.Audio(label="ไฟล์ MP3", visible=False)
                
                # Tab 2: Transcription
                with gr.Tab("2️⃣ แกะเสียง") as transcribe_tab:
                    transcribe_tab_content = gr.Column(visible=False)
                    with transcribe_tab_content:
                        gr.Markdown("""
                        ### 🎤 แกะเสียงเป็นข้อความ
                        
                        **ขั้นตอน:**
                        1. เลือกผู้ให้บริการ (แนะนำ Botnoi สำหรับภาษาไทย)
                        2. กดปุ่ม "เริ่มแกะเสียง"
                        3. รอให้ระบบประมวลผล (อาจใช้เวลาสักครู่)
                        4. ตรวจสอบผลการแกะเสียง
                        5. ไปที่ Tab "3️⃣ แก้ไข Subtitle" เพื่อแก้ไขข้อความ
                        """)
                        
                        provider_transcribe = gr.Radio(
                            choices=["botnoi"],
                            value="botnoi",
                            label="เลือกผู้ให้บริการ ASR",
                            info="Botnoi: เหมาะสำหรับภาษาไทย, ความแม่นยำสูง"
                        )
                        transcribe_btn = gr.Button("🎤 เริ่มแกะเสียง", variant="primary", size="lg")
                        transcribe_status = gr.Markdown("")
                        
                        with gr.Accordion("📝 ผลการแกะเสียง (ดูรายละเอียด)", open=True):
                            transcription_output = gr.Textbox(
                                label="",
                                lines=15,
                                interactive=False,
                                show_label=False
                            )
                
                # Tab 3: Edit Subtitles
                with gr.Tab("3️⃣ แก้ไข Subtitle") as edit_tab:
                    edit_tab_content = gr.Column(visible=False)
                    with edit_tab_content:
                        gr.Markdown("""
                        ### 🎬 แก้ไข Subtitle พร้อมดูวิดีโอ
                        
                        **คำแนะนำ:**
                        - เล่นวิดีโอด้านซ้าย
                        - แก้ไข subtitle ในช่องด้านขวาได้เลย
                        - เมื่อแก้ไขเสร็จแล้ว กด "💾 บันทึกการแก้ไขทั้งหมด"
                        """)
                        
                        with gr.Row():
                            # Left: Video Player
                            with gr.Column(scale=1):
                                gr.Markdown("#### 📹 วิดีโอต้นฉบับ")
                                edit_video = gr.Video(
                                    label="",
                                    autoplay=False,
                                    show_label=False
                                )
                                current_subtitle_display = gr.Textbox(
                                    label="Subtitle ที่กำลังเล่น",
                                    interactive=False,
                                    lines=3,
                                    placeholder="เล่นวิดีโอเพื่อดู subtitle"
                                )
                            
                            # Right: Editable Subtitle List
                            with gr.Column(scale=1):
                                gr.Markdown("#### 📝 แก้ไข Subtitle (แก้ไขได้เลยในช่องนี้)")
                                subtitle_editor = gr.Textbox(
                                    label="",
                                    lines=25,
                                    interactive=True,
                                    show_label=False,
                                    placeholder="รายการ subtitle จะแสดงที่นี่...",
                                    info="แก้ไขข้อความ subtitle ได้โดยตรง (อย่าแก้ไข timestamp)"
                                )
                        
                        gr.Markdown("---")
                        
                        with gr.Row():
                            save_all_btn = gr.Button(
                                "💾 บันทึกการแก้ไขทั้งหมด", 
                                variant="primary", 
                                size="lg",
                                scale=2
                            )
                            refresh_btn = gr.Button(
                                "🔄 รีเฟรช (ยกเลิกการแก้ไข)", 
                                variant="secondary",
                                scale=1
                            )
                        
                        edit_status = gr.Markdown("")
                
                # Tab 4: Translation
                with gr.Tab("4️⃣ แปลภาษา"):
                    gr.Markdown("""
                    ### 🌍 แปล Subtitle เป็นภาษาอื่น
                    
                    **ขั้นตอน:**
                    1. เลือกภาษาเป้าหมาย
                    2. (ไม่บังคับ) กำหนด Style การแปล
                    3. กดปุ่ม "แปลภาษา"
                    4. รอให้ระบบแปล
                    5. ดาวน์โหลดไฟล์ SRT ที่แปลแล้ว
                    """)
                    
                    with gr.Row():
                        language_select = gr.Dropdown(
                            choices=["english", "lao", "burmese", "khmer", "vietnamese"],
                            label="🌐 เลือกภาษาเป้าหมาย",
                            value="english",
                            info="เลือกภาษาที่ต้องการแปล"
                        )
                        provider_translate = gr.Radio(
                            choices=["botnoi"],
                            value="botnoi",
                            label="เลือกผู้ให้บริการ",
                            info="Botnoi: รองรับหลายภาษา"
                        )
                    
                    style_input = gr.Textbox(
                        label="🎨 Style Prompt (ไม่บังคับ)",
                        placeholder="เช่น: แปลเป็นภาษาที่เป็นทางการ, ใช้คำง่ายๆ, แปลแบบสบายๆ",
                        info="กำหนดสไตล์การแปลตามต้องการ"
                    )
                    
                    translate_btn = gr.Button("🌍 แปลภาษา", variant="primary", size="lg")
                    translate_status = gr.Markdown("")
                    
                    gr.Markdown("---")
                    gr.Markdown("### 📥 ดาวน์โหลดไฟล์ SRT")
                    
                    with gr.Row():
                        download_lang = gr.Dropdown(
                            choices=["original", "english", "lao", "burmese", "khmer", "vietnamese"],
                            label="เลือกภาษา",
                            value="original",
                            info="เลือกภาษาที่ต้องการดาวน์โหลด"
                        )
                        download_srt_btn = gr.Button("📥 ดาวน์โหลด SRT", variant="secondary")
                    
                    srt_file = gr.File(label="ไฟล์ SRT", interactive=False)
                
                # Tab 5: Embed Subtitles
                with gr.Tab("5️⃣ ฝัง Subtitle"):
                    gr.Markdown("""
                    ### 🎞️ ฝัง Subtitle เข้ากับวิดีโอ
                    
                    **ขั้นตอน:**
                    1. เลือกภาษา subtitle ที่ต้องการฝัง
                    2. เลือกประเภท: Hard (ฝังติดวิดีโอ) หรือ Soft (แยกไฟล์)
                    3. ปรับแต่งฟอนต์ (สำหรับ Hard subtitle)
                    4. กดปุ่ม "ฝัง Subtitle"
                    5. รอให้ระบบประมวลผล
                    6. ดาวน์โหลดวิดีโอที่ฝัง subtitle แล้ว
                    """)
                    
                    with gr.Row():
                        embed_language = gr.Dropdown(
                            choices=["original", "english", "lao", "burmese", "khmer", "vietnamese"],
                            label="🌐 เลือกภาษา Subtitle",
                            value="original",
                            info="เลือกภาษาที่ต้องการฝังในวิดีโอ"
                        )
                        subtitle_type = gr.Radio(
                            choices=["hard", "soft"],
                            value="hard",
                            label="📝 ประเภท Subtitle",
                            info="Hard: ฝังติดวิดีโอ | Soft: แยกไฟล์ subtitle"
                        )
                    
                    with gr.Accordion("⚙️ ตั้งค่าขั้นสูง (สำหรับ Hard Subtitle)", open=False):
                        gr.Markdown("**ความเร็วในการประมวลผล**")
                        speed_preset = gr.Radio(
                            choices=["fast", "balanced", "quality"],
                            value="balanced",
                            label="",
                            info="Fast: เร็วแต่คุณภาพต่ำ | Balanced: สมดุล | Quality: ช้าแต่คุณภาพสูง"
                        )
                        
                        gr.Markdown("**การตั้งค่าฟอนต์**")
                        with gr.Row():
                            font_name = gr.Textbox(
                                value="TH Sarabun New", 
                                label="ชื่อฟอนต์",
                                info="ฟอนต์ที่รองรับภาษาไทย"
                            )
                            font_size = gr.Slider(
                                10, 50, value=20, step=1, 
                                label="ขนาดฟอนต์",
                                info="ขนาดตัวอักษร (px)"
                            )
                        
                        with gr.Row():
                            bold = gr.Checkbox(value=True, label="ตัวหนา")
                            outline = gr.Slider(
                                0, 5, value=1.5, step=0.1, 
                                label="ความหนาขอบ",
                                info="ขอบตัวอักษร"
                            )
                            shadow = gr.Slider(
                                0, 5, value=1.0, step=0.1, 
                                label="เงา",
                                info="เงาตัวอักษร"
                            )
                        
                        with gr.Row():
                            font_color = gr.Textbox(
                                value="white", 
                                label="สีตัวอักษร",
                                info="เช่น: white, yellow, #FFFFFF"
                            )
                            outline_color = gr.Textbox(
                                value="black", 
                                label="สีขอบ",
                                info="เช่น: black, #000000"
                            )
                    
                    embed_btn = gr.Button("🎞️ ฝัง Subtitle เข้ากับวิดีโอ", variant="primary", size="lg")
                    embed_status = gr.Markdown("")
                    
                    gr.Markdown("### 📹 วิดีโอที่ฝัง Subtitle แล้ว")
                    output_video = gr.Video(label="", show_label=False)
                    
                    gr.Markdown("### 📥 ดาวน์โหลดวิดีโอ")
                    download_video_file = gr.File(label="ไฟล์วิดีโอที่ฝัง Subtitle", interactive=False)
        
        # Event Handlers
        def login_and_update_limits(username, password):
            """Login and update limits display"""
            result = login(username, password)
            # Get limits display
            limits = session.limits or get_limits()
            if limits:
                max_size = limits.get('maxFileSizeMB', 500)
                max_duration = limits.get('maxDurationMinutes', 10)
                limits_text = f"""
**ข้อจำกัด:**
- 📏 ขนาดไฟล์สูงสุด: {max_size} MB
- ⏱️ ความยาววิดีโอสูงสุด: {max_duration} นาที
- 📁 รองรับไฟล์: MP4, MOV, AVI, MKV, WMV
"""
            else:
                limits_text = "**รองรับไฟล์:** MP4, MOV, AVI, MKV, WMV"
            
            return result + (limits_text,)
        
        login_btn.click(
            login_and_update_limits,
            inputs=[username_input, password_input],
            outputs=[login_section, main_section, login_status, quota_display, user_display, limits_display]
        )
        
        logout_btn.click(
            logout,
            outputs=[login_section, main_section, login_status, quota_display, user_display]
        )
        
        upload_btn.click(
            upload_video,
            inputs=[video_input],
            outputs=[upload_status, transcribe_tab_content, video_preview, audio_preview, quota_display]
        )
        
        def transcribe_and_prepare_edit(provider):
            """Transcribe and prepare edit tab"""
            if not session.file_id:
                return (
                    "❌ กรุณาอัปโหลดวิดีโอก่อน",
                    "",
                    gr.update(visible=False),
                    None,
                    ""
                )
            
            try:
                # Call transcribe API
                response = requests.post(
                    f"{API_URL}/transcribe/{session.file_id}",
                    data={"provider": provider},
                    headers=get_headers()
                )
                
                if response.status_code == 200:
                    result = response.json()
                    session.transcription = result['transcription']
                    
                    # Format transcription for display
                    segments = session.transcription['segments']
                    text_display = "\n\n".join([
                        f"[{format_time(seg['start'])} - {format_time(seg['end'])}]\n{seg['text']}"
                        for seg in segments
                    ])
                    
                    status = f"""
✅ **แกะเสียงสำเร็จด้วย {provider}!**

📝 จำนวน segments: {len(segments)}

➡️ **ขั้นตอนถัดไป:** ไปที่ Tab "3️⃣ แก้ไข Subtitle" เพื่อแก้ไขข้อความ
"""
                    
                    # Get subtitle list for editing
                    _, subtitle_text = get_subtitle_list()
                    
                    # Get video file path
                    video_file = get_video_file()
                    
                    return (
                        status,
                        text_display,
                        gr.update(visible=True),
                        video_file,
                        subtitle_text
                    )
                else:
                    error_msg = response.json().get('detail', 'Unknown error')
                    return (
                        f"❌ แกะเสียงไม่สำเร็จ: {error_msg}",
                        "",
                        gr.update(visible=False),
                        None,
                        ""
                    )
                    
            except Exception as e:
                import traceback
                traceback.print_exc()
                return (
                    f"❌ เกิดข้อผิดพลาด: {str(e)}",
                    "",
                    gr.update(visible=False),
                    None,
                    ""
                )
        
        transcribe_btn.click(
            transcribe_and_prepare_edit,
            inputs=[provider_transcribe],
            outputs=[
                transcribe_status, 
                transcription_output, 
                edit_tab_content,
                edit_video,
                subtitle_editor
            ]
        )
        
        # Save edited subtitles
        save_all_btn.click(
            save_edited_subtitles,
            inputs=[subtitle_editor],
            outputs=[edit_status, subtitle_editor]
        )
        
        # Refresh subtitle editor
        refresh_btn.click(
            refresh_subtitle_editor,
            outputs=[subtitle_editor, edit_status]
        )
        
        translate_btn.click(
            translate_subtitles,
            inputs=[language_select, style_input, provider_translate],
            outputs=[translate_status, srt_file]
        )
        
        download_srt_btn.click(
            download_srt,
            inputs=[download_lang],
            outputs=[srt_file]
        )
        
        def embed_and_prepare_download(
            language, subtitle_type, speed_preset,
            font_name, font_size, bold, outline, shadow,
            font_color, outline_color
        ):
            """Embed subtitles and prepare for download"""
            status, video_path = embed_subtitles(
                language, subtitle_type, speed_preset,
                font_name, font_size, bold, outline, shadow,
                font_color, outline_color
            )
            
            # Return video path for both preview and download
            return status, video_path, video_path
        
        embed_btn.click(
            embed_and_prepare_download,
            inputs=[
                embed_language, subtitle_type, speed_preset,
                font_name, font_size, bold, outline, shadow,
                font_color, outline_color
            ],
            outputs=[embed_status, output_video, download_video_file]
        )
    
    return app

if __name__ == "__main__":
    app = create_ui()
    app.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False
    )
