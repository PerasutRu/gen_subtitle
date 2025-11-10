# วิธี Restart Backend เพื่อใช้ Botnoi

## ขั้นตอน

### 1. หยุด Backend ปัจจุบัน
ไปที่ terminal ที่รัน backend แล้วกด:
```
Ctrl + C
```

### 2. รัน Backend ใหม่
```bash
./start-backend.sh
```

### 3. ทดสอบ Botnoi
1. เปิด http://localhost:3000
2. อัปโหลดวิดีโอ
3. เลือก "Botnoi Gensub"
4. กดเริ่มแกะเสียง

### 4. ดู Log
ใน terminal backend จะเห็น log แบบนี้:

```
[Botnoi] Uploading file: uploads/xxx.mp3
[Botnoi] Response status: 200
[Botnoi] Response body: {...}
[Botnoi] Upload data: {...}
[Botnoi] Parsing response data keys: [...]
[Botnoi] Parsed X segments
```

## ถ้ายังมีปัญหา

### ตรวจสอบ API Key
```bash
cat .env | grep BOTNOI_API_KEY
```

### ดู Error Message
ดูใน terminal backend ว่ามี error อะไร

### ลอง OpenAI แทน
ถ้า Botnoi ยังไม่ทำงาน ให้ใช้ OpenAI ไปก่อน

## หมายเหตุ

- Log ที่เพิ่มเข้ามาจะช่วยให้เห็นว่า Botnoi API ส่ง response มาในรูปแบบอะไร
- ถ้า response format ไม่ตรง จะต้องแก้ไข code ใน `botnoi_service.py`
- อ่านรายละเอียดเพิ่มเติมใน `DEBUG_BOTNOI.md`
