import React, { useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { FileVideo, AlertCircle } from 'lucide-react'
import axios from 'axios'

const VideoUploader = ({ onVideoUploaded }) => {
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState(null)

  const onDrop = async (acceptedFiles) => {
    const file = acceptedFiles[0]
    if (!file) return

    setUploading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

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

      // MP3 conversion is already complete when we get the response
      onVideoUploaded(response.data)

    } catch (err) {
      setError(err.response?.data?.detail || 'เกิดข้อผิดพลาดในการอัปโหลด')
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
                    ? 'วางไฟル์ที่นี่...'
                    : 'ลากไฟล์มาวางที่นี่ หรือคลิกเพื่อเลือกไฟล์'}
                </p>
                <p className="text-sm">
                  รองรับ: MP4, MOV, AVI, MKV, WMV
                </p>
              </div>
            )}
            

          </div>
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-center space-x-2">
          <AlertCircle className="h-5 w-5 text-red-500" />
          <span className="text-red-700">{error}</span>
        </div>
      )}
    </div>
  )
}

export default VideoUploader