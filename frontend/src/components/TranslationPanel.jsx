import { useState } from 'react'
import { Download, Languages, AlertCircle, Loader, CheckCircle2 } from 'lucide-react'
import axios from 'axios'
import VideoEmbedder from './VideoEmbedder'

const TranslationPanel = ({ fileData }) => {
  const [translations, setTranslations] = useState({})
  const [translating, setTranslating] = useState({})
  const [stylePrompts, setStylePrompts] = useState({})
  const [error, setError] = useState(null)
  const [selectedLanguages, setSelectedLanguages] = useState([])

  const languages = [
    { code: 'english', name: 'อังกฤษ', flag: '🇺🇸' },
    { code: 'lao', name: 'ลาว', flag: '🇱🇦' },
    { code: 'myanmar', name: 'พม่า', flag: '🇲🇲' },
    { code: 'khmer', name: 'กัมพูชา', flag: '🇰🇭' },
    { code: 'vietnamese', name: 'เวียดนาม', flag: '🇻🇳' }
  ]

  const toggleLanguageSelection = (languageCode) => {
    setSelectedLanguages(prev => {
      if (prev.includes(languageCode)) {
        return prev.filter(code => code !== languageCode)
      } else {
        return [...prev, languageCode]
      }
    })
  }

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
          เลือกภาษาที่ต้องการแปล แล้วกดปุ่มแปลเพื่อเริ่มการแปลทีละภาษา
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

      {/* Language Selection Grid */}
      <div className="card">
        <h4 className="font-semibold text-gray-900 mb-4">เลือกภาษาที่ต้องการแปล</h4>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-3">
          {languages.map((language) => {
            const isSelected = selectedLanguages.includes(language.code)
            const hasTranslation = translations[language.code]
            const isTranslating = translating[language.code]

            return (
              <button
                key={language.code}
                onClick={() => !hasTranslation && !isTranslating && toggleLanguageSelection(language.code)}
                disabled={hasTranslation || isTranslating}
                className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                  hasTranslation
                    ? 'border-green-500 bg-green-50 cursor-default'
                    : isSelected
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-300 hover:border-primary-300 hover:bg-gray-50'
                } ${(hasTranslation || isTranslating) ? 'cursor-not-allowed' : 'cursor-pointer'}`}
              >
                <div className="flex flex-col items-center space-y-2">
                  <span className="text-3xl">{language.flag}</span>
                  <span className="text-sm font-medium text-gray-900">{language.name}</span>
                  {hasTranslation && (
                    <CheckCircle2 className="h-5 w-5 text-green-600" />
                  )}
                  {isTranslating && (
                    <Loader className="h-5 w-5 text-primary-600 animate-spin" />
                  )}
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Selected Languages Detail */}
      {selectedLanguages.length > 0 && (
        <div className="space-y-4">
          {selectedLanguages.map((languageCode) => {
            const language = languages.find(l => l.code === languageCode)
            const isTranslating = translating[languageCode]
            const hasTranslation = translations[languageCode]

            return (
              <div key={languageCode} className="card">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <span className="text-2xl">{language.flag}</span>
                    <h4 className="text-lg font-semibold">{language.name}</h4>
                  </div>
                  {hasTranslation && (
                    <div className="flex items-center space-x-2 text-green-600">
                      <CheckCircle2 className="h-5 w-5" />
                      <span className="text-sm font-medium">แปลเสร็จสิ้น</span>
                    </div>
                  )}
                </div>

                {/* Style Prompt */}
                <div className="mb-4">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Style การแปล (ไม่บังคับ)
                  </label>
                  <textarea
                    value={stylePrompts[languageCode] || ''}
                    onChange={(e) => handleStylePromptChange(languageCode, e.target.value)}
                    placeholder="เช่น: แปลให้เป็นทางการ, ใช้คำง่ายๆ, แปลแบบสบายๆ"
                    className="w-full p-3 border border-gray-300 rounded-lg text-sm resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    rows="2"
                    disabled={isTranslating || hasTranslation}
                  />
                </div>

                {/* Action Buttons */}
                <div className="flex flex-wrap gap-3">
                  {!hasTranslation && (
                    <button
                      onClick={() => translateToLanguage(languageCode)}
                      disabled={isTranslating}
                      className={`btn-primary flex items-center space-x-2 ${
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
                  )}

                  {hasTranslation && (
                    <button
                      onClick={() => downloadTranslatedSrt(languageCode)}
                      className="btn-secondary flex items-center space-x-2"
                    >
                      <Download className="h-4 w-4" />
                      <span>ดาวน์โหลด SRT</span>
                    </button>
                  )}
                </div>
              </div>
            )
          })}
        </div>
      )}

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