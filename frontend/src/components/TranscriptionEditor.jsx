import React, { useState, useEffect } from 'react'
import { Download, Edit3, AlertCircle } from 'lucide-react'
import axios from 'axios'

const TranscriptionEditor = ({ fileData, onTranscriptionComplete }) => {
  const [transcribing, setTranscribing] = useState(false)
  const [transcription, setTranscription] = useState(null)
  const [error, setError] = useState(null)
  const provider = 'botnoi' // Default to Botnoi

  useEffect(() => {
    startTranscription()
  }, [])

  const startTranscription = async () => {
    setTranscribing(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('provider', provider)
      
      const response = await axios.post(`/api/transcribe/${fileData.file_id}`, formData)
      setTranscription(response.data)
      onTranscriptionComplete(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'เกิดข้อผิดพลาดในการแกะเสียง')
    } finally {
      setTranscribing(false)
    }
  }

  const downloadMp3 = () => {
    window.open(`/api/download-mp3/${fileData.file_id}`, '_blank')
  }

  const downloadSrt = () => {
    window.open(`/api/download-srt/${fileData.file_id}/original`, '_blank')
  }

  const handleContinue = () => {
    // Just pass the data to next step
    onTranscriptionComplete(transcription)
  }

  if (transcribing) {
    return (
      <div className="card text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto mb-4"></div>
        <h3 className="text-xl font-semibold mb-2">กำลังแกะเสียง...</h3>
        <p className="text-gray-600">กรุณารอสักครู่ ขั้นตอนนี้อาจใช้เวลาหลายนาที</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="card">
        <div className="flex items-center space-x-2 text-red-700 mb-4">
          <AlertCircle className="h-5 w-5" />
          <span className="font-semibold">เกิดข้อผิดพลาด</span>
        </div>
        <p className="text-red-600 mb-4">{error}</p>
        <button
          onClick={startTranscription}
          className="btn-primary"
        >
          ลองใหม่
        </button>
      </div>
    )
  }

  if (!transcription) return null

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">ผลการแกะเสียง</h3>
        <p className="text-gray-600">
          ระบบได้แกะเสียงจากวิดีโอเรียบร้อยแล้ว คุณสามารถดาวน์โหลดไฟล์หรือดำเนินการต่อเพื่อแก้ไข subtitle
        </p>
      </div>

      {/* Download Section */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">ดาวน์โหลดไฟล์</h3>
        <div className="flex flex-wrap gap-4">
          <button
            onClick={downloadMp3}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>ดาวน์โหลด MP3</span>
          </button>
          <button
            onClick={downloadSrt}
            className="btn-secondary flex items-center space-x-2"
          >
            <Download className="h-4 w-4" />
            <span>ดาวน์โหลด SRT (ต้นฉบับ)</span>
          </button>
        </div>
      </div>

      {/* Transcription Preview */}
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">ตัวอย่างข้อความที่แกะได้</h3>
        
        <div className="bg-gray-50 p-4 rounded-lg mb-4 max-h-64 overflow-y-auto">
          <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">
            {transcription.transcription.text}
          </p>
        </div>

        {/* Segments Preview */}
        <div className="mt-4">
          <h4 className="font-semibold mb-3 text-sm text-gray-700">
            ตัวอย่าง Segments พร้อม Timestamp ({transcription.transcription.segments.length} รายการ)
          </h4>
          <div className="max-h-64 overflow-y-auto space-y-2">
            {transcription.transcription.segments.slice(0, 5).map((segment, index) => (
              <div key={index} className="bg-white p-3 rounded border text-sm">
                <div className="text-gray-500 text-xs mb-1">
                  {Math.floor(segment.start / 60)}:{String(Math.floor(segment.start % 60)).padStart(2, '0')} - {Math.floor(segment.end / 60)}:{String(Math.floor(segment.end % 60)).padStart(2, '0')}
                </div>
                <div className="text-gray-800">{segment.text}</div>
              </div>
            ))}
            {transcription.transcription.segments.length > 5 && (
              <div className="text-center text-gray-500 text-sm">
                และอีก {transcription.transcription.segments.length - 5} segments...
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Continue Button */}
      <div className="card bg-primary-50 border-primary-200">
        <div className="flex items-center justify-between">
          <div>
            <h4 className="font-semibold text-primary-900 mb-1">พร้อมแก้ไข Subtitle แล้วหรือยัง?</h4>
            <p className="text-primary-700 text-sm">
              ขั้นตอนถัดไปคุณจะสามารถแก้ไข subtitle แต่ละรายการพร้อมดูวิดีโอประกอบ
            </p>
          </div>
          <button
            onClick={handleContinue}
            className="btn-primary flex items-center space-x-2"
          >
            <Edit3 className="h-4 w-4" />
            <span>ดำเนินการต่อ</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default TranscriptionEditor