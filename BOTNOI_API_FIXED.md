# Botnoi API - Fixed Implementation

## ปัญหาที่พบ

1. **405 Not Allowed** - ใช้ endpoint หรือ method ไม่ถูกต้อง
2. **Header ไม่ถูกต้อง** - ต้องใช้ `botnoi-token` (lowercase)
3. **Parameters ไม่ครบ** - `/gensub_upload` ต้องมี parameters เพิ่มเติม

## การแก้ไข

### 1. `/gensub_upload` Endpoint

**Parameters ที่ต้องส่ง:**
```python
files = {
    "audio_file": (filename, file_content, "audio/mpeg")
}

data = {
    "max_duration": "10",      # Maximum chunk duration in seconds
    "max_silence": "0.3",      # Maximum silence allowed in seconds
    "language": "th",          # Language used for transcription
    "srt": "yes"              # Set to 'yes' for SRT response
}

headers = {
    "botnoi-token": "YOUR_API_KEY"  # lowercase!
}
```

**Response Format:**
```json
{
  "data": {
    "current_monthly_point": 858,
    "current_point": 100,
    "text": "1\n00:00:00,000 --> 00:00:02,858\nสวัสดีครับ\n\n2\n00:00:02,858 --> 00:00:04,008\nยินดีต้อนรับ\n\n",
    "used_points": 20
  },
  "message": "Transcribe successfully"
}
```

### 2. `/translate` Endpoint

**Request Body:**
```json
{
  "language": "en",
  "native_style": true,
  "simple_style": true,
  "text": "สวัสดีครับ"
}
```

**Headers:**
```python
headers = {
    "botnoi-token": "YOUR_API_KEY",
    "Content-Type": "application/json"
}
```

**Response Format:**
```json
{
  "data": {
    "language": "en",
    "native_style": true,
    "simple_style": true,
    "text": "Hello"
  },
  "message": "translation generated successfully"
}
```

## การใช้งาน

### 1. Restart Backend
```bash
# หยุด backend (Ctrl+C)
./start-backend.sh
```

### 2. ทดสอบ
1. อัปโหลดวิดีโอ
2. เลือก "Botnoi Gensub"
3. กดเริ่มแกะเสียง

### 3. ดู Log
```
[Botnoi] Uploading file: uploads/xxx.mp3
[Botnoi] Response status: 200
[Botnoi] Response body: {...}
[Botnoi] Upload data keys: dict_keys(['data', 'message'])
[Botnoi] Got SRT text, length: 1234
[Botnoi] Parsed 10 segments from SRT
```

## สิ่งที่แก้ไข

### ใน `botnoi_service.py`:

1. ✅ เปลี่ยน header จาก `Botnoi-Token` เป็น `botnoi-token`
2. ✅ เพิ่ม parameters: `max_duration`, `max_silence`, `language`, `srt`
3. ✅ เปลี่ยน file field จาก `file` เป็น `audio_file`
4. ✅ Parse SRT text จาก `data.text`
5. ✅ เพิ่มฟังก์ชัน `_parse_srt_to_segments()`
6. ✅ เพิ่มฟังก์ชัน `_srt_time_to_seconds()`
7. ✅ แก้ไข `/translate` ให้ส่ง JSON body ที่ถูกต้อง
8. ✅ Parse response จาก `data.text`

## ตัวอย่าง Response

### Transcription Response:
```json
{
  "data": {
    "current_monthly_point": 858,
    "current_point": 100,
    "text": "1\n00:00:00,000 --> 00:00:02,858\nสวัสดีครับ ยินดีต้อนรับ\n\n2\n00:00:02,858 --> 00:00:04,008\nวันนี้เราจะมาพูดถึง\n\n",
    "used_points": 20
  },
  "message": "Transcribe successfully"
}
```

### Translation Response:
```json
{
  "data": {
    "language": "en",
    "native_style": true,
    "simple_style": true,
    "text": "Hello, welcome"
  },
  "message": "translation generated successfully"
}
```

## การทดสอบ

### ทดสอบด้วย curl

**Transcription:**
```bash
curl -X POST https://voice.botnoi.ai/gensub_upload \
  -H "botnoi-token: YOUR_API_KEY" \
  -F "audio_file=@test.mp3" \
  -F "max_duration=10" \
  -F "max_silence=0.3" \
  -F "language=th" \
  -F "srt=yes"
```

**Translation:**
```bash
curl -X POST https://voice.botnoi.ai/translate \
  -H "botnoi-token: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "language": "en",
    "native_style": true,
    "simple_style": true,
    "text": "สวัสดีครับ"
  }'
```

## สรุป

การแก้ไขครั้งนี้ทำให้:
- ✅ ใช้ API endpoint ที่ถูกต้อง
- ✅ ส่ง parameters ครบถ้วน
- ✅ Parse response ได้ถูกต้อง
- ✅ รองรับ SRT format จาก Botnoi
- ✅ แปลภาษาได้ถูกต้อง

ระบบพร้อมใช้งานแล้ว!
