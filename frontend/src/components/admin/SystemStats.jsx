import React, { useState, useEffect } from 'react';
import { getStats, reloadLimits } from '../../services/adminApi';
import { BarChart3, RefreshCw, Settings } from 'lucide-react';

const SystemStats = () => {
  const [stats, setStats] = useState(null);
  const [limits, setLimits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reloading, setReloading] = useState(false);

  const loadStats = async () => {
    try {
      setLoading(true);
      const data = await getStats();
      setStats(data.stats);
      setLimits(data.limits);
    } catch (error) {
      console.error('Error loading stats:', error);
      alert('ไม่สามารถโหลดสถิติได้');
    } finally {
      setLoading(false);
    }
  };

  const handleReloadLimits = async () => {
    if (!confirm('ต้องการโหลดค่า limits ใหม่จาก config file?')) return;
    
    try {
      setReloading(true);
      const data = await reloadLimits();
      setLimits(data.limits);
      alert('โหลดค่า limits ใหม่สำเร็จ');
    } catch (error) {
      console.error('Error reloading limits:', error);
      alert('ไม่สามารถโหลดค่า limits ได้');
    } finally {
      setReloading(false);
    }
  };

  useEffect(() => {
    loadStats();
  }, []);

  if (loading) {
    return <div className="text-center py-8">กำลังโหลด...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <BarChart3 className="mr-2" />
          สถิติระบบ
        </h2>
        <button
          onClick={loadStats}
          className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
        >
          <RefreshCw className="h-4 w-4" />
          <span>รีเฟรช</span>
        </button>
      </div>

      {/* System Limits */}
      <div className="bg-white rounded-lg shadow p-6">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <Settings className="mr-2 h-5 w-5" />
            ค่า Limits ของระบบ
          </h3>
          <button
            onClick={handleReloadLimits}
            disabled={reloading}
            className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
          >
            {reloading ? 'กำลังโหลด...' : 'โหลดใหม่'}
          </button>
        </div>
        {limits && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded">
              <p className="text-sm text-gray-600">จำนวนวิดีโอสูงสุด</p>
              <p className="text-2xl font-bold text-blue-600">{limits.maxVideos}</p>
            </div>
            <div className="bg-green-50 p-4 rounded">
              <p className="text-sm text-gray-600">ความยาวสูงสุด (นาที)</p>
              <p className="text-2xl font-bold text-green-600">{limits.maxDurationMinutes}</p>
            </div>
            <div className="bg-purple-50 p-4 rounded">
              <p className="text-sm text-gray-600">ขนาดไฟล์สูงสุด (MB)</p>
              <p className="text-2xl font-bold text-purple-600">{limits.maxFileSizeMB}</p>
            </div>
            <div className="bg-orange-50 p-4 rounded">
              <p className="text-sm text-gray-600">ไฟล์ที่รองรับ</p>
              <p className="text-sm font-semibold text-orange-600">
                {limits.allowedExtensions?.join(', ')}
              </p>
            </div>
          </div>
        )}
      </div>

      {/* Usage Stats */}
      {stats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">สถิติการใช้งาน</h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="bg-indigo-50 p-4 rounded">
              <p className="text-sm text-gray-600">จำนวน Sessions</p>
              <p className="text-2xl font-bold text-indigo-600">{stats.total_sessions || 0}</p>
            </div>
            <div className="bg-pink-50 p-4 rounded">
              <p className="text-sm text-gray-600">วิดีโอทั้งหมด</p>
              <p className="text-2xl font-bold text-pink-600">{stats.total_videos || 0}</p>
            </div>
            <div className="bg-yellow-50 p-4 rounded">
              <p className="text-sm text-gray-600">ความยาวรวม (นาที)</p>
              <p className="text-2xl font-bold text-yellow-600">
                {stats.total_duration ? (stats.total_duration / 60).toFixed(1) : 0}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SystemStats;
