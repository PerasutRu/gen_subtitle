import React, { useState } from 'react'
import { Download, Languages, AlertCircle, Loader } from 'lucide-react'
import axios from 'axios'
import VideoEmbedder from './VideoEmbedder'

const TranslationPanel = ({ fileData, transcriptionData }) => {
  const [translations, setTranslations] = useState({})
  const [translating, setTranslating] = useState({})
  const [stylePrompts, setStylePrompts] = useState({})
  const [error, setError] = useState(null)

  const languages = [
    { code: 'english', name: 'อังกฤษ', flag: '🇺🇸' },
    { code: 'lao', name: 'ลาว', flag: '🇱🇦' },
    { code: 'myanmar', name: 'พม่า', flag: '🇲🇲' },
    { code: 'khmer', name: 'กัมพูชา', flag: '🇰🇭' },
    { code: 'vietnamese', name: 'เวียดนาม', flag: '🇻🇳' }
  ]

  const translateToLanguage = async (languageCode) => {
    setTranslating(prev => ({ ...prev, [languageCode]: true }))
    setError(null)

    try {
      const response = await axios.post('/api/translate', {
        file_id: fileData.file_id,
        target_language: languageCode,
        style_prompt: stylePrompts[languageCode] || null
      })

      setTranslations(prev => ({
        ...prev,
        [languageCode]: response.data
      }))
    } catch (err) {
      setError(err.response?.data?.detail || `เกิดข้อผิดพลาดในการแปลเป็น${languageCode}`)
    } finally {
      setTranslating(prev => ({ ...prev, [languageCode]: false }))
    }
  }

  const downloadTranslatedSrt = (languageCode) => {
    window.open(`/api/download-srt/${fileData.file_id}/${languageCode}`, '_blank')
  }

  const handleStylePromptChange = (languageCode, prompt) => {
    setStylePrompts(prev => ({
      ...prev,
      [languageCode]: prompt
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center space-x-3 mb-4">
          <Languages className="h-6 w-6 text-primary-600" />
          <h3 className="text-xl font-semibold">แปลซับไตเติ้ลเป็นภาษาต่างๆ</h3>
        </div>
        <p className="text-gray-600">
          เลือกภาษาที่ต้องการแปล และสามารถกำหนด style การแปลได้
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
        {languages.map((language) => {
          const isTranslating = translating[language.code]
          const hasTranslation = translations[language.code]

          return (
            <div key={language.code} className="card">
              <div className="flex items-center space-x-3 mb-4">
                <span className="text-2xl">{language.flag}</span>
                <h4 className="text-lg font-semibold">{language.name}</h4>
              </div>

              {/* Style Prompt */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Style การแปล (ไม่บังคับ)
                </label>
                <textarea
                  value={stylePrompts[language.code] || ''}
                  onChange={(e) => handleStylePromptChange(language.code, e.target.value)}
                  placeholder="เช่น: แปลให้เป็นทางการ, ใช้คำง่ายๆ, แปลแบบสบายๆ"
                  className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  rows="2"
                  disabled={isTranslating}
                />
              </div>

              {/* Action Buttons */}
              <div className="flex flex-col space-y-3">
                <button
                  onClick={() => translateToLanguage(language.code)}
                  disabled={isTranslating}
                  className={`btn-primary flex items-center justify-center space-x-2 ${
                    isTranslating ? 'opacity-50 cursor-not-allowed' : ''
                  }`}
                >
                  {isTranslating ? (
                    <>
                      <Loader className="h-4 w-4 animate-spin" />
                      <span>กำลังแปล...</span>
                    </>
                  ) : (
                    <>
                      <Languages className="h-4 w-4" />
                      <span>แปลเป็น{language.name}</span>
                    </>
                  )}
                </button>

                {hasTranslation && (
                  <button
                    onClick={() => downloadTranslatedSrt(language.code)}
                    className="btn-secondary flex items-center justify-center space-x-2"
                  >
                    <Download className="h-4 w-4" />
                    <span>ดาวน์โหลด SRT ({language.name})</span>
                  </button>
                )}
              </div>

              {/* Translation Status */}
              {hasTranslation && (
                <div className="mt-3 p-3 bg-green-50 border border-green-200 rounded-lg">
                  <div className="flex items-center space-x-2 text-green-700">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm font-medium">แปลเสร็จสิ้น</span>
                  </div>
                </div>
              )}
            </div>
          )
        })}
      </div>

      {/* Video Embedder */}
      {Object.keys(translations).length > 0 && (
        <VideoEmbedder 
          fileData={fileData}
          availableLanguages={Object.keys(translations)}
        />
      )}

      {/* Summary */}
      <div className="card bg-blue-50 border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2">สรุป</h4>
        <div className="text-blue-800 text-sm space-y-1">
          <p>• ไฟล์ต้นฉบับ: {fileData.original_filename}</p>
          <p>• ภาษาที่แปลแล้ว: {Object.keys(translations).length} ภาษา</p>
          <p>• สามารถดาวน์โหลดไฟล์ SRT ได้ทุกภาษาที่แปลเสร็จแล้ว</p>
          <p>• สามารถฝัง subtitle เข้ากับวิดีโอได้</p>
        </div>
      </div>
    </div>
  )
}

export default TranslationPanel