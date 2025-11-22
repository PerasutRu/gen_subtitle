# Testing Duplicate Prevention

## วิธีทดสอบ:

### 1. Restart Backend
```bash
# Stop backend
# Start backend again
```

### 2. ทดสอบ Transcribe
- Upload video
- Click transcribe
- ดูใน terminal ว่ามี message นี้ไหม:
  ```
  ⚠️ Duplicate activity log prevented: transcribe for {file_id}
  ```

### 3. เช็ค Database
```bash
sqlite3 backend/data/sessions.db "
SELECT id, created_at, activity_type, file_id 
FROM activity_logs 
WHERE activity_type = 'transcribe' 
ORDER BY created_at DESC 
LIMIT 5;
"
```

## Expected Results:

### ถ้าทำงานถูกต้อง:
- ✅ เห็น warning message ใน terminal
- ✅ มี log แค่ 1 รายการ
- ✅ ไม่มี duplicate

### ถ้ายังซ้ำอยู่:
- ❌ ไม่เห็น warning message
- ❌ มี 2 logs
- 🔍 ต้องเช็คเพิ่ม

## Debug Steps:

### 1. เช็คว่า code ถูก deploy
```python
# ใน database.py ควรมี:
from datetime import timedelta
five_seconds_ago = (datetime.now() - timedelta(seconds=5)).isoformat()
```

### 2. เช็ค log details
```bash
sqlite3 backend/data/sessions.db "
SELECT 
    id,
    created_at,
    activity_type,
    file_id,
    session_id,
    status
FROM activity_logs 
WHERE activity_type = 'transcribe' 
ORDER BY created_at DESC 
LIMIT 10;
"
```

### 3. เช็คว่า file_id ตรงกันไหม
ถ้า file_id ต่างกัน → ไม่ถือว่า duplicate (ถูกต้อง)

## Alternative: ถ้ายังไม่ได้ผล

ใช้ UNIQUE constraint แทน:

```sql
CREATE UNIQUE INDEX idx_unique_activity 
ON activity_logs(session_id, activity_type, file_id, 
                 strftime('%Y-%m-%d %H:%M:%S', created_at));
```

แต่วิธีนี้จะ error ถ้าซ้ำ (ไม่ silent)
