# Transcribe Logging Fix

## ปัญหา
```
object of type 'TranscriptionResult' has no len()
```

เกิดจากการพยายามใช้ `len(result)` กับ `TranscriptionResult` object ที่ไม่ support `__len__()` method

## สาเหตุ
ใน transcribe endpoint เพิ่ม activity logging โดยใช้:
```python
"segments_count": len(result)
```

แต่ `result` จาก `transcribe_with_timestamps()` เป็น object ไม่ใช่ list

## แก้ไข

### 1. Transcribe Endpoint
เปลี่ยนจาก:
```python
db.log_activity(
    session_id=session_id,
    activity_type="transcribe",
    file_id=file_id,
    details={
        "provider": provider,
        "segments_count": len(result)  # ❌ Error!
    },
    status="success"
)
```

เป็น:
```python
# Get segments count safely
segments_count = 0
if isinstance(result, list):
    segments_count = len(result)
elif hasattr(result, 'segments'):
    segments_count = len(result.segments)
elif hasattr(result, '__len__'):
    try:
        segments_count = len(result)
    except:
        segments_count = 0

db.log_activity(
    session_id=session_id,
    activity_type="transcribe",
    file_id=file_id,
    details={
        "provider": provider,
        "segments_count": segments_count  # ✅ Safe!
    },
    status="success"
)
```

### 2. Translate Endpoint (OpenAI)
เพิ่ม activity logging สำหรับ OpenAI provider ที่ขาดไป:
```python
# Log activity for OpenAI
db.log_activity(
    session_id=session_id,
    activity_type="translate",
    file_id=file_id,
    details={
        "provider": provider,
        "target_language": target_language,
        "style_prompt": style_prompt,
        "segments_count": len(segments)  # segments เป็น list จาก parse_srt_file
    },
    status="success"
)
```

## วิธีการ Handle Segments Count

### Safe Approach:
1. **Check if list** - `isinstance(result, list)`
2. **Check for segments attribute** - `hasattr(result, 'segments')`
3. **Try __len__** - ลองเรียก `len()` ใน try-except
4. **Default to 0** - ถ้าไม่ได้ทั้งหมด

### Why This Works:
- รองรับทั้ง list และ object
- ไม่ crash ถ้า structure เปลี่ยน
- Graceful degradation (ได้ 0 แทน error)

## Testing

### ทดสอบ Transcribe:
```bash
# OpenAI
curl -X POST http://localhost:8000/transcribe/{file_id} \
  -F "provider=openai" \
  -H "Authorization: Bearer <token>"

# Botnoi
curl -X POST http://localhost:8000/transcribe/{file_id} \
  -F "provider=botnoi" \
  -H "Authorization: Bearer <token>"
```

### ตรวจสอบ Activity Log:
```sql
SELECT * FROM activity_logs 
WHERE activity_type = 'transcribe' 
ORDER BY created_at DESC 
LIMIT 5;
```

ควรเห็น `segments_count` ใน details JSON

## Files Changed
- `backend/main.py` - แก้ transcribe และ translate endpoints

---

**Status:** ✅ Fixed
**Date:** November 23, 2025
