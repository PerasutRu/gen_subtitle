# User Quota Management Feature

## ✅ สิ่งที่ทำเสร็จแล้ว

### Backend Implementation

#### 1. Database Schema Update
- ✅ เพิ่มฟิลด์ `custom_limits` (JSON) ใน users table
- ✅ เพิ่มฟังก์ชัน `get_user_limits()`, `set_user_limits()`, `delete_user_limits()`
- ✅ แก้ไข `get_user()` และ `get_all_users()` ให้ return custom_limits

#### 2. Session Manager Update
- ✅ เพิ่มฟังก์ชัน `get_limits_for_session()` - ดึง custom limits ถ้ามี
- ✅ แก้ไข `can_upload()` ให้ใช้ custom limits
- ✅ แก้ไข `get_session_usage()` ให้คำนวณจาก custom limits

#### 3. API Endpoints
- ✅ `GET /admin/user/{username}/limits` - ดู limits ของ user
- ✅ `PUT /admin/user/{username}/limits` - ตั้งค่า custom limits
- ✅ `DELETE /admin/user/{username}/limits` - ลบ custom limits (ใช้ default)

### Frontend Implementation

#### 1. API Service
- ✅ เพิ่ม `getUserLimits()`, `setUserLimits()`, `deleteUserLimits()` ใน adminApi.js

#### 2. Components
- ✅ สร้าง `UserQuotaModal.jsx` - Modal สำหรับตั้งค่า quota
- ✅ แก้ไข `UserManagement.jsx` - เพิ่มปุ่ม "Quota" และแสดง custom limits

---

## 🎯 Features

### 1. ตั้งค่า Custom Quota แยกแต่ละ User
Admin สามารถตั้งค่า quota เฉพาะให้แต่ละ user ได้:
- จำนวนวิดีโอสูงสุด (maxVideos)
- ความยาววิดีโอสูงสุด (maxDurationMinutes)
- ขนาดไฟล์สูงสุด (maxFileSizeMB)

### 2. แสดง Custom Limits ในตาราง Users
- แสดง "Default" ถ้าใช้ค่า default
- แสดง "20/15/1000MB" ถ้ามี custom limits

### 3. Modal สำหรับแก้ไข Quota
- แสดงค่า default เป็น hint
- แสดงว่ามี custom limits อยู่แล้วหรือไม่
- ปุ่ม "ใช้ค่า Default" สำหรับลบ custom limits

### 4. Validation
- ตรวจสอบค่าต้องมากกว่า 0
- ตรวจสอบ required fields
- แสดง error message ที่ชัดเจน

---

## 📊 การทำงาน

### Flow การตั้งค่า Quota:

```
1. Admin เปิดหน้า User Management
   ↓
2. กดปุ่ม "Quota" ที่ user ที่ต้องการ
   ↓
3. Modal เปิดขึ้น แสดงฟอร์ม
   - โหลดค่า custom limits (ถ้ามี)
   - แสดงค่า default เป็น hint
   ↓
4. แก้ไขค่าและกด "บันทึก"
   ↓
5. เรียก API PUT /admin/user/{username}/limits
   ↓
6. Backend บันทึกลง database
   ↓
7. User นั้นจะใช้ custom limits ทันที
```

### Flow การใช้ Quota:

```
1. User upload วิดีโอ
   ↓
2. Backend ดึง session_id (format: user_username)
   ↓
3. Session Manager ดึง custom_limits จาก database
   - ถ้ามี → ใช้ custom limits
   - ถ้าไม่มี → ใช้ default limits
   ↓
4. ตรวจสอบ quota ตาม limits ที่ได้
   ↓
5. อนุญาตหรือปฏิเสธการ upload
```

---

## 🎨 UI/UX

### User Management Table:
```
┌──────────┬──────┬─────────────┬────────────┬─────────────┐
│ Username │ Role │ Quota       │ Created    │ Actions     │
├──────────┼──────┼─────────────┼────────────┼─────────────┤
│ john     │ user │ 20/15/1000MB│ 2024-01-01 │ [⚙️Quota][🗑️]│
│ jane     │ user │ Default     │ 2024-01-02 │ [⚙️Quota][🗑️]│
│ admin    │ admin│ -           │ 2024-01-01 │ [🗑️]        │
└──────────┴──────┴─────────────┴────────────┴─────────────┘
```

### Quota Modal:
```
┌─────────────────────────────────────────┐
│  ตั้งค่า Quota: john                   │
│  ℹ️ User นี้มี custom quota อยู่แล้ว   │
├─────────────────────────────────────────┤
│  จำนวนวิดีโอสูงสุด                     │
│  [20        ] ไฟล์                      │
│  Default: 10 ไฟล์                       │
│                                         │
│  ความยาววิดีโอสูงสุด (นาที)            │
│  [15        ] นาที                      │
│  Default: 10 นาที                       │
│                                         │
│  ขนาดไฟล์สูงสุด (MB)                   │
│  [1000      ] MB                        │
│  Default: 500 MB                        │
│                                         │
│  [ใช้ค่า Default]  [บันทึก]  [ยกเลิก] │
└─────────────────────────────────────────┘
```

---

## 🧪 การทดสอบ

### Test Case 1: ตั้งค่า Custom Quota
1. Login as admin
2. ไปที่ User Management
3. กดปุ่ม "Quota" ที่ user john
4. ตั้งค่า: 20 videos, 15 minutes, 1000 MB
5. กด "บันทึก"
6. ✅ ควรเห็น "20/15/1000MB" ในตาราง

### Test Case 2: User ใช้ Custom Quota
1. Login as john
2. Upload วิดีโอ
3. ✅ ควรใช้ quota ตาม custom limits (20 videos)

### Test 3: ลบ Custom Quota
1. Login as admin
2. กดปุ่ม "Quota" ที่ user john
3. กด "ใช้ค่า Default"
4. Confirm
5. ✅ ควรเห็น "Default" ในตาราง

### Test Case 4: User ใช้ Default Quota
1. Login as jane (ไม่มี custom limits)
2. Upload วิดีโอ
3. ✅ ควรใช้ quota ตาม default limits (10 videos)

### Test Case 5: Validation
1. พยายามตั้งค่า maxVideos = 0
2. ✅ ควรแสดง error "กรุณากรอกค่าที่มากกว่า 0"

### Test Case 6: Admin ไม่มีปุ่ม Quota
1. ดูตาราง users
2. ✅ Admin user ไม่ควรมีปุ่ม "Quota"

---

## 💾 Database Structure

### users table:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    created_at TEXT NOT NULL,
    custom_limits TEXT  -- JSON: {"maxVideos": 20, ...}
);
```

### ตัวอย่างข้อมูล:
```json
{
  "id": 1,
  "username": "john",
  "password_hash": "...",
  "role": "user",
  "created_at": "2024-01-01",
  "custom_limits": "{\"maxVideos\": 20, \"maxDurationMinutes\": 15, \"maxFileSizeMB\": 1000}"
}
```

---

## 🔧 API Documentation

### GET /admin/user/{username}/limits
ดู limits ของ user

**Response:**
```json
{
  "username": "john",
  "custom_limits": {
    "maxVideos": 20,
    "maxDurationMinutes": 15,
    "maxFileSizeMB": 1000
  },
  "default_limits": {
    "maxVideos": 10,
    "maxDurationMinutes": 10,
    "maxFileSizeMB": 500
  },
  "active_limits": {
    "maxVideos": 20,
    "maxDurationMinutes": 15,
    "maxFileSizeMB": 1000
  }
}
```

### PUT /admin/user/{username}/limits
ตั้งค่า custom limits

**Request Body:**
```json
{
  "maxVideos": 20,
  "maxDurationMinutes": 15,
  "maxFileSizeMB": 1000
}
```

**Response:**
```json
{
  "message": "ตั้งค่า limits สำหรับ john สำเร็จ",
  "username": "john",
  "custom_limits": {
    "maxVideos": 20,
    "maxDurationMinutes": 15,
    "maxFileSizeMB": 1000
  }
}
```

### DELETE /admin/user/{username}/limits
ลบ custom limits (ใช้ default)

**Response:**
```json
{
  "message": "ลบ custom limits สำหรับ john สำเร็จ (ใช้ default limits)",
  "username": "john"
}
```

---

## 📝 ไฟล์ที่แก้ไข/สร้าง

### Backend:
- ✅ `backend/services/database.py` - เพิ่ม custom_limits support
- ✅ `backend/services/session_manager.py` - ใช้ custom limits
- ✅ `backend/main.py` - เพิ่ม 3 API endpoints

### Frontend:
- ✅ `frontend/src/services/adminApi.js` - เพิ่ม API calls
- ✅ `frontend/src/components/admin/UserQuotaModal.jsx` - Modal component (ใหม่)
- ✅ `frontend/src/components/admin/UserManagement.jsx` - เพิ่มปุ่มและ modal

---

## 🚀 การใช้งาน

### 1. Restart Backend
```bash
cd gen_subtitle
./start-backend.sh
```

### 2. Restart Frontend
```bash
cd frontend
npm run dev
```

### 3. Login as Admin
- Username: admin
- Password: admin123

### 4. ไปที่ User Management Tab
- เห็นปุ่ม "Quota" ในแต่ละ user
- กดเพื่อตั้งค่า custom quota

---

## ⚠️ หมายเหตุ

### 1. Database Migration
- ถ้า database เก่าอยู่แล้ว จะต้อง add column `custom_limits`
- หรือลบ database เก่าและสร้างใหม่

### 2. Session ID Format
- ต้องเป็น `user_{username}` เพื่อให้ระบบหา custom limits ได้
- ถ้าใช้ random UUID จะไม่สามารถหา custom limits ได้

### 3. Admin Users
- Admin ไม่มีปุ่ม "Quota" (ไม่จำกัด quota)
- Admin ไม่ควรมี custom_limits

### 4. Backward Compatibility
- User เก่าที่ไม่มี custom_limits จะใช้ default อัตโนมัติ
- ไม่กระทบกับ user ที่มีอยู่แล้ว

---

## 🎉 สรุป

ตอนนี้ระบบมี feature ตั้งค่า quota แยกแต่ละ user แล้ว!

**Admin สามารถ:**
- ✅ ดู quota ของแต่ละ user
- ✅ ตั้งค่า custom quota ให้ user เฉพาะ
- ✅ ลบ custom quota (ใช้ default)
- ✅ เห็นว่า user ไหนมี custom quota

**User จะได้:**
- ✅ Quota ที่เหมาะสมกับการใช้งาน
- ✅ VIP user ได้ quota มากกว่า
- ✅ Trial user ได้ quota น้อยกว่า

**ระบบจะ:**
- ✅ ใช้ custom limits อัตโนมัติถ้ามี
- ✅ ใช้ default limits ถ้าไม่มี custom
- ✅ ตรวจสอบ quota ตาม limits ที่ถูกต้อง

Happy managing! 🚀
