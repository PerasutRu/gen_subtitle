import React, { useState, useEffect, useRef } from 'react'
import { Save, Play, Pause, SkipBack, SkipForward, Edit3, Check, X, AlertCircle } from 'lucide-react'
import axios from 'axios'

const SubtitleEditor = ({ fileData, transcriptionData, onEditComplete }) => {
  const [segments, setSegments] = useState([])
  const [editingIndex, setEditingIndex] = useState(null)
  const [editText, setEditText] = useState('')
  const [currentTime, setCurrentTime] = useState(0)
  const [isPlaying, setIsPlaying] = useState(false)
  const [activeSegmentIndex, setActiveSegmentIndex] = useState(-1)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  
  const videoRef = useRef(null)
  const segmentRefs = useRef([])

  useEffect(() => {
    if (transcriptionData?.transcription?.segments) {
      setSegments(transcriptionData.transcription.segments)
    }
  }, [transcriptionData])

  useEffect(() => {
    // Update active segment based on current time
    const activeIndex = segments.findIndex(
      seg => currentTime >= seg.start && currentTime <= seg.end
    )
    setActiveSegmentIndex(activeIndex)
    
    // Auto scroll to active segment
    if (activeIndex >= 0 && segmentRefs.current[activeIndex]) {
      segmentRefs.current[activeIndex].scrollIntoView({
        behavior: 'smooth',
        block: 'center'
      })
    }
  }, [currentTime, segments])

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime)
    }
  }

  const handlePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause()
      } else {
        videoRef.current.play()
      }
      setIsPlaying(!isPlaying)
    }
  }

  const seekToSegment = (segment) => {
    if (videoRef.current) {
      videoRef.current.currentTime = segment.start
      videoRef.current.play()
      setIsPlaying(true)
    }
  }

  const skipTime = (seconds) => {
    if (videoRef.current) {
      videoRef.current.currentTime += seconds
    }
  }

  const startEdit = (index) => {
    setEditingIndex(index)
    setEditText(segments[index].text)
  }

  const cancelEdit = () => {
    setEditingIndex(null)
    setEditText('')
  }

  const saveEdit = (index) => {
    const updatedSegments = [...segments]
    updatedSegments[index] = {
      ...updatedSegments[index],
      text: editText
    }
    setSegments(updatedSegments)
    setEditingIndex(null)
    setEditText('')
  }

  const saveAllChanges = async () => {
    setSaving(true)
    setError(null)

    try {
      // Send updated segments to backend
      await axios.post(`/api/update-srt/${fileData.file_id}`, {
        segments: segments
      })

      // Notify parent component
      onEditComplete({
        ...transcriptionData,
        transcription: {
          ...transcriptionData.transcription,
          segments: segments
        }
      })
    } catch (err) {
      setError(err.response?.data?.detail || 'เกิดข้อผิดพลาดในการบันทึก')
    } finally {
      setSaving(false)
    }
  }

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    const ms = Math.floor((seconds % 1) * 1000)
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}.${String(ms).padStart(3, '0')}`
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="text-xl font-semibold">แก้ไข Subtitle ต้นฉบับ</h3>
            <p className="text-gray-600 text-sm mt-1">
              คลิกที่ข้อความเพื่อแก้ไข หรือคลิกที่เวลาเพื่อเล่นวิดีโอจากจุดนั้น
            </p>
          </div>
          <button
            onClick={saveAllChanges}
            disabled={saving}
            className="btn-primary flex items-center space-x-2"
          >
            {saving ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>กำลังบันทึก...</span>
              </>
            ) : (
              <>
                <Save className="h-4 w-4" />
                <span>บันทึกและดำเนินการต่อ</span>
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="flex items-center space-x-2 text-red-700 bg-red-50 p-3 rounded-lg">
            <AlertCircle className="h-5 w-5" />
            <span>{error}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Video Player */}
        <div className="card">
          <h4 className="font-semibold mb-4">วิดีโอต้นฉบับ</h4>
          
          <div className="bg-black rounded-lg overflow-hidden mb-4">
            <video
              ref={videoRef}
              src={`/api/stream-video/${fileData.file_id}`}
              className="w-full"
              onTimeUpdate={handleTimeUpdate}
              onPlay={() => setIsPlaying(true)}
              onPause={() => setIsPlaying(false)}
            />
          </div>

          {/* Video Controls */}
          <div className="space-y-3">
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(videoRef.current?.duration || 0)}</span>
            </div>

            <div className="flex items-center justify-center space-x-4">
              <button
                onClick={() => skipTime(-5)}
                className="p-2 hover:bg-gray-100 rounded-full transition"
                title="ย้อนกลับ 5 วินาที"
              >
                <SkipBack className="h-5 w-5" />
              </button>

              <button
                onClick={handlePlayPause}
                className="p-3 bg-primary-600 hover:bg-primary-700 text-white rounded-full transition"
              >
                {isPlaying ? (
                  <Pause className="h-6 w-6" />
                ) : (
                  <Play className="h-6 w-6" />
                )}
              </button>

              <button
                onClick={() => skipTime(5)}
                className="p-2 hover:bg-gray-100 rounded-full transition"
                title="ข้ามไป 5 วินาที"
              >
                <SkipForward className="h-5 w-5" />
              </button>
            </div>

            {/* Current Subtitle Display */}
            {activeSegmentIndex >= 0 && (
              <div className="bg-gray-900 text-white p-4 rounded-lg text-center">
                <p className="text-lg leading-relaxed">
                  {segments[activeSegmentIndex].text}
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Subtitle List */}
        <div className="card">
          <h4 className="font-semibold mb-4">รายการ Subtitle ({segments.length} รายการ)</h4>
          
          <div className="max-h-[600px] overflow-y-auto space-y-2">
            {segments.map((segment, index) => (
              <div
                key={index}
                ref={el => segmentRefs.current[index] = el}
                className={`border rounded-lg p-3 transition ${
                  activeSegmentIndex === index
                    ? 'border-primary-500 bg-primary-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                }`}
              >
                {/* Timestamp */}
                <button
                  onClick={() => seekToSegment(segment)}
                  className="text-xs text-primary-600 hover:text-primary-700 font-mono mb-2 flex items-center space-x-1"
                >
                  <Play className="h-3 w-3" />
                  <span>
                    {formatTime(segment.start)} → {formatTime(segment.end)}
                  </span>
                </button>

                {/* Text Content */}
                {editingIndex === index ? (
                  <div className="space-y-2">
                    <textarea
                      value={editText}
                      onChange={(e) => setEditText(e.target.value)}
                      className="w-full p-2 border border-gray-300 rounded resize-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                      rows={3}
                      autoFocus
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => saveEdit(index)}
                        className="flex-1 btn-primary text-sm py-1 flex items-center justify-center space-x-1"
                      >
                        <Check className="h-4 w-4" />
                        <span>บันทึก</span>
                      </button>
                      <button
                        onClick={cancelEdit}
                        className="flex-1 btn-secondary text-sm py-1 flex items-center justify-center space-x-1"
                      >
                        <X className="h-4 w-4" />
                        <span>ยกเลิก</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <div className="flex items-start justify-between group">
                    <p className="text-gray-800 leading-relaxed flex-1">
                      {segment.text}
                    </p>
                    <button
                      onClick={() => startEdit(index)}
                      className="ml-2 p-1 opacity-0 group-hover:opacity-100 hover:bg-gray-100 rounded transition"
                    >
                      <Edit3 className="h-4 w-4 text-gray-600" />
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Info */}
      <div className="card bg-blue-50 border-blue-200">
        <h4 className="font-semibold text-blue-900 mb-2">คำแนะนำ</h4>
        <div className="text-blue-800 text-sm space-y-1">
          <p>• คลิกที่เวลา (timestamp) เพื่อเล่นวิดีโอจากจุดนั้น</p>
          <p>• คลิกที่ไอคอนแก้ไขหรือข้อความเพื่อแก้ไข subtitle</p>
          <p>• Subtitle ที่กำลังเล่นจะถูกไฮไลท์และเลื่อนมาให้เห็นอัตโนมัติ</p>
          <p>• แก้ไขให้เสร็จแล้วคลิก "บันทึกและดำเนินการต่อ" เพื่อไปขั้นตอนแปลภาษา</p>
        </div>
      </div>
    </div>
  )
}

export default SubtitleEditor
