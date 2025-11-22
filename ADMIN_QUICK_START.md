# Admin Dashboard - Quick Start Guide

## 🚀 เริ่มต้นใช้งานเร็ว (5 นาที)

### Step 1: คัดลอกไฟล์ที่สร้างไว้แล้ว ✅

ไฟล์ทั้งหมดถูกสร้างไว้แล้วใน:
```
frontend/src/
├── services/
│   └── adminApi.js ✅
└── components/admin/
    ├── AdminDashboard.jsx ✅
    ├── AdminRoute.jsx ✅
    ├── SystemStats.jsx ✅
    ├── UserManagement.jsx ✅
    └── SessionManagement.jsx ✅
```

### Step 2: แก้ไข App.jsx

เปิดไฟล์ `frontend/src/App.jsx` และเพิ่ม:

**1. Import AdminDashboard:**
```jsx
import AdminDashboard from './components/admin/AdminDashboard'
```

**2. เพิ่มเงื่อนไขสำหรับ admin (หลังจาก `if (!user)`):**
```jsx
// ✨ เพิ่มส่วนนี้
if (user.role === 'admin') {
  return <AdminDashboard user={user} onLogout={handleLogout} />
}
```

**ตัวอย่างเต็ม:** ดูได้ที่ `frontend/src/App.ADMIN_EXAMPLE.jsx`

### Step 3: ตั้งค่า Environment Variable (ถ้ายังไม่มี)

สร้างไฟล์ `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

### Step 4: รัน Frontend

```bash
cd frontend
npm run dev
```

### Step 5: Login ด้วย Admin Account

1. เปิด browser: http://localhost:5173
2. Login ด้วย admin account
3. จะเห็น Admin Dashboard!

---

## 📸 Screenshot Features

### 1. System Stats Tab
- แสดงค่า limits (maxVideos, maxDuration, maxFileSize)
- แสดงสถิติการใช้งาน
- ปุ่ม Reload Limits

### 2. User Management Tab
- ตารางแสดง users ทั้งหมด
- ฟอร์มสร้าง user ใหม่
- ปุ่มลบ user

### 3. Session Management Tab
- ตารางแสดง sessions ทั้งหมด
- ปุ่มลบ session เฉพาะ
- ปุ่ม Reset ทั้งหมด

---

## 🧪 ทดสอบเร็ว

### Test 1: ดูสถิติ
1. Login as admin
2. ดู tab "สถิติระบบ"
3. ✅ เห็นค่า limits และสถิติ

### Test 2: สร้าง User
1. ไปที่ tab "จัดการ Users"
2. กด "สร้าง User"
3. กรอก: username, password, role
4. กด "สร้าง"
5. ✅ เห็น user ใหม่ในตาราง

### Test 3: ดู Sessions
1. ไปที่ tab "จัดการ Sessions"
2. ✅ เห็นรายการ sessions

---

## 🐛 แก้ปัญหาเร็ว

### ปัญหา: ไม่เห็น Admin Dashboard
```bash
# ตรวจสอบ user role
console.log(user.role) // ต้องเป็น 'admin'
```

### ปัญหา: API Error
```bash
# ตรวจสอบ backend ทำงานหรือไม่
curl http://localhost:8000/admin/users \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### ปัญหา: Import Error
```bash
# ตรวจสอบว่าไฟล์อยู่ที่ถูกต้อง
ls frontend/src/components/admin/
ls frontend/src/services/
```

---

## 📚 เอกสารเพิ่มเติม

- **คู่มือเต็ม:** `ADMIN_DASHBOARD_GUIDE.md`
- **Backend API:** `backend/main.py` (admin endpoints)
- **ตัวอย่าง App.jsx:** `frontend/src/App.ADMIN_EXAMPLE.jsx`

---

## ✅ Checklist

- [ ] คัดลอกไฟล์ทั้งหมดแล้ว
- [ ] แก้ไข App.jsx แล้ว
- [ ] ตั้งค่า .env แล้ว
- [ ] รัน frontend แล้ว
- [ ] Login as admin ได้
- [ ] เห็น Admin Dashboard
- [ ] ทดสอบทุก tab แล้ว

---

## 🎉 เสร็จแล้ว!

ตอนนี้คุณมี Admin Dashboard ที่พร้อมใช้งานแล้ว!

**Next:** ดูคู่มือเต็มใน `ADMIN_DASHBOARD_GUIDE.md` สำหรับ features เพิ่มเติม
