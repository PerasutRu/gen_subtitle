import React, { useState } from 'react'
import { Download, Video, Loader, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'

const VideoEmbedder = ({ fileData, availableLanguages }) => {
  const [embedding, setEmbedding] = useState({})
  const [embedded, setEmbedded] = useState({})
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState({})

  const embedSubtitles = async (language, type = 'hard') => {
    const key = `${language}_${type}`
    setEmbedding(prev => ({ ...prev, [key]: true }))
    setError(null)
    setProgress(prev => ({ ...prev, [key]: 0 }))

    try {
      // Simulate progress for user feedback
      const progressInterval = setInterval(() => {
        setProgress(prev => ({
          ...prev,
          [key]: Math.min((prev[key] || 0) + Math.random() * 15, 90)
        }))
      }, 1000)

      const response = await axios.post('/api/embed-subtitles', {
        file_id: fileData.file_id,
        language: language,
        type: type
      }, {
        timeout: 600000 // 10 minute timeout
      })

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setEmbedded(prev => ({ ...prev, [key]: response.data }))
    } catch (err) {
      setError(err.response?.data?.detail || `เกิดข้อผิดพลาดในการฝัง ${type} subtitle ${language}`)
    } finally {
      setEmbedding(prev => ({ ...prev, [key]: false }))
      setTimeout(() => {
        setProgress(prev => ({ ...prev, [key]: 0 }))
      }, 2000)
    }
  }

  const downloadEmbeddedVideo = (language, type = 'hard') => {
    window.open(`/api/download-video/${fileData.file_id}/${language}/${type}`, '_blank')
  }

  const languages = [
    { code: 'original', name: 'ไทย (ต้นฉบับ)', flag: '🇹🇭' },
    { code: 'english', name: 'อังกฤษ', flag: '🇺🇸' },
    { code: 'lao', name: 'ลาว', flag: '🇱🇦' },
    { code: 'myanmar', name: 'พม่า', flag: '🇲🇲' },
    { code: 'khmer', name: 'กัมพูชา', flag: '🇰🇭' },
    { code: 'vietnamese', name: 'เวียดนาม', flag: '🇻🇳' }
  ]

  // Filter languages that have subtitles available
  const availableLangs = languages.filter(lang => 
    lang.code === 'original' || availableLanguages.includes(lang.code)
  )

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Video className="h-6 w-6 text-primary-600" />
          <h3 className="text-xl font-semibold">ฝัง Subtitle เข้ากับวิดีโอ</h3>
        </div>
        <p className="text-gray-600">
          เลือกภาษาที่ต้องการฝัง subtitle เข้ากับวิดีโอต้นฉบับ
        </p>
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200">
          <div className="flex items-center space-x-2 text-red-700">
            <AlertCircle className="h-5 w-5" />
            <span className="font-semibold">เกิดข้อผิดพลาด</span>
          </div>
          <p className="text-red-600 mt-2">{error}</p>
        </div>
      )}

      {/* Language Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {availableLangs.map((language) => {
          const hardKey = `${language.code}_hard`
          const softKey = `${language.code}_soft`
          const isEmbeddingHard = embedding[hardKey]
          const isEmbeddingSoft = embedding[softKey]
          const hasEmbeddedHard = embedded[hardKey]
          const hasEmbeddedSoft = embedded[softKey]

          return (
            <div key={language.code} className="card">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-2xl">{language.flag}</span>
                <h4 className="text-lg font-semibold">{language.name}</h4>
              </div>

              {/* Hard Subtitle Section */}
              <div className="mb-4">
                <h5 className="text-sm font-medium text-gray-700 mb-2">Hard Subtitle (เผาลงในวิดีโอ)</h5>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => embedSubtitles(language.code, 'hard')}
                    disabled={isEmbeddingHard || hasEmbeddedHard}
                    className={`btn-primary flex items-center justify-center space-x-2 text-sm ${
                      (isEmbeddingHard || hasEmbeddedHard) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {isEmbeddingHard ? (
                      <>
                        <Loader className="h-4 w-4 animate-spin" />
                        <span>กำลังฝัง... {Math.round(progress[hardKey] || 0)}%</span>
                      </>
                    ) : hasEmbeddedHard ? (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        <span>ฝังแล้ว</span>
                      </>
                    ) : (
                      <>
                        <Video className="h-4 w-4" />
                        <span>ฝัง Hard Subtitle</span>
                      </>
                    )}
                  </button>
                  
                  {/* Progress bar for hard subtitle */}
                  {isEmbeddingHard && (
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div 
                        className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                        style={{ width: `${progress[hardKey] || 0}%` }}
                      ></div>
                    </div>
                  )}

                  {hasEmbeddedHard && (
                    <button
                      onClick={() => downloadEmbeddedVideo(language.code, 'hard')}
                      className="btn-secondary flex items-center justify-center space-x-2 text-sm"
                    >
                      <Download className="h-4 w-4" />
                      <span>ดาวน์โหลด Hard</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Soft Subtitle Section */}
              <div>
                <h5 className="text-sm font-medium text-gray-700 mb-2">Soft Subtitle (แยกเป็นไฟล์)</h5>
                <div className="flex flex-col space-y-2">
                  <button
                    onClick={() => embedSubtitles(language.code, 'soft')}
                    disabled={isEmbeddingSoft || hasEmbeddedSoft}
                    className={`btn-secondary flex items-center justify-center space-x-2 text-sm ${
                      (isEmbeddingSoft || hasEmbeddedSoft) ? 'opacity-50 cursor-not-allowed' : ''
                    }`}
                  >
                    {isEmbeddingSoft ? (
                      <>
                        <Loader className="h-4 w-4 animate-spin" />
                        <span>กำลังฝัง...</span>
                      </>
                    ) : hasEmbeddedSoft ? (
                      <>
                        <CheckCircle className="h-4 w-4" />
                        <span>ฝังแล้ว</span>
                      </>
                    ) : (
                      <>
                        <Video className="h-4 w-4" />
                        <span>ฝัง Soft Subtitle</span>
                      </>
                    )}
                  </button>

                  {hasEmbeddedSoft && (
                    <button
                      onClick={() => downloadEmbeddedVideo(language.code, 'soft')}
                      className="btn-secondary flex items-center justify-center space-x-2 text-sm"
                    >
                      <Download className="h-4 w-4" />
                      <span>ดาวน์โหลด Soft</span>
                    </button>
                  )}
                </div>
              </div>

              {/* Status */}
              {(hasEmbeddedHard || hasEmbeddedSoft) && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2 text-green-700">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium">
                      {hasEmbeddedHard && hasEmbeddedSoft ? 'ฝัง subtitle ทั้งสองแบบแล้ว' :
                       hasEmbeddedHard ? 'ฝัง hard subtitle แล้ว' :
                       'ฝัง soft subtitle แล้ว'}
                    </span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Info */}
      <div className="card bg-blue-50 border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2">ข้อมูล</h4>
        <div className="text-blue-800 text-sm space-y-1">
          <p>• <strong>Hard Subtitle:</strong> เผา subtitle ลงในวิดีโอ ไม่สามารถปิดได้</p>
          <p>• <strong>Soft Subtitle:</strong> ฝัง subtitle เป็นไฟล์แยก สามารถเปิด/ปิดได้</p>
          <p>• การฝัง subtitle ใช้เวลา 1-5 นาที ขึ้นอยู่กับความยาววิดีโอ</p>
          <p>• ใช้ ffmpeg preset ultrafast เพื่อความเร็วสูงสุด</p>
          <p>• Hard subtitle ได้รับการปรับแต่งสำหรับภาษาไทย</p>
        </div>
      </div>
    </div>
  )
}

export default VideoEmbedder