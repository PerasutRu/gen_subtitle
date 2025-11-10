# การตั้งค่า Botnoi Gensub API

## ขั้นตอนการตั้งค่า

### 1. สมัครและรับ API Key

1. ไปที่ https://voice.botnoi.ai/developer/api
2. สมัครสมาชิกหรือเข้าสู่ระบบ
3. สร้าง API Key ใหม่
4. คัดลอก API Key ที่ได้

### 2. ตั้งค่า Environment Variable

เพิ่ม `BOTNOI_API_KEY` ในไฟล์ `.env`:

```bash
BOTNOI_API_KEY=your_botnoi_api_key_here
```

### 3. API Endpoints ที่ใช้

#### 3.1 Transcription (แกะเสียง)
- **Endpoint**: `/gensub_upload`
- **Method**: POST
- **Headers**: 
  - `Botnoi-Token`: your_api_key
- **Body**: 
  - `file`: audio file (multipart/form-data)

#### 3.2 Translation (แปลภาษา)
- **Endpoint**: `/translate`
- **Method**: POST
- **Headers**: 
  - `Botnoi-Token`: your_api_key
- **Body** (JSON):
  ```json
  {
    "text": "ข้อความที่ต้องการแปล",
    "target_lang": "en"
  }
  ```

### 4. รหัสภาษาที่รองรับ

- `th` - ภาษาไทย
- `en` - อังกฤษ
- `lo` - ลาว
- `my` - พม่า
- `km` - กัมพูชา
- `vi` - เวียดนาม

## การใช้งาน

### ในส่วน Backend

ระบบจะตรวจสอบว่ามี `BOTNOI_API_KEY` หรือไม่ ถ้ามีจะเปิดใช้งาน Botnoi service อัตโนมัติ

### ในส่วน Frontend

1. **ขั้นตอนแกะเสียง**: เลือก "Botnoi Gensub" แทน "OpenAI Whisper"
2. **ขั้นตอนแปลภาษา**: เลือก provider เป็น "Botnoi" สำหรับแต่ละภาษา

## ข้อควรระวัง

1. Botnoi API อาจมีข้อจำกัดด้านขนาดไฟล์และระยะเวลา
2. ตรวจสอบ rate limit และ quota ของ API Key
3. Botnoi เหมาะสำหรับภาษาไทยเป็นพิเศษ
4. Response format อาจแตกต่างจาก OpenAI ระบบจะปรับให้เข้ากันอัตโนมัติ

## Troubleshooting

### ปัญหา: "Botnoi service ไม่พร้อมใช้งาน"
- ตรวจสอบว่าได้ตั้งค่า `BOTNOI_API_KEY` ในไฟล์ `.env` แล้ว
- Restart backend server

### ปัญหา: "Botnoi API error"
- ตรวจสอบว่า API Key ถูกต้อง
- ตรวจสอบว่ามี credit เพียงพอ
- ตรวจสอบขนาดไฟล์ไม่เกินที่กำหนด

### ปัญหา: Response format ไม่ถูกต้อง
- ระบบจะพยายามแปลง response ให้เข้ากับรูปแบบมาตรฐาน
- ถ้ายังมีปัญหา ให้ตรวจสอบ log และแก้ไขใน `botnoi_service.py`

## เอกสารเพิ่มเติม

- [Botnoi API Documentation](https://voice.botnoi.ai/developer/api)
- [Botnoi Developer Portal](https://voice.botnoi.ai/developer)
