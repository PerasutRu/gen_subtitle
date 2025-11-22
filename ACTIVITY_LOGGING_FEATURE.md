# Activity Logging Feature

ระบบบันทึกและติดตาม activities ทั้งหมดที่เกิดขึ้นในระบบ พร้อม Admin Dashboard สำหรับดูและวิเคราะห์

## ✨ Features

### 1. Activity Logging
บันทึก activities ทั้งหมด:
- **Upload** - อัปโหลดวิดีโอ
- **Transcribe** - แกะเสียง
- **Translate** - แปลซับไตเติ้ล
- **Embed Subtitle** - ฝังซับไตเติ้ล

### 2. ข้อมูลที่บันทึก
- Session ID / Username
- Activity Type
- File ID
- Details (JSON):
  - Provider (openai/botnoi)
  - Target Language
  - Style Prompt
  - Subtitle Type (hard/soft)
  - Font Settings
  - File Size, Duration
- Status (success/failed)
- Error Message (ถ้ามี)
- Timestamp

### 3. Admin Dashboard - Activity Logs Tab

#### Filters:
- **Activity Type** - กรองตามประเภท activity
- **Username** - กรองตาม user
- **Status** - Success/Failed
- **Date Range** - ช่วงเวลา

#### Features:
- **Pagination** - 30 รายการต่อหน้า
- **Detail Modal** - คลิกดูรายละเอียดเต็ม
- **Color-coded Badges**:
  - 🔵 Upload (Blue)
  - 🟢 Transcribe (Green)
  - 🟡 Translate (Yellow)
  - 🟣 Embed (Purple)
- **Real-time Search** - ค้นหาจาก username, file_id

### 4. Activity Statistics
แสดงในหน้า System Stats:
- **Total Activities** - จำนวน activities ทั้งหมด
- **Activities by Type** - แยกตามประเภท
- **Provider Usage** - OpenAI vs Botnoi
- **Success Rate** - อัตราความสำเร็จ
- **Language Usage** - ภาษาที่แปลมากที่สุด
- **Recent Trends** - กราฟ 7 วันล่าสุด

## 📊 Database Schema

### Table: `activity_logs`
```sql
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    username TEXT,
    activity_type TEXT NOT NULL,
    file_id TEXT,
    details TEXT,  -- JSON
    status TEXT NOT NULL DEFAULT 'success',
    error_message TEXT,
    created_at TEXT NOT NULL
)
```

### Indexes:
- `idx_activity_session` - session_id
- `idx_activity_type` - activity_type
- `idx_activity_created` - created_at

## 🔌 API Endpoints

### GET /admin/activities
ดึง activity logs พร้อม filters

**Query Parameters:**
- `limit` (default: 50)
- `offset` (default: 0)
- `activity_type` (optional)
- `session_id` (optional)
- `username` (optional)
- `status` (optional)
- `date_from` (optional)
- `date_to` (optional)

**Response:**
```json
{
  "total": 150,
  "activities": [...],
  "limit": 50,
  "offset": 0
}
```

### GET /admin/activities/stats
ดึงสถิติ activities

**Response:**
```json
{
  "total_activities": 150,
  "by_type": {
    "upload": 50,
    "transcribe": 40,
    "translate": 35,
    "embed_subtitle": 25
  },
  "by_status": {
    "success": 145,
    "failed": 5
  },
  "provider_usage": {
    "openai": 60,
    "botnoi": 15
  },
  "language_usage": {
    "en": 20,
    "th": 10,
    "jp": 5
  },
  "recent_by_date": [...]
}
```

## 💻 Frontend Components

### 1. ActivityLogs.jsx
- Activity logs table with filters
- Pagination
- Detail modal
- Color-coded badges

### 2. SystemStats.jsx (Updated)
- เพิ่ม Activity Statistics section
- แสดงกราฟและสถิติ

### 3. AdminDashboard.jsx (Updated)
- เพิ่มแท็บ "Activity Logs"

## 🎯 Use Cases

### 1. Monitoring
- ดูว่า user ทำอะไรบ้าง
- ติดตามการใช้งาน provider (OpenAI vs Botnoi)
- เช็คภาษาที่แปลมากที่สุด

### 2. Debugging
- ดู error logs
- ตรวจสอบ failed activities
- วิเคราะห์ปัญหา

### 3. Analytics
- วิเคราะห์พฤติกรรมการใช้งาน
- ดู trends
- วางแผน capacity

### 4. Auditing
- ตรวจสอบการใช้งานของ user
- ดูประวัติการทำงาน
- Compliance tracking

## 🚀 การใช้งาน

### Admin Dashboard:
1. Login เป็น admin
2. ไปที่แท็บ "Activity Logs"
3. ใช้ filters เพื่อค้นหา
4. คลิกไอคอน 👁️ เพื่อดูรายละเอียด

### System Stats:
1. ไปที่แท็บ "สถิติระบบ"
2. ดู "Activity Statistics" section
3. วิเคราะห์ข้อมูล

## 📝 ตัวอย่าง Activity Details

### Upload:
```json
{
  "file_size_mb": 45.2,
  "duration_seconds": 145.3,
  "original_filename": "video.mp4"
}
```

### Transcribe:
```json
{
  "provider": "openai",
  "segments_count": 42
}
```

### Translate:
```json
{
  "provider": "botnoi",
  "target_language": "en",
  "style_prompt": "แปลแบบเป็นทางการ",
  "segments_count": 42
}
```

### Embed Subtitle:
```json
{
  "subtitle_type": "hard",
  "language": "th",
  "speed_preset": "balanced",
  "font_settings": {
    "font_name": "TH Sarabun New",
    "font_size": 20,
    "bold": true
  }
}
```

## 🔧 Technical Details

### Backend:
- `database.py` - เพิ่ม `log_activity()`, `get_activities()`, `get_activity_stats()`
- `main.py` - เพิ่ม logging ใน endpoints ทั้งหมด
- Automatic logging on success/failure

### Frontend:
- `ActivityLogs.jsx` - Main component
- `SystemStats.jsx` - Activity stats display
- `adminApi.js` - API functions

### Performance:
- Indexed queries สำหรับ fast filtering
- Pagination เพื่อจำกัด data load
- Efficient JSON parsing

## 🎨 UI/UX Highlights

- **Color-coded badges** - แยกแยะ activity type ง่าย
- **Responsive design** - ใช้งานได้ทุกหน้าจอ
- **Quick filters** - กรองข้อมูลได้รวดเร็ว
- **Detail modal** - ดูรายละเอียดแบบเต็ม
- **Clean layout** - อ่านง่าย ไม่ยุ่งเหยิง

## 📈 Future Enhancements

- Export to CSV
- Real-time updates (WebSocket)
- Advanced charts (Chart.js)
- Activity alerts/notifications
- Log retention policy
- Archive old logs

---

**Status:** ✅ Implemented and Ready to Use
**Version:** 1.0.0
**Date:** November 23, 2025
