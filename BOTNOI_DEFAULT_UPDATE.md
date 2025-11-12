# Botnoi as Default Provider - Update

## การเปลี่ยนแปลง

ปรับ UI ให้ใช้ Botnoi เป็น provider เริ่มต้น โดยซ่อนการเลือก provider ออกจาก UI

## สิ่งที่แก้ไข

### 1. TranscriptionEditor.jsx

**เดิม:**
- แสดง UI ให้เลือกระหว่าง OpenAI และ Botnoi
- ต้องกดปุ่มเพื่อเริ่มแกะเสียง
- Default เป็น OpenAI

**ใหม่:**
- ซ่อน UI การเลือก provider
- เริ่มแกะเสียงอัตโนมัติเมื่อเข้าหน้า
- ใช้ Botnoi เป็น default

```javascript
const provider = 'botnoi' // Default to Botnoi

useEffect(() => {
  startTranscription()
}, [])
```

### 2. TranslationPanel.jsx

**เดิม:**
- แสดง radio buttons ให้เลือก provider สำหรับแต่ละภาษา
- Default เป็น OpenAI

**ใหม่:**
- ซ่อน radio buttons
- ใช้ Botnoi เป็น default สำหรับทุกภาษา

```javascript
const defaultProvider = 'botnoi' // Default to Botnoi
```

## ผลลัพธ์

### ขั้นตอนแกะเสียง (Step 2)
- ✅ ไม่มี UI เลือก provider
- ✅ เริ่มแกะเสียงอัตโนมัติด้วย Botnoi
- ✅ แสดง loading state ทันที

### ขั้นตอนแปลภาษา (Step 4)
- ✅ ไม่มี radio buttons เลือก provider
- ✅ ใช้ Botnoi สำหรับทุกภาษา
- ✅ UI สะอาดและเรียบง่ายขึ้น

## การใช้งาน

### สำหรับผู้ใช้:
1. อัปโหลดวิดีโอ
2. รอแกะเสียงอัตโนมัติ (ใช้ Botnoi)
3. แก้ไข subtitle
4. เลือกภาษาที่ต้องการแปล (ใช้ Botnoi)
5. ดาวน์โหลดไฟล์

### สำหรับ Developer:
ถ้าต้องการเปลี่ยนกลับไปใช้ OpenAI หรือให้เลือกได้:

**TranscriptionEditor.jsx:**
```javascript
// เปลี่ยนจาก
const provider = 'botnoi'

// เป็น
const provider = 'openai'
// หรือ
const [provider, setProvider] = useState('botnoi')
// และเพิ่ม UI กลับมา
```

**TranslationPanel.jsx:**
```javascript
// เปลี่ยนจาก
const defaultProvider = 'botnoi'

// เป็น
const defaultProvider = 'openai'
// หรือเพิ่ม state และ UI กลับมา
```

## ข้อดี

1. **UI สะอาดขึ้น** - ไม่มี options ที่ซับซ้อน
2. **ใช้งานง่ายขึ้น** - ไม่ต้องเลือก provider
3. **เริ่มเร็วขึ้น** - แกะเสียงอัตโนมัติทันที
4. **ประหยัดค่าใช้จ่าย** - ใช้ Botnoi ที่ถูกกว่า OpenAI

## ข้อควรระวัง

1. **ต้องมี Botnoi API Key** - ถ้าไม่มีจะ error
2. **Botnoi รองรับภาษาจำกัด** - เหมาะสำหรับภาษาไทยและอาเซียน
3. **ไม่สามารถเลือก provider** - ถ้าต้องการใช้ OpenAI ต้องแก้ไข code

## Fallback Plan

ถ้า Botnoi ไม่ทำงาน สามารถแก้ไขได้ง่ายๆ:

### วิธีที่ 1: เปลี่ยนเป็น OpenAI
```javascript
// ใน TranscriptionEditor.jsx และ TranslationPanel.jsx
const provider = 'openai' // เปลี่ยนจาก 'botnoi'
```

### วิธีที่ 2: เพิ่ม Auto Fallback
```javascript
const startTranscription = async () => {
  try {
    // Try Botnoi first
    await transcribeWithProvider('botnoi')
  } catch (error) {
    // Fallback to OpenAI
    await transcribeWithProvider('openai')
  }
}
```

## สรุป

การเปลี่ยนแปลงนี้ทำให้:
- ✅ UI เรียบง่ายขึ้น
- ✅ ใช้งานง่ายขึ้น
- ✅ ใช้ Botnoi เป็น default
- ✅ ประหยัดค่าใช้จ่าย

แต่ต้องแน่ใจว่า:
- ⚠️ มี Botnoi API Key
- ⚠️ Botnoi API ทำงานได้
- ⚠️ เนื้อหาเป็นภาษาที่ Botnoi รองรับ
