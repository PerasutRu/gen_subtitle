import React, { useState, useEffect } from 'react'
import { useDropzone } from 'react-dropzone'
import { FileVideo, AlertCircle, Info } from 'lucide-react'
import axios from 'axios'

const VideoUploader = ({ onVideoUploaded }) => {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)
  const [limits, setLimits] = useState(null)
  const [usage, setUsage] = useState(null)
  const [sessionId, setSessionId] = useState(null)

  // Load limits on mount
  useEffect(() => {
    const loadLimits = async () => {
      try {
        const response = await axios.get('/api/limits')
        setLimits(response.data)
      } catch (err) {
        console.error('Failed to load limits:', err)
      }
    }
    loadLimits()

    // Get or create session ID from sessionStorage
    let storedSessionId = sessionStorage.getItem('video_session_id')
    if (!storedSessionId) {
      storedSessionId = `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
      sessionStorage.setItem('video_session_id', storedSessionId)
    }
    setSessionId(storedSessionId)
  }, [])

  // Load usage when session ID is available
  useEffect(() => {
    if (sessionId) {
      loadUsage()
    }
  }, [sessionId])

  const loadUsage = async () => {
    if (!sessionId) return
    try {
      const response = await axios.get(`/api/session/${sessionId}/usage`)
      setUsage(response.data.usage)
    } catch (err) {
      console.error('Failed to load usage:', err)
    }
  }

  const validateFile = (file) => {
    if (!limits) return { valid: true }

    // Check file size
    const fileSizeMB = file.size / (1024 * 1024)
    if (fileSizeMB > limits.maxFileSizeMB) {
      return {
        valid: false,
        error: `ขนาดไฟล์เกิน ${limits.maxFileSizeMB} MB (ไฟล์ของคุณ: ${fileSizeMB.toFixed(2)} MB)`
      }
    }

    // Check video count
    if (usage && usage.videos_count >= limits.maxVideos) {
      return {
        valid: false,
        error: `คุณ upload ครบ ${limits.maxVideos} วิดีโอแล้ว กรุณารีเฟรชหน้าเพื่อเริ่มใหม่`
      }
    }

    return { valid: true }
  }

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    // Validate file before upload
    const validation = validateFile(file)
    if (!validation.valid) {
      setError(validation.error)
      return
    }

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)
      if (sessionId) {
        formData.append('session_id', sessionId)
      }

      // Upload video
      const response = await axios.post('/api/upload-video', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          console.log(`Upload Progress: ${percentCompleted}%`)
        },
      })

      // Update session ID if returned from server
      if (response.data.session_id) {
        setSessionId(response.data.session_id)
        sessionStorage.setItem('video_session_id', response.data.session_id)
      }

      // Update usage
      if (response.data.usage) {
        setUsage(response.data.usage)
      }

      // MP3 conversion is already complete when we get the response
      onVideoUploaded(response.data)

    } catch (err) {
      console.error('Upload error:', err)
      console.error('Error response:', err.response)
      const errorMessage = err.response?.data?.detail || err.message || 'เกิดข้อผิดพลาดในการอัปโหลด'
      console.error('Error message:', errorMessage)
      setError(errorMessage)
    } finally {
      setUploading(false)
    }
  }

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.wmv']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="card">
      {/* Quota Display */}
      {limits && usage && (
        <div className="mb-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <Info className="h-5 w-5 text-blue-500 mt-0.5" />
            <div className="flex-1">
              <h4 className="font-semibold text-blue-900 mb-2">Quota การใช้งาน</h4>
              <div className="grid grid-cols-2 gap-3 text-sm">
                <div>
                  <p className="text-blue-700">
                    จำนวนวิดีโอ: <span className="font-semibold">{usage.videos_count}/{limits.maxVideos}</span>
                  </p>
                  <div className="mt-1 w-full bg-blue-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full transition-all"
                      style={{ width: `${(usage.videos_count / limits.maxVideos) * 100}%` }}
                    ></div>
                  </div>
                </div>
                <div>
                  <p className="text-blue-700">
                    ขนาดไฟล์สูงสุด: <span className="font-semibold">{limits.maxFileSizeMB} MB</span>
                  </p>
                  <p className="text-blue-700 mt-1">
                    ความยาวสูงสุด: <span className="font-semibold">{limits.maxDurationMinutes} นาที</span>
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200 ${
          isDragActive
            ? 'border-primary-500 bg-primary-50'
            : 'border-gray-300 hover:border-primary-400'
        } ${uploading ? 'opacity-50 cursor-not-allowed' : ''}`}
      >
        <input {...getInputProps()} />
        
        <div className="flex flex-col items-center space-y-4">
          {uploading ? (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          ) : (
            <FileVideo className="h-12 w-12 text-gray-400" />
          )}
          
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {uploading ? 'กำลังอัปโหลดและแปลงเป็น MP3...' : 'อัปโหลดไฟล์วิดีโอ'}
            </h3>
            
            {!uploading && (
              <div className="text-gray-600">
                <p className="mb-1">
                  {isDragActive
                    ? 'วางไฟล์ที่นี่...'
                    : 'ลากไฟล์มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์'}
                </p>
                <p className="text-sm">
                  รองรับไฟล์วิดีโอทุกประเภท (MP4, MOV, AVI, MKV, WMV, etc.)
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <div className="flex items-start space-x-2">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-red-700 font-semibold mb-1">เกิดข้อผิดพลาด</p>
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default VideoUploader
