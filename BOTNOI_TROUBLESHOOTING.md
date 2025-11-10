# Botnoi API Troubleshooting

## ปัญหา: 405 Not Allowed

### สาเหตุที่เป็นไปได้:

1. **URL ไม่ถูกต้อง**
   - ตรวจสอบว่าใช้ `https://voice.botnoi.ai` ไม่ใช่ URL อื่น
   - ตรวจสอบว่า path เป็น `/gensub_upload` ไม่ใช่ `/gensub-upload` หรืออื่นๆ

2. **API Key ไม่ถูกต้อง**
   - ตรวจสอบว่า API Key ถูกต้อง
   - ตรวจสอบว่าไม่มีช่องว่างหรือ newline ใน API Key

3. **Header ไม่ถูกต้อง**
   - ต้องใช้ `botnoi-token` (lowercase)
   - ไม่ใช่ `Botnoi-Token` หรือ `Authorization`

4. **Method ไม่ถูกต้อง**
   - ต้องใช้ POST method
   - ไม่ใช่ GET, PUT, หรือ DELETE

## วิธีการ Debug

### 1. ตรวจสอบ API Key

```bash
# ดู API Key ใน .env
cat gen_subtitle/.env | grep BOTNOI_API_KEY

# ตรวจสอบว่าไม่มีช่องว่างหรือ newline
cat gen_subtitle/.env | grep BOTNOI_API_KEY | od -c
```

### 2. ทดสอบด้วย curl

```bash
# ตั้งค่า API Key
export BOTNOI_API_KEY="your_api_key_here"

# รัน test script
./test_botnoi_curl.sh
```

### 3. ตรวจสอบ Log

ดู log ใน terminal backend:
```
[Botnoi] Uploading file: uploads/xxx.mp3
[Botnoi] API Key: xxx...
[Botnoi] Base URL: https://voice.botnoi.ai
[Botnoi] POST URL: https://voice.botnoi.ai/gensub_upload
[Botnoi] Headers: {'botnoi-token': 'xxx...'}
[Botnoi] Data: {'max_duration': '10', ...}
[Botnoi] Response status: 405
```

## แนวทางแก้ไข

### แก้ไขที่ 1: ตรวจสอบ API Key

```bash
# ใน .env ต้องไม่มีช่องว่าง
BOTNOI_API_KEY=your_key_here

# ไม่ใช่
BOTNOI_API_KEY = your_key_here  # ❌ มีช่องว่าง
BOTNOI_API_KEY="your_key_here"  # ❌ มี quotes
```

### แก้ไขที่ 2: ลองใช้ API ผ่าน Postman/Insomnia

1. สร้าง POST request ไปยัง `https://voice.botnoi.ai/gensub_upload`
2. เพิ่ม header: `botnoi-token: your_key`
3. เพิ่ม form-data:
   - `audio_file`: เลือกไฟล์ MP3
   - `max_duration`: 10
   - `max_silence`: 0.3
   - `language`: th
   - `srt`: yes
4. ส่ง request และดู response

### แก้ไขที่ 3: ตรวจสอบ API Documentation

ไปที่ https://voice.botnoi.ai/developer/api และตรวจสอบ:
- URL ที่ถูกต้อง
- Header ที่ต้องใช้
- Parameters ที่ต้องส่ง
- Response format

### แก้ไขที่ 4: ติดต่อ Botnoi Support

ถ้าแก้ไม่ได้ ให้ติดต่อ Botnoi support:
- Email: support@botnoi.ai
- Website: https://voice.botnoi.ai
- แนบ error message และ request details

## ตัวอย่าง curl ที่ถูกต้อง

```bash
curl -X POST https://voice.botnoi.ai/gensub_upload \
  -H "botnoi-token: YOUR_API_KEY" \
  -F "audio_file=@test.mp3" \
  -F "max_duration=10" \
  -F "max_silence=0.3" \
  -F "language=th" \
  -F "srt=yes"
```

## ถ้ายังไม่ได้

### ทางเลือก 1: ใช้ OpenAI แทน

ถ้า Botnoi ยังไม่ทำงาน ให้ใช้ OpenAI ไปก่อน:
1. เลือก "OpenAI Whisper" แทน "Botnoi Gensub"
2. ระบบจะใช้ OpenAI API แทน

### ทางเลือก 2: รอ Botnoi แก้ไข API

อาจเป็นไปได้ว่า:
- Botnoi API กำลัง maintenance
- API endpoint เปลี่ยนแปลง
- มีปัญหาชั่วคราว

### ทางเลือก 3: ใช้ API อื่น

พิจารณาใช้ ASR API อื่นๆ เช่น:
- Google Cloud Speech-to-Text
- Azure Speech Services
- AWS Transcribe

## สรุป

ปัญหา 405 Not Allowed มักเกิดจาก:
1. ❌ URL ไม่ถูกต้อง
2. ❌ Method ไม่ถูกต้อง
3. ❌ API Key ไม่ถูกต้อง
4. ❌ Header ไม่ถูกต้อง

ให้ตรวจสอบทีละข้อและทดสอบด้วย curl ก่อน
