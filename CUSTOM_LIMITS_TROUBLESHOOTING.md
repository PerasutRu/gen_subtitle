# Custom Limits Troubleshooting Guide

## ✅ สิ่งที่แก้ไขแล้ว

### ปัญหาที่พบ:
ตั้งค่า custom quota แล้วแต่ไม่เห็นดึงค่ามาใช้

### สาเหตุ:
API endpoints ใช้ `session_manager.get_limits()` แทนที่จะใช้ `get_limits_for_session(session_id)`

### การแก้ไข:

#### 1. แก้ไข `/user/session` endpoint
```python
# เดิม
limits = session_manager.get_limits()  # ❌ ได้ default เสมอ

# ใหม่
limits = session_manager.get_limits_for_session(session_id)  # ✅ ได้ custom ถ้ามี
```

#### 2. แก้ไข `/session/{session_id}/usage` endpoint
```python
# เดิม
limits = session_manager.get_limits()  # ❌ ได้ default เสมอ

# ใหม่
limits = session_manager.get_limits_for_session(session_id)  # ✅ ได้ custom ถ้ามี
```

#### 3. เพิ่ม Debug Logging
```python
def get_limits_for_session(self, session_id: str) -> dict:
    if session_id.startswith("user_"):
        username = session_id.replace("user_", "")
        user = self.db.get_user(username)
        
        if user and user.get("custom_limits"):
            print(f"✅ Using custom limits for {username}: {user['custom_limits']}")
            return user["custom_limits"]
        else:
            print(f"ℹ️ No custom limits for {username}, using default")
    
    return self.limits
```

---

## 🧪 การทดสอบ

### ขั้นตอนที่ 1: ตรวจสอบ Database

```bash
# เช็คว่ามี column custom_limits
sqlite3 backend/data/sessions.db ".schema users"

# เช็คว่ามี custom_limits ใน users
sqlite3 backend/data/sessions.db "SELECT username, custom_limits FROM users WHERE custom_limits IS NOT NULL;"
```

**ผลลัพธ์ที่คาดหวัง:**
```
test1|{"maxVideos": 2, "maxDurationMinutes": 10, "maxFileSizeMB": 500}
test2|{"maxVideos": 4, "maxDurationMinutes": 5, "maxFileSizeMB": 120}
```

### ขั้นตอนที่ 2: Restart Backend

```bash
# หยุด backend (Ctrl+C)
# จากนั้นเริ่มใหม่
cd gen_subtitle
./start-backend.sh
```

### ขั้นตอนที่ 3: ทดสอบด้วย Test Script

```bash
cd gen_subtitle
python3 test_custom_limits.py
```

**ผลลัพธ์ที่คาดหวัง:**
```
1. Testing login...
   ✅ Login successful

2. Testing /user/session...
   ✅ Session retrieved
   Session ID: user_test1
   Username: test1
   Limits: {
     "maxVideos": 2,
     "maxDurationMinutes": 10,
     "maxFileSizeMB": 500
   }

RESULT:
✅ Custom limits are being used!
   maxVideos: 2 (expected: 2)
```

### ขั้นตอนที่ 4: ทดสอบใน Frontend

1. Login as test1
2. เปิด Browser DevTools (F12)
3. ไปที่ Network tab
4. Refresh หน้า
5. ดู request `/user/session`
6. ตรวจสอบ response:

```json
{
  "session_id": "user_test1",
  "username": "test1",
  "usage": {...},
  "limits": {
    "maxVideos": 2,  // ← ต้องเป็น 2 (custom)
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  }
}
```

---

## 🔍 Debug Checklist

### ✅ Backend:
- [ ] Database มี column `custom_limits`
- [ ] User มี custom_limits ใน database
- [ ] Backend ถูก restart แล้ว
- [ ] เห็น debug log "✅ Using custom limits for..."
- [ ] API `/user/session` return custom limits

### ✅ Frontend:
- [ ] Frontend ถูก refresh แล้ว (Ctrl+Shift+R)
- [ ] Clear browser cache
- [ ] ดู Network tab เห็น custom limits
- [ ] Quota display แสดงค่าถูกต้อง

---

## 🐛 ปัญหาที่อาจพบ

### ปัญหา 1: ยังเห็น default limits
**สาเหตุ:**
- Backend ยังไม่ restart
- Frontend cache

**วิธีแก้:**
```bash
# 1. Restart backend
cd gen_subtitle
./start-backend.sh

# 2. Hard refresh frontend
# กด Ctrl+Shift+R (หรือ Cmd+Shift+R บน Mac)
```

### ปัญหา 2: Database ไม่มี custom_limits
**สาเหตุ:**
- Database เก่ายังไม่มี column

**วิธีแก้:**
```bash
# ลบ database และสร้างใหม่
rm backend/data/sessions.db
./start-backend.sh
```

### ปัญหา 3: Session ID ไม่ถูกต้อง
**สาเหตุ:**
- Session ID ไม่ได้เป็น format `user_{username}`

**วิธีแก้:**
- ตรวจสอบว่า login ใช้ `/user/session` endpoint
- Session ID ต้องเป็น `user_test1` ไม่ใช่ random UUID

### ปัญหา 4: JSON parse error
**สาเหตุ:**
- custom_limits ใน database เป็น JSON ที่ไม่ valid

**วิธีแก้:**
```bash
# ทดสอบ parse JSON
python3 -c "
import sqlite3, json
conn = sqlite3.connect('backend/data/sessions.db')
cursor = conn.cursor()
cursor.execute('SELECT username, custom_limits FROM users WHERE custom_limits IS NOT NULL')
for username, limits_str in cursor.fetchall():
    try:
        limits = json.loads(limits_str)
        print(f'✅ {username}: OK')
    except Exception as e:
        print(f'❌ {username}: {e}')
conn.close()
"
```

---

## 📊 Expected Behavior

### User ที่มี Custom Limits:
```
test1 login
→ session_id: user_test1
→ get_limits_for_session("user_test1")
→ ดึง user test1 จาก database
→ เจอ custom_limits
→ return {"maxVideos": 2, ...}
```

### User ที่ไม่มี Custom Limits:
```
test3 login
→ session_id: user_test3
→ get_limits_for_session("user_test3")
→ ดึง user test3 จาก database
→ ไม่เจอ custom_limits
→ return default limits {"maxVideos": 10, ...}
```

---

## 🎯 Quick Fix Commands

```bash
# 1. เช็ค database
sqlite3 backend/data/sessions.db "SELECT username, custom_limits FROM users;"

# 2. Restart backend
cd gen_subtitle
./start-backend.sh

# 3. Test API
python3 test_custom_limits.py

# 4. ดู backend logs
# ควรเห็น: "✅ Using custom limits for test1: ..."
```

---

## ✅ Success Indicators

เมื่อทำงานถูกต้อง จะเห็น:

1. **Backend logs:**
```
✅ Using custom limits for test1: {'maxVideos': 2, 'maxDurationMinutes': 10, 'maxFileSizeMB': 500}
```

2. **API Response:**
```json
{
  "limits": {
    "maxVideos": 2,  // ← custom value
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  }
}
```

3. **Frontend Display:**
```
Quota: 0/2 ไฟล์  // ← แสดง 2 ไม่ใช่ 10
```

---

## 📝 Summary

**ไฟล์ที่แก้ไข:**
- ✅ `backend/main.py` - แก้ไข 2 endpoints
- ✅ `backend/services/session_manager.py` - เพิ่ม debug logging

**ขั้นตอนที่ต้องทำ:**
1. ✅ Restart backend
2. ✅ Hard refresh frontend
3. ✅ ทดสอบด้วย test script
4. ✅ ตรวจสอบ logs และ API response

**ตอนนี้ระบบควรทำงานได้แล้ว!** 🎉
