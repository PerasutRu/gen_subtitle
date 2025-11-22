import React, { useState, useEffect } from 'react';
import { getSessions, deleteSession, resetAllSessions } from '../../services/adminApi';
import { Database, Trash2, RefreshCw, AlertTriangle } from 'lucide-react';

const SessionManagement = () => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  const loadSessions = async () => {
    try {
      setLoading(true);
      const data = await getSessions();
      setSessions(data.sessions);
    } catch (error) {
      console.error('Error loading sessions:', error);
      alert('ไม่สามารถโหลดรายการ sessions ได้');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteSession = async (sessionId) => {
    if (!confirm(`ต้องการลบ session "${sessionId}"?`)) return;
    
    try {
      const result = await deleteSession(sessionId);
      console.log('✅ Delete session result:', result);
      
      // Reload sessions first
      await loadSessions();
      
      // Show success message
      alert(result.message || 'ลบ session สำเร็จ');
    } catch (error) {
      console.error('❌ Error deleting session:', error);
      console.error('   Error response:', error.response);
      
      // Check if it's actually successful (status 200)
      if (error.response?.status === 200 || error.response?.data?.success) {
        console.log('   Actually successful, reloading...');
        await loadSessions();
        alert('ลบ session สำเร็จ');
      } else {
        // Real error
        const errorMsg = error.response?.data?.detail || 'ไม่สามารถลบ session ได้';
        alert(errorMsg);
      }
    }
  };

  const handleResetAll = async () => {
    if (!confirm('⚠️ ต้องการลบ session ทั้งหมด? การกระทำนี้ไม่สามารถย้อนกลับได้!')) return;
    
    try {
      const result = await resetAllSessions();
      console.log('✅ Reset all result:', result);
      
      // Reload sessions first
      await loadSessions();
      
      // Show success message
      alert(result.message || 'Reset สำเร็จ ลบ session ทั้งหมดแล้ว');
    } catch (error) {
      console.error('❌ Error resetting sessions:', error);
      console.error('   Error response:', error.response);
      
      // Check if it's actually successful
      if (error.response?.status === 200 || error.response?.data?.success) {
        console.log('   Actually successful, reloading...');
        await loadSessions();
        alert('Reset สำเร็จ ลบ session ทั้งหมดแล้ว');
      } else {
        const errorMsg = error.response?.data?.detail || 'ไม่สามารถ reset sessions ได้';
        alert(errorMsg);
      }
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  if (loading) {
    return <div className="text-center py-8">กำลังโหลด...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Database className="mr-2" />
          จัดการ Sessions ({sessions.length})
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={loadSessions}
            className="flex items-center space-x-2 px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600"
          >
            <RefreshCw className="h-4 w-4" />
            <span>รีเฟรช</span>
          </button>
          <button
            onClick={handleResetAll}
            className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600"
          >
            <AlertTriangle className="h-4 w-4" />
            <span>Reset ทั้งหมด</span>
          </button>
        </div>
      </div>

      {/* Sessions Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Session ID
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                จำนวนวิดีโอ
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                ความยาวรวม (นาที)
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                สร้างเมื่อ
              </th>
              <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sessions.length === 0 ? (
              <tr>
                <td colSpan="5" className="px-6 py-4 text-center text-gray-500">
                  ไม่มี session
                </td>
              </tr>
            ) : (
              sessions.map((session) => (
                <tr key={session.session_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-mono text-gray-900">{session.session_id}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">{session.videos_count || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-900">
                      {session.total_duration ? (session.total_duration / 60).toFixed(1) : 0}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {session.created_at ? new Date(session.created_at).toLocaleString('th-TH') : '-'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleDeleteSession(session.session_id)}
                      className="text-red-600 hover:text-red-900 flex items-center justify-end ml-auto"
                    >
                      <Trash2 className="h-4 w-4 mr-1" />
                      ลบ
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default SessionManagement;
