import React, { useState } from 'react'
import VideoUploader from './components/VideoUploader'
import TranscriptionEditor from './components/TranscriptionEditor'
import TranslationPanel from './components/TranslationPanel'
import ProgressTracker from './components/ProgressTracker'
import { FileVideo, FileText, Languages } from 'lucide-react'

function App() {
  const [currentStep, setCurrentStep] = useState(1)
  const [fileData, setFileData] = useState(null)
  const [transcriptionData, setTranscriptionData] = useState(null)

  const steps = [
    { id: 1, title: 'อัปโหลดวิดีโอ', icon: FileVideo, completed: false },
    { id: 2, title: 'แกะเสียง', icon: FileText, completed: false },
    { id: 3, title: 'แปลภาษา', icon: Languages, completed: false }
  ]

  const handleVideoUploaded = (data) => {
    setFileData(data)
    setCurrentStep(2) // ไป step 2 (แกะเสียง)
  }

  const handleTranscriptionComplete = (data) => {
    setTranscriptionData(data)
    setCurrentStep(3) // ไป step 3 (แปลภาษา)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Video Subtitle Generator
          </h1>
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
            <TranslationPanel 
              fileData={fileData}
              transcriptionData={transcriptionData}
            />
          )}
        </div>
      </div>
    </div>
  )
}

export default App