# Frontend Quota Display Fix

## ✅ ปัญหาที่แก้ไข

### 🐛 ปัญหา:
หน้า frontend ของ user แสดง quota เป็น **1/10** แทนที่จะเป็น **1/2** ตาม custom limits ที่ตั้งไว้

### 🔍 สาเหตุ:
Frontend ไม่ได้ใช้ `/user/session` endpoint ที่ return custom limits แต่ใช้ API endpoints เก่าที่ return default limits เสมอ

---

## 🔧 การแก้ไข

### 1. แก้ไข VideoUploader.jsx

#### เดิม (❌):
```javascript
// ใช้ /api/limits (ไม่มี endpoint นี้)
const response = await axios.get('/api/limits')

// ใช้ session ID แบบ random
storedSessionId = `session_${Date.now()}_${Math.random()...}`

// ไม่ได้ดึง custom limits
```

#### ใหม่ (✅):
```javascript
// ใช้ /user/session (return custom limits)
const response = await axios.get(`${VITE_API_URL}/user/session`)

// ได้ session_id จาก backend (format: user_username)
setSessionId(data.session_id)  // เช่น "user_test1"

// ได้ custom limits และ usage
setLimits(data.limits)  // custom limits ถ้ามี
setUsage(data.usage)
```

### 2. สร้าง .env file

สร้างไฟล์ `frontend/.env`:
```
VITE_API_URL=http://localhost:8000
```

### 3. เพิ่ม Console Logs

เพื่อ debug ง่ายขึ้น:
```javascript
console.log('✅ Loaded user session:', data)
console.log('   Limits:', data.limits)
console.log('   Usage:', data.usage)
```

---

## 📊 Flow การทำงานใหม่

### เดิม (❌):
```
User login
  ↓
Frontend สร้าง random session_id
  ↓
เรียก /api/limits (ไม่มี endpoint)
  ↓
ได้ default limits เสมอ (10 videos)
```

### ใหม่ (✅):
```
User login (test1)
  ↓
Frontend เรียก /user/session
  ↓
Backend ดึง custom_limits จาก database
  ↓
Return: {
  session_id: "user_test1",
  limits: {maxVideos: 2, ...},  ← custom limits
  usage: {videos_count: 1, ...}
}
  ↓
Frontend แสดง: 1/2 ไฟล์ ✅
```

---

## 🧪 การทดสอบ

### 1. Restart Frontend
```bash
cd frontend
# หยุด dev server (Ctrl+C)
npm run dev
```

### 2. Hard Refresh Browser
```
กด Ctrl+Shift+R (หรือ Cmd+Shift+R บน Mac)
```

### 3. Login as test1

### 4. ตรวจสอบ Console Logs
เปิด Browser DevTools (F12) → Console tab

ควรเห็น:
```
✅ Loaded user session: {session_id: "user_test1", ...}
   Limits: {maxVideos: 2, maxDurationMinutes: 10, maxFileSizeMB: 500}
   Usage: {videos_count: 1, ...}
```

### 5. ตรวจสอบ UI
ควรเห็น:
```
Quota การใช้งาน
จำนวนวิดีโอ: 1/2  ← ต้องเป็น 2 ไม่ใช่ 10
```

---

## 🔍 Debug Checklist

### ✅ Backend:
- [ ] Backend ทำงานอยู่ (port 8000)
- [ ] Endpoint `/user/session` return custom limits
- [ ] เห็น log "✅ Using custom limits for test1"

### ✅ Frontend:
- [ ] มีไฟล์ `.env` พร้อม `VITE_API_URL`
- [ ] Frontend restart แล้ว
- [ ] Browser hard refresh แล้ว
- [ ] Console log แสดง custom limits
- [ ] UI แสดง quota ถูกต้อง (1/2)

---

## 📝 ไฟล์ที่แก้ไข

### Frontend:
- ✅ `frontend/src/components/VideoUploader.jsx`
  - เปลี่ยนจาก `/api/limits` เป็น `/user/session`
  - ใช้ session_id จาก backend
  - เพิ่ม console logs

- ✅ `frontend/.env` (สร้างใหม่)
  - กำหนด `VITE_API_URL=http://localhost:8000`

---

## 🎯 Expected Results

### User test1 (มี custom limits):
```
Quota การใช้งาน
จำนวนวิดีโอ: 1/2 ไฟล์
ขนาดไฟล์สูงสุด: 500 MB
ความยาวสูงสุด: 10 นาที
```

### User test3 (ไม่มี custom limits):
```
Quota การใช้งาน
จำนวนวิดีโอ: 0/10 ไฟล์  ← default
ขนาดไฟล์สูงสุด: 500 MB
ความยาวสูงสุด: 10 นาที
```

---

## ⚠️ หมายเหตุ

### 1. Environment Variable
- Vite ใช้ `import.meta.env.VITE_*` ไม่ใช่ `process.env.*`
- ต้อง restart dev server หลังแก้ไข `.env`

### 2. Session ID Format
- Backend สร้าง session_id เป็น `user_{username}`
- Frontend ไม่ต้องสร้าง random session_id เอง

### 3. API Endpoints
- ใช้ `/user/session` สำหรับดึง session + limits + usage
- ใช้ `/session/{session_id}/usage` สำหรับ refresh usage
- ใช้ `/upload-video` สำหรับ upload (ไม่ใช่ `/api/upload-video`)

---

## 🎉 สรุป

**ปัญหา:** Frontend ไม่ได้ดึง custom limits จาก backend

**วิธีแก้:** เปลี่ยนจาก `/api/limits` เป็น `/user/session`

**ผลลัพธ์:** Frontend แสดง quota ตาม custom limits ที่ตั้งไว้

**ตอนนี้ระบบควรทำงานได้ถูกต้องแล้ว!** 🚀
