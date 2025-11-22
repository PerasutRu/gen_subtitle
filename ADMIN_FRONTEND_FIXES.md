# Admin Frontend Fixes

## ปัญหาที่พบและแก้ไข

### 1. ❌ Missing Auth Token in API Calls
**ปัญหา:** adminApi.js ไม่มี axios interceptor สำหรับส่ง Authorization header
**ผลกระทบ:** API calls ทั้งหมดจะได้ 401 Unauthorized

**แก้ไข:**
```javascript
// สร้าง axios instance พร้อม interceptor
const api = axios.create({
  baseURL: API_URL
});

// เพิ่ม auth token ทุก request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

เปลี่ยนจาก `axios.get()` เป็น `api.get()` ทั้งหมด

### 2. ❌ Infinite Loop in ActivityLogs useEffect
**ปัญหา:** useEffect dependency เป็น object `filters` ทำให้ re-render ไม่หยุด
**ผลกระทบ:** Component จะ call API ซ้ำๆ ไม่หยุด

**แก้ไข:**
```javascript
// เปลี่ยนจาก
useEffect(() => {
  loadActivities();
}, [page, filters]);

// เป็น
useEffect(() => {
  loadActivities();
  // eslint-disable-next-line react-hooks/exhaustive-deps
}, [page, filters.activity_type, filters.username, filters.status, filters.date_from, filters.date_to]);
```

## ✅ สิ่งที่แก้ไขแล้ว

### Files Changed:
1. **frontend/src/services/adminApi.js**
   - ✅ เพิ่ม axios instance with auth interceptor
   - ✅ เปลี่ยน axios calls ทั้งหมดเป็น api instance
   - ✅ ใช้ relative paths แทน full URL

2. **frontend/src/components/admin/ActivityLogs.jsx**
   - ✅ แก้ useEffect dependencies เพื่อป้องกัน infinite loop
   - ✅ ใช้ individual filter properties แทน object

## 🧪 Testing

### ทดสอบว่าแก้ไขสำเร็จ:

1. **Login as Admin**
   ```
   Username: admin
   Password: admin123
   ```

2. **เช็ค Network Tab**
   - ทุก API call ควรมี `Authorization: Bearer <token>` header
   - ไม่ควรมี 401 errors

3. **เช็ค Console**
   - ไม่ควรมี infinite loop warnings
   - ไม่ควรมี repeated API calls

4. **ทดสอบแต่ละแท็บ:**
   - ✅ สถิติระบบ - โหลดข้อมูลได้
   - ✅ Activity Logs - แสดง logs พร้อม filters
   - ✅ จัดการ Users - CRUD operations
   - ✅ จัดการ Sessions - ลบ sessions ได้

## 📝 Best Practices Applied

1. **Centralized Auth** - ใช้ axios interceptor แทนการส่ง token แต่ละ call
2. **Proper Dependencies** - ใช้ primitive values ใน useEffect deps
3. **Error Handling** - มี try-catch ทุก API call
4. **Loading States** - แสดง loading indicator

## 🚀 Next Steps

หลังจากแก้ไขแล้ว:
1. Restart frontend dev server
2. Clear browser cache/localStorage
3. Login ใหม่
4. ทดสอบทุก features

---

**Status:** ✅ Fixed
**Date:** November 23, 2025
