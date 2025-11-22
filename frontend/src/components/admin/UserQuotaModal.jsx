import React, { useState, useEffect } from 'react';
import { getUserLimits, setUserLimits, deleteUserLimits } from '../../services/adminApi';
import { X, Save, RotateCcw } from 'lucide-react';

const UserQuotaModal = ({ username, onClose, onSuccess }) => {
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [defaultLimits, setDefaultLimits] = useState(null);
  const [formData, setFormData] = useState({
    maxVideos: '',
    maxDurationMinutes: '',
    maxFileSizeMB: ''
  });
  const [hasCustomLimits, setHasCustomLimits] = useState(false);

  useEffect(() => {
    loadUserLimits();
  }, [username]);

  const loadUserLimits = async () => {
    try {
      setLoading(true);
      const data = await getUserLimits(username);
      
      setDefaultLimits(data.default_limits);
      
      if (data.custom_limits) {
        setFormData({
          maxVideos: data.custom_limits.maxVideos,
          maxDurationMinutes: data.custom_limits.maxDurationMinutes,
          maxFileSizeMB: data.custom_limits.maxFileSizeMB
        });
        setHasCustomLimits(true);
      } else {
        setFormData({
          maxVideos: data.default_limits.maxVideos,
          maxDurationMinutes: data.default_limits.maxDurationMinutes,
          maxFileSizeMB: data.default_limits.maxFileSizeMB
        });
        setHasCustomLimits(false);
      }
    } catch (error) {
      console.error('Error loading user limits:', error);
      alert('ไม่สามารถโหลดข้อมูล limits ได้');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    
    // Validation
    if (formData.maxVideos <= 0 || formData.maxDurationMinutes <= 0 || formData.maxFileSizeMB <= 0) {
      alert('กรุณากรอกค่าที่มากกว่า 0');
      return;
    }
    
    try {
      setSaving(true);
      await setUserLimits(username, {
        maxVideos: parseInt(formData.maxVideos),
        maxDurationMinutes: parseInt(formData.maxDurationMinutes),
        maxFileSizeMB: parseInt(formData.maxFileSizeMB)
      });
      
      alert('ตั้งค่า quota สำเร็จ');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error saving limits:', error);
      alert(error.response?.data?.detail || 'ไม่สามารถบันทึกได้');
    } finally {
      setSaving(false);
    }
  };

  const handleUseDefault = async () => {
    if (!confirm('ต้องการใช้ค่า default และลบ custom limits?')) return;
    
    try {
      setSaving(true);
      await deleteUserLimits(username);
      alert('ลบ custom limits สำเร็จ (ใช้ค่า default)');
      onSuccess();
      onClose();
    } catch (error) {
      console.error('Error deleting limits:', error);
      alert('ไม่สามารถลบ custom limits ได้');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8">
          <p>กำลังโหลด...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b">
          <h3 className="text-xl font-bold text-gray-900">
            ตั้งค่า Quota: {username}
          </h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Body */}
        <form onSubmit={handleSave} className="p-6 space-y-4">
          {hasCustomLimits && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 text-sm text-blue-800">
              ℹ️ User นี้มี custom quota อยู่แล้ว
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              จำนวนวิดีโอสูงสุด
            </label>
            <input
              type="number"
              required
              min="1"
              value={formData.maxVideos}
              onChange={(e) => setFormData({...formData, maxVideos: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            {defaultLimits && (
              <p className="text-xs text-gray-500 mt-1">
                Default: {defaultLimits.maxVideos} ไฟล์
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ความยาววิดีโอสูงสุด (นาที)
            </label>
            <input
              type="number"
              required
              min="1"
              value={formData.maxDurationMinutes}
              onChange={(e) => setFormData({...formData, maxDurationMinutes: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            {defaultLimits && (
              <p className="text-xs text-gray-500 mt-1">
                Default: {defaultLimits.maxDurationMinutes} นาที
              </p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              ขนาดไฟล์สูงสุด (MB)
            </label>
            <input
              type="number"
              required
              min="1"
              value={formData.maxFileSizeMB}
              onChange={(e) => setFormData({...formData, maxFileSizeMB: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500"
            />
            {defaultLimits && (
              <p className="text-xs text-gray-500 mt-1">
                Default: {defaultLimits.maxFileSizeMB} MB
              </p>
            )}
          </div>

          {/* Actions */}
          <div className="flex space-x-2 pt-4">
            {hasCustomLimits && (
              <button
                type="button"
                onClick={handleUseDefault}
                disabled={saving}
                className="flex items-center space-x-2 px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 disabled:opacity-50"
              >
                <RotateCcw className="h-4 w-4" />
                <span>ใช้ค่า Default</span>
              </button>
            )}
            <button
              type="submit"
              disabled={saving}
              className="flex-1 flex items-center justify-center space-x-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 disabled:opacity-50"
            >
              <Save className="h-4 w-4" />
              <span>{saving ? 'กำลังบันทึก...' : 'บันทึก'}</span>
            </button>
            <button
              type="button"
              onClick={onClose}
              disabled={saving}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 disabled:opacity-50"
            >
              ยกเลิก
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default UserQuotaModal;
