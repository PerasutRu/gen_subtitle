import React, { useState, useEffect } from 'react';
import { getActivities } from '../../services/adminApi';
import { Activity, Filter, ChevronLeft, ChevronRight, Eye, X } from 'lucide-react';

const ActivityLogs = () => {
  const [activities, setActivities] = useState([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit] = useState(30);
  
  // Filters
  const [filters, setFilters] = useState({
    activity_type: '',
    username: '',
    status: '',
    date_from: '',
    date_to: ''
  });
  
  // Detail modal
  const [selectedActivity, setSelectedActivity] = useState(null);

  const loadActivities = async () => {
    try {
      setLoading(true);
      const offset = (page - 1) * limit;
      
      const params = {
        limit,
        offset,
        ...Object.fromEntries(
          Object.entries(filters).filter(([_, v]) => v !== '')
        )
      };
      
      const data = await getActivities(params);
      setActivities(data.activities);
      setTotal(data.total);
    } catch (error) {
      console.error('Error loading activities:', error);
      alert('ไม่สามารถโหลด activity logs ได้');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Debounce for username filter (wait 500ms after user stops typing)
    const timeoutId = setTimeout(() => {
      loadActivities();
    }, filters.username ? 500 : 0);

    return () => clearTimeout(timeoutId);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page, filters.activity_type, filters.username, filters.status, filters.date_from, filters.date_to]);

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setPage(1); // Reset to first page
  };

  const clearFilters = () => {
    setFilters({
      activity_type: '',
      username: '',
      status: '',
      date_from: '',
      date_to: ''
    });
    setPage(1);
  };

  const getActivityBadge = (type) => {
    const badges = {
      upload: { color: 'bg-blue-100 text-blue-800', label: '📤 Upload' },
      transcribe: { color: 'bg-green-100 text-green-800', label: '🎤 Transcribe' },
      translate: { color: 'bg-yellow-100 text-yellow-800', label: '🌐 Translate' },
      embed_subtitle: { color: 'bg-purple-100 text-purple-800', label: '🎬 Embed' }
    };
    const badge = badges[type] || { color: 'bg-gray-100 text-gray-800', label: type };
    return (
      <span className={`px-2 py-1 rounded text-xs font-medium ${badge.color}`}>
        {badge.label}
      </span>
    );
  };

  const getStatusBadge = (status) => {
    if (status === 'success') {
      return <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-800">✓ Success</span>;
    }
    return <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-800">✗ Failed</span>;
  };

  const totalPages = Math.ceil(total / limit);

  if (loading && activities.length === 0) {
    return <div className="text-center py-8">กำลังโหลด...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center">
          <Activity className="mr-2" />
          Activity Logs ({total})
        </h2>
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-gray-700 flex items-center">
            <Filter className="h-4 w-4 mr-2" />
            Filters
          </h3>
          <button
            onClick={clearFilters}
            className="text-sm text-gray-600 hover:text-gray-800 flex items-center"
          >
            <X className="h-4 w-4 mr-1" />
            Clear
          </button>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-5 gap-3">
          <select
            value={filters.activity_type}
            onChange={(e) => handleFilterChange('activity_type', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Activities</option>
            <option value="upload">Upload</option>
            <option value="transcribe">Transcribe</option>
            <option value="translate">Translate</option>
            <option value="embed_subtitle">Embed Subtitle</option>
          </select>

          <input
            type="text"
            placeholder="Username"
            value={filters.username}
            onChange={(e) => handleFilterChange('username', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />

          <select
            value={filters.status}
            onChange={(e) => handleFilterChange('status', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          >
            <option value="">All Status</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>

          <input
            type="date"
            placeholder="From Date"
            value={filters.date_from}
            onChange={(e) => handleFilterChange('date_from', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />

          <input
            type="date"
            placeholder="To Date"
            value={filters.date_to}
            onChange={(e) => handleFilterChange('date_to', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg text-sm"
          />
        </div>
      </div>

      {/* Activities Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Time</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">User</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Activity</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">File ID</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Details</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {activities.length === 0 ? (
                <tr>
                  <td colSpan="7" className="px-4 py-8 text-center text-gray-500">
                    ไม่มี activity logs
                  </td>
                </tr>
              ) : (
                activities.map((activity) => (
                  <tr key={activity.id} className="hover:bg-gray-50">
                    <td className="px-4 py-3 whitespace-nowrap text-sm text-gray-600">
                      {new Date(activity.created_at).toLocaleString('th-TH', {
                        year: '2-digit',
                        month: '2-digit',
                        day: '2-digit',
                        hour: '2-digit',
                        minute: '2-digit'
                      })}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm">
                      <span className="font-mono text-gray-900">{activity.username || '-'}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {getActivityBadge(activity.activity_type)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-sm font-mono text-gray-600">
                      {activity.file_id ? activity.file_id.substring(0, 8) + '...' : '-'}
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">
                      {activity.details?.provider && (
                        <span className="text-xs bg-gray-100 px-2 py-1 rounded mr-1">
                          {activity.details.provider}
                        </span>
                      )}
                      {activity.details?.target_language && (
                        <span className="text-xs bg-blue-100 px-2 py-1 rounded mr-1">
                          → {activity.details.target_language}
                        </span>
                      )}
                      {activity.details?.subtitle_type && (
                        <span className="text-xs bg-purple-100 px-2 py-1 rounded">
                          {activity.details.subtitle_type}
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {getStatusBadge(activity.status)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap text-center">
                      <button
                        onClick={() => setSelectedActivity(activity)}
                        className="text-blue-600 hover:text-blue-800"
                      >
                        <Eye className="h-4 w-4" />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="bg-gray-50 px-4 py-3 flex items-center justify-between border-t">
            <div className="text-sm text-gray-700">
              Showing {(page - 1) * limit + 1} to {Math.min(page * limit, total)} of {total} results
            </div>
            <div className="flex space-x-2">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronLeft className="h-4 w-4" />
              </button>
              <span className="px-3 py-1 text-sm">
                Page {page} of {totalPages}
              </span>
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="px-3 py-1 border rounded hover:bg-gray-100 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <ChevronRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {selectedActivity && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex justify-between items-center p-6 border-b">
              <h3 className="text-xl font-semibold">Activity Details</h3>
              <button
                onClick={() => setSelectedActivity(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            
            <div className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Activity Type</label>
                  <div className="mt-1">{getActivityBadge(selectedActivity.activity_type)}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Status</label>
                  <div className="mt-1">{getStatusBadge(selectedActivity.status)}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Username</label>
                  <div className="mt-1 font-mono text-sm">{selectedActivity.username || '-'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Session ID</label>
                  <div className="mt-1 font-mono text-sm text-xs">{selectedActivity.session_id}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">File ID</label>
                  <div className="mt-1 font-mono text-sm">{selectedActivity.file_id || '-'}</div>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Time</label>
                  <div className="mt-1 text-sm">
                    {new Date(selectedActivity.created_at).toLocaleString('th-TH')}
                  </div>
                </div>
              </div>

              {selectedActivity.details && Object.keys(selectedActivity.details).length > 0 && (
                <div>
                  <label className="text-sm font-medium text-gray-500">Details</label>
                  <pre className="mt-1 bg-gray-50 p-3 rounded text-xs overflow-x-auto">
                    {JSON.stringify(selectedActivity.details, null, 2)}
                  </pre>
                </div>
              )}

              {selectedActivity.error_message && (
                <div>
                  <label className="text-sm font-medium text-red-500">Error Message</label>
                  <div className="mt-1 bg-red-50 p-3 rounded text-sm text-red-700">
                    {selectedActivity.error_message}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ActivityLogs;
