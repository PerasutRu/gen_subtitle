import React, { useState, useEffect } from 'react';
import { getStats, reloadLimits, getActivityStats } from '../../services/adminApi';
import { BarChart3, RefreshCw, Settings, Edit, Activity, TrendingUp } from 'lucide-react';
import DefaultLimitsModal from './DefaultLimitsModal';

const SystemStats = () => {
  const [stats, setStats] = useState(null);
  const [limits, setLimits] = useState(null);
  const [activityStats, setActivityStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [reloading, setReloading] = useState(false);
  const [showLimitsModal, setShowLimitsModal] = useState(false);

  const loadStats = async () => {
    try {
      setLoading(true);
      const [statsData, activityData] = await Promise.all([
        getStats(),
        getActivityStats()
      ]);
      setStats(statsData.stats);
      setLimits(statsData.limits);
      setActivityStats(activityData);
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
            ค่า Limits ของระบบ (Default)
          </h3>
          <div className="flex space-x-2">
            <button
              onClick={() => setShowLimitsModal(true)}
              className="flex items-center space-x-1 px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600"
            >
              <Edit className="h-4 w-4" />
              <span>แก้ไข</span>
            </button>
            <button
              onClick={handleReloadLimits}
              disabled={reloading}
              className="px-3 py-1 text-sm bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
            >
              {reloading ? 'กำลังโหลด...' : 'โหลดใหม่'}
            </button>
          </div>
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
                {stats.total_duration_minutes || 0}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Activity Stats */}
      {activityStats && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Activity className="mr-2 h-5 w-5" />
            Activity Statistics
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Activities by Type */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Activities by Type</h4>
              <div className="space-y-2">
                {Object.entries(activityStats.by_type || {}).map(([type, count]) => (
                  <div key={type} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{type.replace('_', ' ')}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Provider Usage */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Provider Usage</h4>
              <div className="space-y-2">
                {Object.entries(activityStats.provider_usage || {}).map(([provider, count]) => (
                  <div key={provider} className="flex justify-between items-center">
                    <span className="text-sm text-gray-600 capitalize">{provider}</span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Success Rate */}
            <div>
              <h4 className="text-sm font-medium text-gray-700 mb-3">Success Rate</h4>
              <div className="space-y-2">
                {Object.entries(activityStats.by_status || {}).map(([status, count]) => (
                  <div key={status} className="flex justify-between items-center">
                    <span className={`text-sm capitalize ${status === 'success' ? 'text-green-600' : 'text-red-600'}`}>
                      {status}
                    </span>
                    <span className="text-sm font-semibold text-gray-900">{count}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Language Usage */}
            {activityStats.language_usage && Object.keys(activityStats.language_usage).length > 0 && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Translation Languages</h4>
                <div className="space-y-2">
                  {Object.entries(activityStats.language_usage).slice(0, 5).map(([lang, count]) => (
                    <div key={lang} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600 uppercase">{lang}</span>
                      <span className="text-sm font-semibold text-gray-900">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Total Activities */}
          <div className="mt-6 pt-6 border-t">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">Total Activities</span>
              <span className="text-2xl font-bold text-blue-600">{activityStats.total_activities || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Default Limits Modal */}
      <DefaultLimitsModal
        isOpen={showLimitsModal}
        onClose={() => setShowLimitsModal(false)}
        onSuccess={() => {
          loadStats();
        }}
      />
    </div>
  );
};

export default SystemStats;
