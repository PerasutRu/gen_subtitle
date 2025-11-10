# Debug Botnoi Integration

## ปัญหาที่พบ

เมื่อลองใช้ Botnoi provider เกิด error 400 Bad Request

## การแก้ไข

1. เพิ่ม logging ใน `botnoi_service.py` เพื่อดู response จาก Botnoi API
2. ปรับปรุง `_parse_botnoi_segments()` ให้รองรับหลาย format
3. เพิ่ม fallback mechanism ถ้าไม่พบ segments

## วิธีการ Debug

### 1. ดู Backend Logs

เมื่อใช้ Botnoi provider จะเห็น log แบบนี้:

```
[Botnoi] Uploading file: uploads/xxx.mp3
[Botnoi] Response status: 200
[Botnoi] Response body: {...}
[Botnoi] Upload data: {...}
[Botnoi] Parsing response data keys: [...]
[Botnoi] Found 'xxx' key
[Botnoi] Parsed X segments
```

### 2. ตรวจสอบ Response Format

จาก log จะเห็น response format ที่ Botnoi ส่งมา เช่น:

**Format 1: Direct segments**
```json
{
  "segments": [
    {"start": 0.0, "end": 1.5, "text": "สวัสดี"},
    {"start": 1.5, "end": 3.0, "text": "ครับ"}
  ]
}
```

**Format 2: Result with segments**
```json
{
  "result": {
    "segments": [...]
  }
}
```

**Format 3: Text only**
```json
{
  "text": "สวัสดีครับ ยินดีต้อนรับ",
  "file_path": "..."
}
```

### 3. แก้ไขตาม Response Format

ถ้า response format ไม่ตรงกับที่รองรับ ให้แก้ไข `_parse_botnoi_segments()` ใน `botnoi_service.py`

## ขั้นตอนการแก้ปัญหา

### Step 1: Restart Backend
```bash
# หยุด backend (Ctrl+C)
# รันใหม่
./start-backend.sh
```

### Step 2: ลองใช้ Botnoi อีกครั้ง
1. อัปโหลดวิดีโอ
2. เลือก "Botnoi Gensub"
3. ดู log ใน terminal backend

### Step 3: วิเคราะห์ Log
- ดู response status code
- ดู response body
- ดู keys ที่มีใน response
- ดูจำนวน segments ที่ parse ได้

### Step 4: แก้ไข Code (ถ้าจำเป็น)

ถ้า response format ไม่ตรง ให้เพิ่ม condition ใน `_parse_botnoi_segments()`:

```python
# Format ใหม่ที่พบ
elif "your_key" in response_data:
    print(f"[Botnoi] Found 'your_key' key")
    # Parse ตาม format ที่พบ
    ...
```

## ตัวอย่าง Error และวิธีแก้

### Error: "ไม่พบ file_path ใน response"
**สาเหตุ**: Botnoi API ไม่ส่ง file_path กลับมา  
**วิธีแก้**: ลบการตรวจสอบ file_path หรือทำให้เป็น optional

### Error: "ไม่พบข้อความหรือ segments ใน response"
**สาเหตุ**: Response format ไม่ตรงกับที่รองรับ  
**วิธีแก้**: ดู log และเพิ่ม format ใหม่ใน `_parse_botnoi_segments()`

### Error: 400 Bad Request
**สาเหตุ**: 
- API Key ไม่ถูกต้อง
- ไฟล์ไม่ถูก format
- ขนาดไฟล์เกินกำหนด

**วิธีแก้**:
1. ตรวจสอบ BOTNOI_API_KEY
2. ตรวจสอบไฟล์เป็น MP3
3. ตรวจสอบขนาดไฟล์

### Error: 401 Unauthorized
**สาเหตุ**: API Key ไม่ถูกต้องหรือหมดอายุ  
**วิธีแก้**: สร้าง API Key ใหม่

### Error: 429 Too Many Requests
**สาเหตุ**: เกิน rate limit  
**วิธีแก้**: รอสักครู่แล้วลองใหม่

## การทดสอบ

### ทดสอบด้วย Script
```bash
python test_botnoi.py
```

### ทดสอบด้วย curl
```bash
# ทดสอบ upload
curl -X POST https://voice.botnoi.ai/gensub_upload \
  -H "Botnoi-Token: YOUR_API_KEY" \
  -F "file=@test.mp3"
```

## Tips

1. **เก็บ Log**: Copy log ที่สำคัญไว้เพื่อวิเคราะห์
2. **ทดสอบกับไฟล์เล็ก**: ใช้ไฟล์เสียงสั้นๆ ในการทดสอบ
3. **ตรวจสอบ API Docs**: อ่าน Botnoi API documentation อีกครั้ง
4. **ติดต่อ Support**: ถ้าแก้ไม่ได้ ติดต่อ Botnoi support

## สรุป

การ debug Botnoi integration ต้องอาศัย:
1. Log ที่ชัดเจน
2. ความเข้าใจ response format
3. การปรับ code ให้รองรับ format ที่แท้จริง

หลังจากแก้ไขแล้ว ระบบควรทำงานได้ปกติ
