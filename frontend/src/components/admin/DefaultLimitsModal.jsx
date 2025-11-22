import React, { useState, useEffect } from 'react';
import { X, Save } from 'lucide-react';
import { getDefaultLimits, updateDefaultLimits } from '../../services/adminApi';

const DefaultLimitsModal = ({ isOpen, onClose, onSuccess }) => {
  const [limits, setLimits] = useState({
    maxVideos: 10,
    maxDurationMinutes: 10,
    maxFileSizeMB: 500
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (isOpen) {
      loadDefaultLimits();
    }
  }, [isOpen]);

  const loadDefaultLimits = async () => {
    try {
      const data = await getDefaultLimits();
      setLimits(data.limits);
      setError('');
    } catch (err) {
      console.error('Error loading default limits:', err);
      setError('ไม่สามารถโหลดข้อมูล limits ได้');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const result = await updateDefaultLimits(limits);
      alert(result.message || 'อัปเดต default limits สำเร็จ');
      onSuccess();
      onClose();
    } catch (err) {
      console.error('Error updating default limits:', err);
      const errorMsg = err.response?.data?.detail || 'ไม่สามารถอัปเดต limits ได้';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex justify-between items-center p-6 border-b">
          <h3 className="text-xl font-semibold text-gray-900">
            แก้ไข Default Limits
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          <div className="bg-yellow-50 border border-yellow-200 text-yellow-800 px-4 py-3 rounded text-sm">
            ⚠️ การเปลี่ยนแปลงนี้จะมีผลกับ user ใหม่และ user ที่ไม่มี custom limits
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              จำนวนวิดีโอสูงสุด
            </label>
            <input
              type="number"
              min="1"
              value={limits.maxVideos}
              onChange={(e) => setLimits({ ...limits, maxVideos: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ความยาววิดีโอสูงสุด (นาที)
            </label>
            <input
              type="number"
              min="1"
              value={limits.maxDurationMinutes}
              onChange={(e) => setLimits({ ...limits, maxDurationMinutes: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              ขนาดไฟล์สูงสุด (MB)
            </label>
            <input
              type="number"
              min="1"
              value={limits.maxFileSizeMB}
              onChange={(e) => setLimits({ ...limits, maxFileSizeMB: parseInt(e.target.value) })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
          </div>

          {/* Footer */}
          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              disabled={loading}
            >
              ยกเลิก
            </button>
            <button
              type="submit"
              className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50"
              disabled={loading}
            >
              <Save className="h-4 w-4" />
              <span>{loading ? 'กำลังบันทึก...' : 'บันทึก'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default DefaultLimitsModal;
