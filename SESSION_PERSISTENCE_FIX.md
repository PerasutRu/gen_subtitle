# แก้ไขปัญหา Session Persistence

## ปัญหา

เมื่อ login user เดิม quota ไม่ถูกดึงมาจาก session เดิม แต่เริ่มใหม่ทุกครั้ง

### สาเหตุ

1. **Backend สร้าง session_id แบบ random UUID** ไม่ได้ผูกกับ username
2. **Frontend ไม่ได้เก็บ session_id ไว้** เมื่อ logout หรือ refresh จะหายไป
3. **ไม่มีการ link session กับ user** ทำให้ไม่สามารถดึง session เดิมกลับมาได้

### ตัวอย่างปัญหา

```
User A login ครั้งที่ 1:
- Upload 3 วิดีโอ
- Quota: 3/10 ไฟล์
- Logout

User A login ครั้งที่ 2:
- Quota: 0/10 ไฟล์ ❌ (ควรเป็น 3/10)
```

---

## การแก้ไข

### 1. เปลี่ยน Session ID จาก Random UUID เป็น Username-based

**เดิม:**
```python
session_id = str(uuid.uuid4())  # เช่น "a1b2c3d4-..."
```

**ใหม่:**
```python
session_id = f"user_{username}"  # เช่น "user_john"
```

**ประโยชน์:**
- Session ผูกกับ username
- Login ครั้งต่อไปจะได้ session เดิม
- ไม่ต้องเก็บ session_id ที่ client

---

### 2. เพิ่ม API Endpoint: GET `/user/session`

Backend เพิ่ม endpoint ใหม่สำหรับดึง session ของ user:

```python
@app.get("/user/session")
async def get_user_session(current_user: dict = Depends(get_current_user)):
    """ดึง session ของ user ปัจจุบัน"""
    # Use username as session_id for persistence
    username = current_user["username"]
    session_id = f"user_{username}"
    
    # Get or create session
    session_manager.get_or_create_session(session_id)
    
    # Get usage
    usage = session_manager.get_session_usage(session_id)
    limits = session_manager.get_limits()
    
    return {
        "session_id": session_id,
        "username": username,
        "usage": usage,
        "limits": limits
    }
```

**Response Example:**
```json
{
  "session_id": "user_john",
  "username": "john",
  "usage": {
    "videos_count": 3,
    "total_duration": 450.5,
    "remaining_videos": 7,
    "remaining_duration": 149.5
  },
  "limits": {
    "maxVideos": 10,
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  }
}
```

---

### 3. ปรับ Upload Endpoint ให้ใช้ Username-based Session

**เดิม:**
```python
if not session_id:
    session_id = session_manager.get_or_create_session()
else:
    session_manager.get_or_create_session(session_id)
```

**ใหม่:**
```python
# Use username-based session for persistence
username = current_user["username"]
if not session_id:
    session_id = f"user_{username}"

# Get or create session
session_manager.get_or_create_session(session_id)
```

---

### 4. ปรับ Frontend ให้ดึง Session หลัง Login

**เดิม:**
```python
# Get limits after login
get_limits()

# Try to get existing session usage if available
if session.session_id:
    get_session_usage()

quota_text = format_quota_display()
```

**ใหม่:**
```python
# Get limits after login
get_limits()

# Get user's session (this will retrieve existing session or create new one)
try:
    session_response = requests.get(
        f"{API_URL}/user/session",
        headers=get_headers()
    )
    if session_response.status_code == 200:
        session_data = session_response.json()
        session.session_id = session_data["session_id"]
        session.usage = session_data.get("usage", {})
        session.limits = session_data.get("limits", session.limits)
        print(f"✅ Loaded session: {session.session_id}, usage: {session.usage}")
    else:
        print(f"⚠️ Could not load session: {session_response.status_code}")
except Exception as e:
    print(f"⚠️ Error loading session: {e}")

quota_text = format_quota_display()
```

---

## การทำงานของระบบใหม่

### Flow การทำงาน:

```
1. User login
   ↓
2. Frontend เรียก GET /user/session
   ↓
3. Backend ตรวจสอบ session ของ username
   - ถ้ามี: ดึง usage เดิมกลับมา
   - ถ้าไม่มี: สร้าง session ใหม่
   ↓
4. Frontend แสดง quota ที่ถูกต้อง
```

### ตัวอย่างการทำงาน:

#### Scenario 1: User ใหม่ (Login ครั้งแรก)
```
User A login ครั้งที่ 1:
- Backend สร้าง session: "user_A"
- Usage: 0 วิดีโอ
- Quota: 0/10 ไฟล์ ✅
```

#### Scenario 2: User เดิม (Login ครั้งที่ 2)
```
User A login ครั้งที่ 1:
- Upload 3 วิดีโอ
- Quota: 3/10 ไฟล์
- Logout

User A login ครั้งที่ 2:
- Backend ดึง session: "user_A"
- Usage: 3 วิดีโอ (จาก database)
- Quota: 3/10 ไฟล์ ✅
```

#### Scenario 3: หลายครั้งในวันเดียวกัน
```
User A login เช้า:
- Upload 2 วิดีโอ
- Quota: 2/10 ไฟล์
- Logout

User A login บ่าย:
- Quota: 2/10 ไฟล์ ✅ (ยังคงอยู่)
- Upload 3 วิดีโอเพิ่ม
- Quota: 5/10 ไฟล์
```

---

## ประโยชน์

### 1. Session Persistence
- ✅ User login ครั้งต่อไปจะเห็น quota เดิม
- ✅ ไม่ต้องเริ่มนับใหม่ทุกครั้ง
- ✅ Track การใช้งานได้ต่อเนื่อง

### 2. ไม่ต้องเก็บ Session ID ที่ Client
- ✅ ไม่ต้องกังวลเรื่อง session หายเมื่อ refresh
- ✅ ไม่ต้องใช้ localStorage หรือ cookies
- ✅ Backend เป็นตัวจัดการทั้งหมด

### 3. Admin สามารถ Track ได้ง่าย
- ✅ Session ID = username ทำให้หาง่าย
- ✅ Admin รู้ว่า user ไหนใช้ quota เท่าไหร่
- ✅ สามารถ reset quota ของ user เฉพาะได้

---

## การทดสอบ

### Test Case 1: User ใหม่ Login ครั้งแรก
**ขั้นตอน:**
1. Login ด้วย user ใหม่
2. ตรวจสอบ quota

**ผลลัพธ์ที่คาดหวัง:**
```
Quota: 0/10 ไฟล์
Session ID: user_newuser
```

---

### Test Case 2: Upload และ Login ใหม่
**ขั้นตอน:**
1. Login ด้วย user A
2. Upload 3 วิดีโอ
3. Logout
4. Login ด้วย user A อีกครั้ง
5. ตรวจสอบ quota

**ผลลัพธ์ที่คาดหวัง:**
```
Login ครั้งที่ 1:
- Upload 3 วิดีโอ
- Quota: 3/10 ไฟล์

Login ครั้งที่ 2:
- Quota: 3/10 ไฟล์ ✅ (ยังคงอยู่)
```

---

### Test Case 3: หลาย User แยกกัน
**ขั้นตอน:**
1. User A login และ upload 3 วิดีโอ
2. Logout
3. User B login และ upload 5 วิดีโอ
4. Logout
5. User A login อีกครั้ง

**ผลลัพธ์ที่คาดหวัง:**
```
User A:
- Session: user_A
- Quota: 3/10 ไฟล์ ✅

User B:
- Session: user_B
- Quota: 5/10 ไฟล์ ✅

User A (login ใหม่):
- Quota: 3/10 ไฟล์ ✅ (ไม่ปนกับ User B)
```

---

### Test Case 4: Refresh Browser
**ขั้นตอน:**
1. Login
2. Upload 2 วิดีโอ
3. Refresh browser (F5)
4. Login อีกครั้ง

**ผลลัพธ์ที่คาดหวัง:**
```
หลัง refresh และ login ใหม่:
- Quota: 2/10 ไฟล์ ✅ (ยังคงอยู่)
```

---

### Test Case 5: API Error Handling
**ขั้นตอน:**
1. ปิด backend
2. Login (จะล้มเหลว)
3. เปิด backend
4. Login อีกครั้ง

**ผลลัพธ์ที่คาดหวัง:**
```
Backend ปิด:
- Login ล้มเหลว
- แสดง error message

Backend เปิด:
- Login สำเร็จ
- Quota แสดงถูกต้อง
```

---

## Debug และ Monitoring

### ดู Session ID ใน Console
```python
print(f"✅ Loaded session: {session.session_id}, usage: {session.usage}")
```

**Output Example:**
```
✅ Loaded session: user_john, usage: {'videos_count': 3, 'total_duration': 450.5, ...}
```

### ตรวจสอบ API Call
```bash
# ดู session ของ user
curl -X GET http://localhost:8000/user/session \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**Response:**
```json
{
  "session_id": "user_john",
  "username": "john",
  "usage": {
    "videos_count": 3,
    "remaining_videos": 7
  }
}
```

### Admin: ดู Session ทั้งหมด
```bash
curl -X GET http://localhost:8000/admin/sessions \
  -H "Authorization: Bearer ADMIN_TOKEN"
```

---

## ไฟล์ที่แก้ไข

### Backend
- `gen_subtitle/backend/main.py`
  - เพิ่ม endpoint `GET /user/session`
  - ปรับ `POST /upload-video` ให้ใช้ username-based session

### Frontend
- `gen_subtitle/gradio/app.py`
  - ปรับ `login()` ให้เรียก `/user/session` หลัง login
  - เพิ่ม error handling สำหรับกรณีดึง session ไม่สำเร็จ

---

## หมายเหตุ

### Session Lifetime
- Session จะถูกเก็บใน database
- ไม่มีการหมดอายุอัตโนมัติ (ขึ้นอยู่กับ backend implementation)
- Admin สามารถ reset session ได้ผ่าน admin endpoints

### Security
- Session ID ใช้ username ทำให้คาดเดาได้
- แต่ยังต้องมี JWT token ในการเข้าถึง
- ไม่มีปัญหาด้าน security เพราะต้อง authenticate ก่อน

### Performance
- การใช้ username-based session ทำให้ query ง่ายขึ้น
- ไม่ต้องเก็บ mapping table ระหว่าง user กับ session
- Database query เร็วขึ้น (index by session_id)

---

## Troubleshooting

### ปัญหา: Quota ยังไม่แสดงหลัง login
**วิธีแก้:**
1. ตรวจสอบ console logs
2. ดูว่า API `/user/session` ถูกเรียกหรือไม่
3. ตรวจสอบ response จาก API

### ปัญหา: Quota แสดงผิด
**วิธีแก้:**
1. กดปุ่ม "🔄 รีเฟรช Quota"
2. ตรวจสอบ database ว่ามีข้อมูล session หรือไม่
3. ตรวจสอบ session_id ว่าถูกต้องหรือไม่

### ปัญหา: Session ปนกันระหว่าง users
**วิธีแก้:**
1. ตรวจสอบว่า session_id ใช้ username ถูกต้อง
2. ตรวจสอบว่า logout ทำงานถูกต้อง
3. Clear session ใน database และลองใหม่
