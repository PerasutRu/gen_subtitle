# คู่มือสร้าง Admin Dashboard สำหรับ React Frontend

## 📋 Overview

เอกสารนี้จะแนะนำการสร้าง Admin Dashboard สำหรับ React frontend ที่จะใช้ Admin API endpoints ที่มีอยู่ใน backend

---

## 🎯 Admin API Endpoints ที่มีอยู่

จาก backend มี Admin endpoints ดังนี้:

### 1. User Management
- `POST /admin/register` - สร้าง user ใหม่
- `GET /admin/users` - ดูรายการ user ทั้งหมด
- `DELETE /admin/user/{username}` - ลบ user

### 2. Session Management
- `GET /admin/sessions` - ดูรายการ session ทั้งหมด
- `DELETE /admin/session/{session_id}` - ลบ session เฉพาะ
- `POST /admin/reset` - Reset ลบ session ทั้งหมด

### 3. System Management
- `GET /admin/stats` - ดูสถิติการใช้งาน
- `POST /admin/reload-limits` - โหลดค่า limits ใหม่

---

## 📁 โครงสร้างไฟล์ที่ต้องสร้าง

```
frontend/src/
├── components/
│   ├── admin/
│   │   ├── AdminDashboard.jsx      # หน้าหลัก Admin
│   │   ├── UserManagement.jsx      # จัดการ users
│   │   ├── SessionManagement.jsx   # จัดการ sessions
│   │   ├── SystemStats.jsx         # สถิติระบบ
│   │   └── AdminRoute.jsx          # Protected route สำหรับ admin
│   ├── Login.jsx (แก้ไข)
│   └── ... (existing components)
├── services/
│   └── adminApi.js                 # API calls สำหรับ admin
├── App.jsx (แก้ไข)
└── main.jsx
```

---

## 🚀 ขั้นตอนการทำ

### Step 1: สร้าง Admin API Service

สร้างไฟล์ `src/services/adminApi.js`:


### Step 2: แก้ไข App.jsx เพื่อรองรับ Admin Dashboard

แก้ไขไฟล์ `src/App.jsx`:

```jsx
import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import AdminDashboard from './components/admin/AdminDashboard'
import VideoUploader from './components/VideoUploader'
// ... import components อื่นๆ

function App() {
  const [user, setUser] = useState(null)
  // ... existing state

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (token && storedUser) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setUser(JSON.parse(storedUser))
    }

    setLoading(false)
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
    // ... reset state
  }

  if (loading) {
    return <div>Loading...</div>
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  // ✨ เพิ่มส่วนนี้: ถ้าเป็น admin ให้แสดง Admin Dashboard
  if (user.role === 'admin') {
    return <AdminDashboard user={user} onLogout={handleLogout} />
  }

  // User ปกติแสดง UI เดิม
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* ... existing user UI */}
    </div>
  )
}

export default App
```

---

## 📝 สรุปไฟล์ที่สร้าง

### 1. `src/services/adminApi.js`
- API calls สำหรับ admin endpoints
- Functions: getUsers, createUser, deleteUser, getSessions, etc.

### 2. `src/components/admin/AdminRoute.jsx`
- Protected route component
- ตรวจสอบว่าเป็น admin หรือไม่

### 3. `src/components/admin/SystemStats.jsx`
- แสดงสถิติระบบ
- แสดงค่า limits
- ปุ่ม reload limits

### 4. `src/components/admin/UserManagement.jsx`
- แสดงรายการ users
- สร้าง user ใหม่
- ลบ user

### 5. `src/components/admin/SessionManagement.jsx`
- แสดงรายการ sessions
- ลบ session เฉพาะ
- Reset sessions ทั้งหมด

### 6. `src/components/admin/AdminDashboard.jsx`
- หน้าหลัก Admin Dashboard
- Tabs navigation
- รวม components ทั้งหมด

---

## 🎨 Features ที่มี

### 1. System Stats Tab
- ✅ แสดงค่า limits (maxVideos, maxDuration, maxFileSize)
- ✅ แสดงสถิติการใช้งาน (total sessions, videos, duration)
- ✅ ปุ่ม reload limits จาก config file
- ✅ ปุ่ม refresh

### 2. User Management Tab
- ✅ แสดงรายการ users ทั้งหมด
- ✅ สร้าง user ใหม่ (username, password, role)
- ✅ ลบ user
- ✅ แสดง role (admin/user) ด้วยสี
- ✅ แสดงวันที่สร้าง

### 3. Session Management Tab
- ✅ แสดงรายการ sessions ทั้งหมด
- ✅ แสดงจำนวนวิดีโอและความยาวรวม
- ✅ ลบ session เฉพาะ
- ✅ Reset sessions ทั้งหมด (มี confirmation)
- ✅ แสดงวันที่สร้าง

---

## 🚀 การติดตั้งและใช้งาน

### 1. ติดตั้ง dependencies (ถ้ายังไม่มี)
```bash
cd frontend
npm install axios lucide-react
```

### 2. ตั้งค่า environment variable
สร้างไฟล์ `.env` ใน frontend folder:
```
VITE_API_URL=http://localhost:8000
```

### 3. รัน frontend
```bash
npm run dev
```

### 4. Login ด้วย admin account
- Username: admin
- Password: (ตามที่ตั้งไว้)
- จะเห็น Admin Dashboard แทน UI ปกติ

---

## 🔒 Security Notes

### 1. Role-based Access
- ตรวจสอบ role ที่ frontend (App.jsx)
- Backend ก็ตรวจสอบด้วย `Depends(get_current_admin)`

### 2. JWT Token
- เก็บใน localStorage
- ส่งใน Authorization header ทุก request

### 3. Confirmation Dialogs
- ลบ user → confirm
- ลบ session → confirm
- Reset ทั้งหมด → confirm พร้อมคำเตือน

---

## 📊 UI/UX Features

### 1. Color Coding
- Admin role: Purple badge
- User role: Green badge
- Stats cards: Different colors for each metric

### 2. Icons
- ใช้ lucide-react icons
- Icons สำหรับแต่ละ action

### 3. Responsive Design
- Grid layout ปรับตาม screen size
- Table responsive
- Mobile-friendly

### 4. Loading States
- แสดง loading ขณะโหลดข้อมูล
- Disable buttons ขณะทำงาน

---

## 🧪 การทดสอบ

### Test Case 1: Login as Admin
1. Login ด้วย admin account
2. ควรเห็น Admin Dashboard
3. ควรเห็น 3 tabs

### Test Case 2: View System Stats
1. ไปที่ tab "สถิติระบบ"
2. ควรเห็นค่า limits
3. ควรเห็นสถิติการใช้งาน

### Test Case 3: Create User
1. ไปที่ tab "จัดการ Users"
2. กด "สร้าง User"
3. กรอกข้อมูล
4. กด "สร้าง"
5. ควรเห็น user ใหม่ในตาราง

### Test Case 4: Delete User
1. เลือก user ที่ต้องการลบ
2. กด "ลบ"
3. Confirm
4. User ควรหายจากตาราง

### Test Case 5: View Sessions
1. ไปที่ tab "จัดการ Sessions"
2. ควรเห็นรายการ sessions
3. ควรเห็นจำนวนวิดีโอและความยาว

### Test Case 6: Delete Session
1. เลือก session ที่ต้องการลบ
2. กด "ลบ"
3. Confirm
4. Session ควรหายจากตาราง

### Test Case 7: Reset All Sessions
1. กด "Reset ทั้งหมด"
2. Confirm
3. Sessions ทั้งหมดควรหายไป

### Test Case 8: Reload Limits
1. แก้ไข `backend/config/limits.json`
2. กด "โหลดใหม่" ใน System Stats
3. ค่า limits ควร update

---

## 🐛 Troubleshooting

### ปัญหา: ไม่เห็น Admin Dashboard
**วิธีแก้:**
- ตรวจสอบว่า user.role === 'admin'
- ตรวจสอบ localStorage มี user data หรือไม่
- ดู console logs

### ปัญหา: API calls ล้มเหลว
**วิธีแก้:**
- ตรวจสอบว่า backend ทำงานอยู่
- ตรวจสอบ VITE_API_URL ถูกต้อง
- ตรวจสอบ JWT token ใน localStorage
- ดู Network tab ใน DevTools

### ปัญหา: 403 Forbidden
**วิธีแก้:**
- ตรวจสอบว่า user เป็น admin จริง
- ตรวจสอบ JWT token ยังไม่หมดอายุ
- Login ใหม่

### ปัญหา: UI แสดงผิด
**วิธีแก้:**
- ตรวจสอบ Tailwind CSS ทำงานหรือไม่
- Clear browser cache
- Restart dev server

---

## 🎯 Next Steps (ถ้าต้องการพัฒนาต่อ)

### 1. เพิ่ม Features
- [ ] Search/Filter users และ sessions
- [ ] Pagination สำหรับตารางที่มีข้อมูลเยอะ
- [ ] Export data เป็น CSV
- [ ] Charts/Graphs สำหรับสถิติ
- [ ] Real-time updates (WebSocket)

### 2. ปรับปรุง UX
- [ ] Toast notifications แทน alert()
- [ ] Loading skeletons
- [ ] Error boundaries
- [ ] Form validation ที่ดีขึ้น

### 3. เพิ่ม Admin Features
- [ ] Edit user (เปลี่ยน password, role)
- [ ] View user activity logs
- [ ] System health monitoring
- [ ] Backup/Restore database

### 4. Security Enhancements
- [ ] Two-factor authentication
- [ ] Audit logs
- [ ] Rate limiting
- [ ] IP whitelist

---

## 📚 เอกสารอ้างอิง

### Backend API Docs
- ดูที่ `backend/main.py` สำหรับ admin endpoints
- Swagger UI: http://localhost:8000/docs

### Frontend Libraries
- React: https://react.dev
- Axios: https://axios-http.com
- Lucide Icons: https://lucide.dev
- Tailwind CSS: https://tailwindcss.com

---

## ✅ Checklist

### Setup
- [x] สร้าง adminApi.js
- [x] สร้าง AdminRoute.jsx
- [x] สร้าง SystemStats.jsx
- [x] สร้าง UserManagement.jsx
- [x] สร้าง SessionManagement.jsx
- [x] สร้าง AdminDashboard.jsx
- [ ] แก้ไข App.jsx
- [ ] ทดสอบทุก features

### Testing
- [ ] Login as admin
- [ ] View system stats
- [ ] Create user
- [ ] Delete user
- [ ] View sessions
- [ ] Delete session
- [ ] Reset all sessions
- [ ] Reload limits

---

## 💡 Tips

1. **ใช้ React DevTools** เพื่อ debug state และ props
2. **ใช้ Network tab** เพื่อดู API calls
3. **ใช้ Console logs** เพื่อ debug
4. **Test บน different browsers** เพื่อความมั่นใจ
5. **Backup database** ก่อนทดสอบ delete/reset functions

---

## 🎉 สรุป

ตอนนี้คุณมี Admin Dashboard ที่สมบูรณ์แล้ว! สามารถ:
- ✅ จัดการ users (สร้าง, ลบ)
- ✅ จัดการ sessions (ดู, ลบ, reset)
- ✅ ดูสถิติระบบ
- ✅ Reload limits จาก config

Happy coding! 🚀
