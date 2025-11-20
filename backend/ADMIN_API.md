# Admin API Documentation

API endpoints สำหรับจัดการ quota และ sessions (ไม่แสดงใน frontend)

## Base URL
```
http://localhost:8000
```

## Admin Endpoints

### 1. ดูรายการ Session ทั้งหมด
```bash
GET /admin/sessions
```

**Response:**
```json
{
  "total": 5,
  "sessions": [
    {
      "session_id": "session_123",
      "created_at": "2024-11-20T10:00:00",
      "last_activity": "2024-11-20T10:30:00",
      "video_count": 3,
      "total_duration": 450.5
    }
  ]
}
```

**ตัวอย่างการใช้งาน:**
```bash
curl http://localhost:8000/admin/sessions
```

---

### 2. ดูสถิติการใช้งานทั้งหมด
```bash
GET /admin/stats
```

**Response:**
```json
{
  "stats": {
    "total_sessions": 10,
    "total_videos": 45,
    "total_duration_seconds": 5400,
    "total_duration_minutes": 90,
    "total_size_mb": 2500,
    "total_size_gb": 2.44
  },
  "limits": {
    "maxVideos": 10,
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  }
}
```

**ตัวอย่างการใช้งาน:**
```bash
curl http://localhost:8000/admin/stats
```

---

### 3. ลบ Session เฉพาะ
```bash
DELETE /admin/session/{session_id}
```

**Parameters:**
- `session_id` - ID ของ session ที่ต้องการลบ

**Response:**
```json
{
  "message": "ลบ session session_123 สำเร็จ"
}
```

**ตัวอย่างการใช้งาน:**
```bash
curl -X DELETE http://localhost:8000/admin/session/session_123
```

---

### 4. Reset ลบ Session ทั้งหมด
```bash
POST /admin/reset
```

**Response:**
```json
{
  "message": "Reset สำเร็จ ลบ session ทั้งหมดแล้ว",
  "timestamp": "2024-11-20T11:00:00"
}
```

**ตัวอย่างการใช้งาน:**
```bash
curl -X POST http://localhost:8000/admin/reset
```

---

### 5. โหลดค่า Limits ใหม่
```bash
POST /admin/reload-limits
```

**Response:**
```json
{
  "message": "โหลดค่า limits ใหม่สำเร็จ",
  "limits": {
    "maxVideos": 10,
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  }
}
```

**ตัวอย่างการใช้งาน:**
```bash
curl -X POST http://localhost:8000/admin/reload-limits
```

**หมายเหตุ:** ใช้เมื่อแก้ไขไฟล์ `config/limits.json` แล้วต้องการให้ระบบโหลดค่าใหม่โดยไม่ต้อง restart server

---

## การใช้งานจริง

### ตัวอย่าง: Reset Quota ทุกวัน
```bash
# สร้าง cron job ที่รันทุกวันเวลา 00:00
0 0 * * * curl -X POST http://localhost:8000/admin/reset
```

### ตัวอย่าง: ดูสถิติการใช้งาน
```bash
# ดูสถิติแบบ pretty print
curl http://localhost:8000/admin/stats | python -m json.tool
```

### ตัวอย่าง: ลบ Session เก่า
```bash
# ดูรายการ session ก่อน
curl http://localhost:8000/admin/sessions

# ลบ session ที่ต้องการ
curl -X DELETE http://localhost:8000/admin/session/session_old_123
```

---

## Database Location

ข้อมูล session ถูกเก็บใน SQLite database:
```
backend/data/sessions.db
```

### ตารางในฐานข้อมูล:

**sessions**
- session_id (TEXT, PRIMARY KEY)
- created_at (TEXT)
- last_activity (TEXT)

**videos**
- id (INTEGER, PRIMARY KEY)
- session_id (TEXT, FOREIGN KEY)
- file_id (TEXT)
- file_size_mb (REAL)
- duration_seconds (REAL)
- uploaded_at (TEXT)

---

## Security Note

⚠️ **คำเตือน:** Admin endpoints เหล่านี้ไม่มีการ authentication ในตอนนี้

สำหรับ production ควร:
1. เพิ่ม API key authentication
2. จำกัด IP ที่สามารถเข้าถึงได้
3. ใช้ HTTPS
4. เพิ่ม rate limiting

---

## ตัวอย่าง Python Script

```python
import requests

BASE_URL = "http://localhost:8000"

# ดูสถิติ
response = requests.get(f"{BASE_URL}/admin/stats")
print(response.json())

# Reset ทั้งหมด
response = requests.post(f"{BASE_URL}/admin/reset")
print(response.json())

# ดูรายการ session
response = requests.get(f"{BASE_URL}/admin/sessions")
sessions = response.json()["sessions"]
print(f"Total sessions: {len(sessions)}")

# ลบ session แรก
if sessions:
    session_id = sessions[0]["session_id"]
    response = requests.delete(f"{BASE_URL}/admin/session/{session_id}")
    print(response.json())
```
