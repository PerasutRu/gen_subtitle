import React, { useState } from 'react'
import { Download, Video, Loader, AlertCircle, CheckCircle } from 'lucide-react'
import axios from 'axios'

const VideoEmbedder = ({ fileData, availableLanguages }) => {
  const [embedding, setEmbedding] = useState({})
  const [embedded, setEmbedded] = useState({})
  const [error, setError] = useState(null)
  const [progress, setProgress] = useState({})
  const [showSpeedSettings, setShowSpeedSettings] = useState(false)
  const [showFontSettings, setShowFontSettings] = useState(false)
  const [speedPreset, setSpeedPreset] = useState('balanced')
  
  // Font settings state
  const [fontSettings, setFontSettings] = useState({
    font_name: 'TH Sarabun New',
    font_size: 20,
    bold: true,
    outline: 1.5,
    shadow: 1.0,
    font_color: 'white',
    outline_color: 'black'
  })

  const resetEmbedding = (language, type = 'hard') => {
    const key = `${language}_${type}`
    setEmbedded(prev => {
      const newEmbedded = { ...prev }
      delete newEmbedded[key]
      return newEmbedded
    })
    setError(null)
  }

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

      const requestData = {
        file_id: fileData.file_id,
        language: language,
        type: type
      }

      // Add speed preset and font settings for hard subtitles
      if (type === 'hard') {
        requestData.speed_preset = speedPreset
        requestData.font_name = fontSettings.font_name
        requestData.font_size = fontSettings.font_size
        requestData.bold = fontSettings.bold
        requestData.outline = fontSettings.outline
        requestData.shadow = fontSettings.shadow
        requestData.font_color = fontSettings.font_color
        requestData.outline_color = fontSettings.outline_color
      }

      console.log('Sending embed request:', requestData)
      
      const response = await axios.post('/api/embed-subtitles', requestData, {
        timeout: 600000, // 10 minute timeout
        onUploadProgress: (progressEvent) => {
          console.log('Upload progress:', progressEvent)
        }
      })

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setEmbedded(prev => ({ ...prev, [key]: response.data }))
      
      console.log('Embed successful:', response.data)
    } catch (err) {
      console.error('Embed error:', err)
      clearInterval(progressInterval)
      
      let errorMessage = `เกิดข้อผิดพลาดในการฝัง ${type} subtitle ${language}`
      
      if (err.code === 'ECONNABORTED') {
        errorMessage = 'การฝัง subtitle ใช้เวลานานเกินไป กรุณาลองใหม่อีกครั้ง'
      } else if (err.response?.data?.detail) {
        errorMessage = err.response.data.detail
      } else if (err.message) {
        errorMessage += `: ${err.message}`
      }
      
      setError(errorMessage)
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
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-3">
            <Video className="h-6 w-6 text-primary-600" />
            <h3 className="text-xl font-semibold">ฝัง Subtitle เข้ากับวิดีโอ</h3>
          </div>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowSpeedSettings(!showSpeedSettings)}
              className="btn-secondary text-sm"
            >
              {showSpeedSettings ? '⚡ ซ่อนความเร็ว' : '⚡ ความเร็ว'}
            </button>
            <button
              onClick={() => setShowFontSettings(!showFontSettings)}
              className="btn-secondary text-sm"
            >
              {showFontSettings ? '🎨 ซ่อนฟอนต์' : '🎨 ฟอนต์'}
            </button>
          </div>
        </div>
        <p className="text-gray-600">
          เลือกภาษาที่ต้องการฝัง subtitle เข้ากับวิดีโอต้นฉบับ และปรับแต่งฟอนต์ตามต้องการ
        </p>
      </div>

      {/* Font Settings Panel */}
      {showFontSettings && (
        <div className="card bg-gradient-to-br from-purple-50 to-pink-50 border-purple-200">
          <h4 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <span>🎨</span>
            <span>การตั้งค่าฟอนต์สำหรับ Hard Subtitle</span>
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Font Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ฟอนต์ (รองรับภาษาไทย)
              </label>
              <select
                value={fontSettings.font_name}
                onChange={(e) => setFontSettings({...fontSettings, font_name: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="TH Sarabun New">TH Sarabun New (แนะนำ - ฟอนต์ไทยสวย)</option>
                <option value="Tahoma">Tahoma (วรรณยุกต์ไม่โดด)</option>
                <option value="Arial">Arial</option>
                <option value="Helvetica">Helvetica</option>
                <option value="DejaVu Sans">DejaVu Sans</option>
                <option value="Verdana">Verdana</option>
              </select>
            </div>

            {/* Font Size */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ขนาดฟอนต์: {fontSettings.font_size}
              </label>
              <input
                type="range"
                min="14"
                max="32"
                value={fontSettings.font_size}
                onChange={(e) => setFontSettings({...fontSettings, font_size: parseInt(e.target.value)})}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>เล็ก (14)</span>
                <span>กลาง (20)</span>
                <span>ใหญ่ (32)</span>
              </div>
            </div>

            {/* Font Color */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                สีตัวอักษร
              </label>
              <select
                value={fontSettings.font_color}
                onChange={(e) => setFontSettings({...fontSettings, font_color: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="white">⚪ ขาว (White)</option>
                <option value="yellow">🟡 เหลือง (Yellow)</option>
                <option value="cyan">🔵 ฟ้า (Cyan)</option>
                <option value="green">🟢 เขียว (Green)</option>
                <option value="red">🔴 แดง (Red)</option>
                <option value="magenta">🟣 ม่วง (Magenta)</option>
              </select>
            </div>

            {/* Outline Color */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                สีขอบ
              </label>
              <select
                value={fontSettings.outline_color}
                onChange={(e) => setFontSettings({...fontSettings, outline_color: e.target.value})}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="black">⚫ ดำ (Black)</option>
                <option value="white">⚪ ขาว (White)</option>
              </select>
            </div>

            {/* Outline Width */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ความหนาของขอบ: {fontSettings.outline.toFixed(1)}
              </label>
              <input
                type="range"
                min="0.5"
                max="4"
                step="0.5"
                value={fontSettings.outline}
                onChange={(e) => setFontSettings({...fontSettings, outline: parseFloat(e.target.value)})}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>บาง (0.5)</span>
                <span>กลาง (1.5)</span>
                <span>หนา (4.0)</span>
              </div>
            </div>

            {/* Shadow */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ความเข้มของเงา: {fontSettings.shadow.toFixed(1)}
              </label>
              <input
                type="range"
                min="0"
                max="3"
                step="0.5"
                value={fontSettings.shadow}
                onChange={(e) => setFontSettings({...fontSettings, shadow: parseFloat(e.target.value)})}
                className="w-full"
              />
              <div className="flex justify-between text-xs text-gray-500 mt-1">
                <span>ไม่มี (0)</span>
                <span>กลาง (1.0)</span>
                <span>เข้ม (3.0)</span>
              </div>
            </div>

            {/* Bold */}
            <div className="md:col-span-2">
              <label className="flex items-center space-x-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={fontSettings.bold}
                  onChange={(e) => setFontSettings({...fontSettings, bold: e.target.checked})}
                  className="w-5 h-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                />
                <span className="text-sm font-medium text-gray-700">ตัวหนา (Bold)</span>
              </label>
            </div>
          </div>

          {/* Preview */}
          <div className="mt-4 p-4 bg-gray-800 rounded-lg">
            <p className="text-center" style={{
              fontFamily: fontSettings.font_name,
              fontSize: `${fontSettings.font_size}px`,
              fontWeight: fontSettings.bold ? 'bold' : 'normal',
              color: fontSettings.font_color,
              textShadow: `
                -${fontSettings.outline}px -${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.outline}px -${fontSettings.outline}px 0 ${fontSettings.outline_color},
                -${fontSettings.outline}px ${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.outline}px ${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.shadow}px ${fontSettings.shadow}px ${fontSettings.shadow * 2}px rgba(0,0,0,0.8)
              `
            }}>
              ตัวอย่างฟอนต์ภาษาไทย ก ข ค ง ไม้เอก ไม้โท
            </p>
            <p className="text-center mt-2" style={{
              fontFamily: fontSettings.font_name,
              fontSize: `${fontSettings.font_size}px`,
              fontWeight: fontSettings.bold ? 'bold' : 'normal',
              color: fontSettings.font_color,
              textShadow: `
                -${fontSettings.outline}px -${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.outline}px -${fontSettings.outline}px 0 ${fontSettings.outline_color},
                -${fontSettings.outline}px ${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.outline}px ${fontSettings.outline}px 0 ${fontSettings.outline_color},
                ${fontSettings.shadow}px ${fontSettings.shadow}px ${fontSettings.shadow * 2}px rgba(0,0,0,0.8)
              `
            }}>
              Font Preview - English ABC 123
            </p>
          </div>

          {/* Reset Button */}
          <div className="mt-4 flex justify-end">
            <button
              onClick={() => setFontSettings({
                font_name: 'TH Sarabun New',
                font_size: 20,
                bold: true,
                outline: 1.5,
                shadow: 1.0,
                font_color: 'white',
                outline_color: 'black'
              })}
              className="btn-secondary text-sm"
            >
              รีเซ็ตเป็นค่าเริ่มต้น
            </button>
          </div>
        </div>
      )}

      {/* Speed Settings Panel */}
      {showSpeedSettings && (
        <div className="card bg-gradient-to-br from-blue-50 to-cyan-50 border-blue-200">
          <h4 className="font-semibold text-gray-900 mb-4 flex items-center space-x-2">
            <span>⚡</span>
            <span>การตั้งค่าความเร็วสำหรับ Hard Subtitle</span>
          </h4>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Fast */}
            <button
              onClick={() => setSpeedPreset('fast')}
              className={`p-4 rounded-lg border-2 transition-all ${
                speedPreset === 'fast'
                  ? 'border-blue-500 bg-blue-50 shadow-md'
                  : 'border-gray-300 hover:border-blue-300'
              }`}
            >
              <div className="text-center">
                <div className="text-3xl mb-2">🚀</div>
                <h5 className="font-semibold text-gray-900 mb-1">เร็วที่สุด</h5>
                <p className="text-xs text-gray-600 mb-2">Fast</p>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>⚡ เร็วมาก</p>
                  <p>📊 คุณภาพปานกลาง</p>
                  <p>⏱️ ~30 วินาที/นาที</p>
                </div>
              </div>
            </button>

            {/* Balanced */}
            <button
              onClick={() => setSpeedPreset('balanced')}
              className={`p-4 rounded-lg border-2 transition-all ${
                speedPreset === 'balanced'
                  ? 'border-green-500 bg-green-50 shadow-md'
                  : 'border-gray-300 hover:border-green-300'
              }`}
            >
              <div className="text-center">
                <div className="text-3xl mb-2">⚖️</div>
                <h5 className="font-semibold text-gray-900 mb-1">สมดุล</h5>
                <p className="text-xs text-gray-600 mb-2">Balanced (แนะนำ)</p>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>⚡ เร็ว</p>
                  <p>📊 คุณภาพดี</p>
                  <p>⏱️ ~45 วินาที/นาที</p>
                </div>
              </div>
            </button>

            {/* Quality */}
            <button
              onClick={() => setSpeedPreset('quality')}
              className={`p-4 rounded-lg border-2 transition-all ${
                speedPreset === 'quality'
                  ? 'border-purple-500 bg-purple-50 shadow-md'
                  : 'border-gray-300 hover:border-purple-300'
              }`}
            >
              <div className="text-center">
                <div className="text-3xl mb-2">💎</div>
                <h5 className="font-semibold text-gray-900 mb-1">คุณภาพสูง</h5>
                <p className="text-xs text-gray-600 mb-2">Quality</p>
                <div className="text-sm text-gray-700 space-y-1">
                  <p>⚡ ปานกลาง</p>
                  <p>📊 คุณภาพสูงสุด</p>
                  <p>⏱️ ~90 วินาที/นาที</p>
                </div>
              </div>
            </button>
          </div>

          {/* Info */}
          <div className="mt-4 p-3 bg-white rounded-lg border border-blue-200">
            <p className="text-sm text-gray-700">
              <strong>ความเร็วที่เลือก:</strong> {
                speedPreset === 'fast' ? '🚀 เร็วที่สุด - เหมาะกับการทดสอบหรือต้องการความเร็ว' :
                speedPreset === 'balanced' ? '⚖️ สมดุล - แนะนำสำหรับการใช้งานทั่วไป' :
                '💎 คุณภาพสูง - เหมาะกับงานที่ต้องการคุณภาพสูงสุด'
              }
            </p>
          </div>
        </div>
      )}

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
                <h5 className="text-sm font-medium text-gray-700 mb-2">Hard Subtitle (ฝังลงในวิดีโอ)</h5>
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
                    <>
                      <button
                        onClick={() => downloadEmbeddedVideo(language.code, 'hard')}
                        className="btn-secondary flex items-center justify-center space-x-2 text-sm"
                      >
                        <Download className="h-4 w-4" />
                        <span>ดาวน์โหลด Hard</span>
                      </button>
                      <button
                        onClick={() => resetEmbedding(language.code, 'hard')}
                        className="btn-secondary flex items-center justify-center space-x-2 text-sm bg-orange-50 hover:bg-orange-100 text-orange-700 border-orange-300"
                      >
                        <Video className="h-4 w-4" />
                        <span>ฝังใหม่</span>
                      </button>
                    </>
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
          <p>• <strong>Hard Subtitle:</strong> เผา subtitle ลงในวิดีโอ ไม่สามารถปิดได้ (ใช้ default style เหมือน soft)</p>
          <p>• <strong>Soft Subtitle:</strong> ฝัง subtitle เป็นไฟล์แยก สามารถเปิด/ปิดได้</p>
          <p>• <strong>⚡ ความเร็ว:</strong> เลือกได้ 3 แบบ - เร็วที่สุด, สมดุล (แนะนำ), คุณภาพสูง</p>
          <p>• <strong>⏱️ เวลา:</strong> ขึ้นอยู่กับความเร็วที่เลือก (30-90 วินาที/นาที)</p>
          <p>• <strong>🎨 ฟอนต์:</strong> ปรับแต่งได้ - ฟอนต์, ขนาด, สี, ขอบ, เงา (default: TH Sarabun New 20px)</p>
          <p>• <strong>✨ คุณภาพ:</strong> ปรับได้ตามความเร็วที่เลือก</p>
          <p>• <strong>🇹🇭 ภาษาไทย:</strong> ใช้ TH Sarabun New หรือ Tahoma เพื่อให้วรรณยุกต์ไม่โดด</p>
        </div>
      </div>
    </div>
  )
}

export default VideoEmbedder