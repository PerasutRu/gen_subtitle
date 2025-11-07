import React, { useState, useEffect } from 'react'
import { Download, Play, Edit3, Save, AlertCircle } from 'lucide-react'
import axios from 'axios'

const TranscriptionEditor = ({ fileData, onTranscriptionComplete }) => {
  const [transcribing, setTranscribing] = useState(false)
  const [transcription, setTranscription] = useState(null)
  const [editableText, setEditableText] = useState('')
  const [isEditing, setIsEditing] = useState(false)
  const [error, setError] = useState(null)

  useEffect(() => {
    startTranscription()
  }, [])

  const startTranscription = async () => {
    setTranscribing(true)
    setError(null)

    try {
      const response = await axios.post(`/api/transcribe/${fileData.file_id}`)
      setTranscription(response.data)
      setEditableText(response.data.transcription.text)
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

  const handleSaveEdit = () => {
    // Here you could implement saving the edited transcription
    setIsEditing(false)
    // Update the transcription data with edited text
    const updatedTranscription = {
      ...transcription,
      transcription: {
        ...transcription.transcription,
        text: editableText
      }
    }
    setTranscription(updatedTranscription)
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
      {/* Download Section */}
      <div className="card">
        <h3 className="text-xl font-semibold mb-4">ดาวน์โหลดไฟล์</h3>
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

      {/* Transcription Editor */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-semibold">ผลการแกะเสียง</h3>
          <div className="flex space-x-2">
            {isEditing ? (
              <button
                onClick={handleSaveEdit}
                className="btn-primary flex items-center space-x-2"
              >
                <Save className="h-4 w-4" />
                <span>บันทึก</span>
              </button>
            ) : (
              <button
                onClick={() => setIsEditing(true)}
                className="btn-secondary flex items-center space-x-2"
              >
                <Edit3 className="h-4 w-4" />
                <span>แก้ไข</span>
              </button>
            )}
          </div>
        </div>

        {isEditing ? (
          <textarea
            value={editableText}
            onChange={(e) => setEditableText(e.target.value)}
            className="w-full h-64 p-4 border border-gray-300 rounded-lg resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            placeholder="แก้ไขข้อความที่นี่..."
          />
        ) : (
          <div className="bg-gray-50 p-4 rounded-lg">
            <p className="whitespace-pre-wrap text-gray-800 leading-relaxed">
              {editableText}
            </p>
          </div>
        )}

        {/* Segments Preview */}
        <div className="mt-6">
          <h4 className="font-semibold mb-3">ตัวอย่าง Segments (พร้อม Timestamp)</h4>
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
    </div>
  )
}

export default TranscriptionEditor