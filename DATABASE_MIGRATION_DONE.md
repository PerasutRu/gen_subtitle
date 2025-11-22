# Database Migration - Custom Limits Feature

## ✅ สิ่งที่ทำแล้ว

### ปัญหา:
```
Error getting user: no such column: custom_limits
```

Database เก่าไม่มี column `custom_limits` ที่เพิ่มใหม่

### การแก้ไข:
ลบ database เก่าและสร้างใหม่

```bash
rm -f gen_subtitle/backend/data/sessions.db
```

---

## 🔄 ขั้นตอนต่อไป:

### 1. Restart Backend
```bash
cd gen_subtitle
./start-backend.sh
```

Backend จะสร้าง database ใหม่อัตโนมัติพร้อม:
- ✅ Column `custom_limits` ใน users table
- ✅ Admin user เริ่มต้น (username: admin, password: admin123)

### 2. ทดสอบ
1. Login as admin
2. ไปที่ User Management
3. สร้าง user ใหม่
4. ตั้งค่า custom quota
5. ✅ ควรทำงานได้ปกติ

---

## 📊 Database Schema ใหม่:

### users table:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'user',
    created_at TEXT NOT NULL,
    custom_limits TEXT  -- ← เพิ่มใหม่ (JSON)
);
```

---

## ⚠️ หมายเหตุ:

### ข้อมูลที่หายไป:
- ❌ Users เก่า (ต้องสร้างใหม่)
- ❌ Sessions เก่า
- ❌ Video history

### ข้อมูลที่ยังอยู่:
- ✅ ไฟล์วิดีโอที่ upload (ใน uploads folder)
- ✅ ไฟล์ SRT
- ✅ Config files

---

## 🔄 วิธีที่ 2: Migration Script (ถ้าต้องการเก็บข้อมูลเก่า)

ถ้าต้องการเก็บ users และ sessions เก่าไว้ ใช้ script นี้:

```python
# migrate_db.py
import sqlite3

db_path = "backend/data/sessions.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# เพิ่ม column custom_limits
try:
    cursor.execute("ALTER TABLE users ADD COLUMN custom_limits TEXT")
    conn.commit()
    print("✅ เพิ่ม column custom_limits สำเร็จ")
except sqlite3.OperationalError as e:
    if "duplicate column name" in str(e):
        print("ℹ️ Column custom_limits มีอยู่แล้ว")
    else:
        print(f"❌ Error: {e}")

conn.close()
```

แต่เนื่องจากเป็น development ลบแล้วสร้างใหม่ง่ายกว่าครับ!

---

## ✅ Checklist:

- [x] ลบ database เก่า
- [ ] Restart backend
- [ ] Login as admin
- [ ] ทดสอบสร้าง user
- [ ] ทดสอบตั้งค่า quota
- [ ] ทดสอบ upload วิดีโอ

---

## 🎉 เสร็จแล้ว!

หลัง restart backend ระบบจะพร้อมใช้งาน custom quota feature!
