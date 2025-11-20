# คู่มือระบบ Authentication

## 🔐 ภาพรวม

ระบบมีการ authentication แบบ JWT (JSON Web Token) โดย:
- **User ต้อง login** ก่อนใช้งาน
- **Admin เท่านั้น** ที่สร้าง user ใหม่ได้
- Token มีอายุ 24 ชั่วโมง

---

## 👤 Default Admin Account

เมื่อรันครั้งแรก ระบบจะสร้าง admin account อัตโนมัติ:

```
Username: admin
Password: admin123
```

⚠️ **สำคัญ:** เปลี่ยน password ทันทีหลังติดตั้ง!

---

## 🚀 การใช้งาน

### 1. Login (User)

**Endpoint:** `POST /auth/login`

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "username": "admin",
    "role": "admin"
  }
}
```

### 2. ใช้ Token ในการเรียก API

เพิ่ม Header ในทุก request:
```
Authorization: Bearer <access_token>
```

**ตัวอย่าง:**
```bash
curl http://localhost:8000/limits \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### 3. ตรวจสอบข้อมูล User

**Endpoint:** `GET /auth/me`

```bash
curl http://localhost:8000/auth/me \
  -H "Authorization: Bearer <token>"
```

---

## 👨‍💼 Admin: สร้าง User ใหม่

**Endpoint:** `POST /admin/register`

```bash
curl -X POST http://localhost:8000/admin/register \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user1",
    "password": "password123",
    "role": "user"
  }'
```

**Parameters:**
- `username` - ชื่อผู้ใช้ (ต้องไม่ซ้ำ)
- `password` - รหัสผ่าน
- `role` - บทบาท: `"user"` หรือ `"admin"`

**Response:**
```json
{
  "message": "สร้าง user user1 สำเร็จ",
  "username": "user1",
  "role": "user"
}
```

---

## 📋 Admin: จัดการ Users

### ดูรายการ User ทั้งหมด

```bash
curl http://localhost:8000/admin/users \
  -H "Authorization: Bearer <admin_token>"
```

**Response:**
```json
{
  "total": 3,
  "users": [
    {
      "id": 1,
      "username": "admin",
      "role": "admin",
      "created_at": "2024-11-20T10:00:00"
    },
    {
      "id": 2,
      "username": "user1",
      "role": "user",
      "created_at": "2024-11-20T11:00:00"
    }
  ]
}
```

### ลบ User

```bash
curl -X DELETE http://localhost:8000/admin/user/user1 \
  -H "Authorization: Bearer <admin_token>"
```

---

## 🔒 Protected Endpoints

Endpoints ที่ต้อง authentication:

### User Endpoints (ต้อง login)
- `POST /upload-video` - Upload วิดีโอ
- `GET /limits` - ดู quota limits
- `GET /session/{id}/usage` - ดูการใช้งาน
- `POST /transcribe/{id}` - แกะเสียง
- `POST /translate` - แปลภาษา
- `POST /embed-subtitles` - ฝัง subtitle
- และอื่น ๆ

### Admin Endpoints (ต้องเป็น admin)
- `POST /admin/register` - สร้าง user
- `GET /admin/users` - ดูรายการ user
- `DELETE /admin/user/{username}` - ลบ user
- `GET /admin/sessions` - ดู sessions
- `GET /admin/stats` - ดูสถิติ
- `POST /admin/reset` - Reset quota
- `DELETE /admin/session/{id}` - ลบ session

---

## 🐍 Python Script ตัวอย่าง

### สร้าง User ใหม่

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login as admin
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "admin",
    "password": "admin123"
})

admin_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}

# 2. สร้าง user ใหม่
register_response = requests.post(
    f"{BASE_URL}/admin/register",
    headers=headers,
    json={
        "username": "newuser",
        "password": "password123",
        "role": "user"
    }
)

print(register_response.json())

# 3. ดูรายการ users
users_response = requests.get(f"{BASE_URL}/admin/users", headers=headers)
print(users_response.json())
```

### Upload วิดีโอ (User)

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Login
login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "username": "user1",
    "password": "password123"
})

token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Upload video
with open("video.mp4", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/upload-video",
        headers=headers,
        files=files
    )

print(response.json())
```

---

## 🔧 Configuration

### เปลี่ยน JWT Secret Key

แก้ไขใน `.env`:
```env
JWT_SECRET_KEY=your-super-secret-key-here-change-me
```

⚠️ **สำคัญ:** ใช้ secret key ที่แข็งแรงใน production!

### เปลี่ยน Token Expiration

แก้ไขใน `backend/services/auth_service.py`:
```python
self.access_token_expire_minutes = 60 * 24  # 24 hours
```

---

## 📦 Dependencies

ติดตั้ง packages เพิ่มเติม:

```bash
cd backend
source venv/bin/activate
pip install bcrypt PyJWT
```

หรือ:
```bash
pip install -r requirements.txt
```

---

## 🗄️ Database

ข้อมูล users ถูกเก็บใน SQLite:
```
backend/data/sessions.db
```

### ตาราง users

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| username | TEXT | Username (unique) |
| password_hash | TEXT | Hashed password |
| role | TEXT | "user" หรือ "admin" |
| created_at | TEXT | วันที่สร้าง |

---

## 🔐 Security Best Practices

### สำหรับ Production:

1. **เปลี่ยน default admin password**
2. **ใช้ HTTPS เท่านั้น**
3. **ตั้ง JWT_SECRET_KEY ที่แข็งแรง**
4. **เพิ่ม rate limiting**
5. **เพิ่ม password policy** (ความยาวขั้นต่ำ, ความซับซ้อน)
6. **Log การ login/logout**
7. **เพิ่ม 2FA (Two-Factor Authentication)**
8. **Backup database เป็นประจำ**

---

## ❓ Troubleshooting

### Token หมดอายุ

Error: `401 Unauthorized - Invalid or expired token`

**แก้ไข:** Login ใหม่เพื่อรับ token ใหม่

### ไม่สามารถสร้าง user ได้

Error: `403 Forbidden - Admin access required`

**แก้ไข:** ต้อง login ด้วย admin account

### Username ซ้ำ

Error: `400 Bad Request - Username already exists`

**แก้ไข:** ใช้ username อื่น

---

## 📞 Support

หากมีปัญหา ติดต่อ Admin หรือดู logs:
```bash
# ดู backend logs
tail -f backend/logs/app.log
```
