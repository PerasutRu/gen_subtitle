import React, { useState, useEffect } from 'react'
import axios from 'axios'
import Login from './components/Login'
import VideoUploader from './components/VideoUploader'
import TranscriptionEditor from './components/TranscriptionEditor'
import SubtitleEditor from './components/SubtitleEditor'
import TranslationPanel from './components/TranslationPanel'
import ProgressTracker from './components/ProgressTracker'
import { FileVideo, FileText, Edit3, Languages, LogOut } from 'lucide-react'

function App() {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [currentStep, setCurrentStep] = useState(1)
  const [fileData, setFileData] = useState(null)
  const [transcriptionData, setTranscriptionData] = useState(null)
  const [editedTranscriptionData, setEditedTranscriptionData] = useState(null)

  const steps = [
    { id: 1, title: 'อัปโหลดวิดีโอ', icon: FileVideo, completed: false },
    { id: 2, title: 'แกะเสียง', icon: FileText, completed: false },
    { id: 3, title: 'แก้ไข Subtitle', icon: Edit3, completed: false },
    { id: 4, title: 'แปลภาษา', icon: Languages, completed: false }
  ]

  const handleVideoUploaded = (data) => {
    setFileData(data)
    setCurrentStep(2) // ไป step 2 (แกะเสียง)
  }

  const handleTranscriptionComplete = (data) => {
    setTranscriptionData(data)
    setCurrentStep(3) // ไป step 3 (แก้ไข subtitle)
  }

  const handleEditComplete = (data) => {
    setEditedTranscriptionData(data)
    setCurrentStep(4) // ไป step 4 (แปลภาษา)
  }

  // Check authentication on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token')
    const storedUser = localStorage.getItem('user')

    if (token && storedUser) {
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      setUser(JSON.parse(storedUser))
    }

    setLoading(false)
  }, [])

  const handleLoginSuccess = (userData) => {
    setUser(userData)
  }

  const handleLogout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user')
    delete axios.defaults.headers.common['Authorization']
    setUser(null)
    setCurrentStep(1)
    setFileData(null)
    setTranscriptionData(null)
    setEditedTranscriptionData(null)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    )
  }

  if (!user) {
    return <Login onLoginSuccess={handleLoginSuccess} />
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className="flex-1"></div>
            <h1 className="text-4xl font-bold text-gray-900 flex-1">
              Video Subtitle Generator
            </h1>
            <div className="flex-1 flex justify-end items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">ยินดีต้อนรับ</p>
                <p className="font-semibold text-gray-900">{user.username}</p>
              </div>
              <button
                onClick={handleLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>ออกจากระบบ</span>
              </button>
            </div>
          </div>
          <p className="text-lg text-gray-600">
            แปลงวิดีโอเป็นซับไตเติ้ลหลายภาษาด้วย AI
          </p>
        </div>

        {/* Progress Tracker */}
        <ProgressTracker steps={steps} currentStep={currentStep} />

        {/* Main Content */}
        <div className="max-w-4xl mx-auto">
          {currentStep === 1 && (
            <VideoUploader onVideoUploaded={handleVideoUploaded} />
          )}

          {currentStep === 2 && fileData && (
            <TranscriptionEditor 
              fileData={fileData}
              onTranscriptionComplete={handleTranscriptionComplete}
            />
          )}

          {currentStep === 3 && transcriptionData && (
            <SubtitleEditor 
              fileData={fileData}
              transcriptionData={transcriptionData}
              onEditComplete={handleEditComplete}
            />
          )}

          {currentStep === 4 && editedTranscriptionData && (
            <TranslationPanel 
              fileData={fileData}
              transcriptionData={editedTranscriptionData}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default App