import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LabelList
} from 'recharts';

const ActivityCharts = ({ stats }) => {
  if (!stats) return null;

  // Enhanced color palette with gradients
  const COLORS = {
    upload: '#3B82F6',      // blue-500
    transcribe: '#10B981',  // green-500
    translate: '#F59E0B',   // amber-500
    embed_subtitle: '#8B5CF6', // purple-500
    openai: '#3B82F6',
    botnoi: '#10B981',
    success: '#10B981',
    failed: '#EF4444'
  };

  // Custom tooltip style
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div className="bg-white px-4 py-3 rounded-lg shadow-lg border border-gray-200">
          <p className="font-semibold text-gray-900 mb-1">{label}</p>
          {payload.map((entry, index) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: <span className="font-bold">{entry.value}</span>
            </p>
          ))}
        </div>
      );
    }
    return null;
  };

  // Prepare data for Activity Distribution (Pie Chart)
  const activityDistribution = Object.entries(stats.by_type || {}).map(([name, value]) => {
    const displayNames = {
      upload: 'Upload',
      transcribe: 'Transcribe',
      translate: 'Translate',
      embed_subtitle: 'Embed'
    };
    return {
      name: displayNames[name] || name,
      value,
      color: COLORS[name] || '#6B7280'
    };
  });

  // Prepare data for Provider Usage (Bar Chart)
  const providerData = Object.entries(stats.provider_usage || {}).map(([name, value]) => ({
    name: name.toUpperCase(),
    count: value,
    fill: COLORS[name] || '#6B7280'
  }));

  // Prepare data for Timeline (Line Chart)
  const timelineData = (stats.recent_by_date || []).reverse().map(item => ({
    date: new Date(item.date).toLocaleDateString('th-TH', { month: 'short', day: 'numeric' }),
    activities: item.count
  }));

  // Prepare data for Language Distribution (Bar Chart)
  const languageNames = {
    en: 'English',
    th: 'Thai',
    jp: 'Japanese',
    ja: 'Japanese',
    ko: 'Korean',
    kr: 'Korean',
    zh: 'Chinese',
    cn: 'Chinese',
    vi: 'Vietnamese',
    id: 'Indonesian',
    ms: 'Malay',
    tl: 'Tagalog',
    my: 'Myanmar',
    lo: 'Lao',
    km: 'Khmer'
  };

  const languageColors = ['#F59E0B', '#EF4444', '#8B5CF6', '#10B981', '#3B82F6'];
  
  const languageData = Object.entries(stats.language_usage || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 5)
    .map(([code, value], index) => ({
      language: languageNames[code.toLowerCase()] || code.toUpperCase(),
      count: value,
      color: languageColors[index]
    }));

  // Calculate success rate
  const totalByStatus = Object.values(stats.by_status || {}).reduce((a, b) => a + b, 0);
  const successCount = stats.by_status?.success || 0;
  const successRate = totalByStatus > 0 ? ((successCount / totalByStatus) * 100).toFixed(1) : 0;

  return (
    <div className="space-y-6">
      {/* Row 1: Timeline and Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Activity Timeline */}
        {timelineData.length > 0 && (
          <div className="bg-gradient-to-br from-blue-50 to-white rounded-xl shadow-lg p-6 border border-blue-100">
            <div className="flex items-center mb-4">
              <div className="w-2 h-8 bg-blue-500 rounded-full mr-3"></div>
              <h3 className="text-lg font-bold text-gray-900">Activity Timeline</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">Last 7 days activity trend</p>
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={timelineData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <defs>
                  <linearGradient id="colorActivities" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="#3B82F6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="date" 
                  tick={{ fill: '#6B7280', fontSize: 12 }}
                  tickLine={{ stroke: '#E5E7EB' }}
                />
                <YAxis 
                  tick={{ fill: '#6B7280', fontSize: 12 }}
                  tickLine={{ stroke: '#E5E7EB' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Line 
                  type="monotone" 
                  dataKey="activities" 
                  stroke="#3B82F6" 
                  strokeWidth={3}
                  dot={{ fill: '#3B82F6', r: 5, strokeWidth: 2, stroke: '#fff' }}
                  activeDot={{ r: 7, strokeWidth: 2 }}
                  fill="url(#colorActivities)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Activity Distribution */}
        {activityDistribution.length > 0 && (
          <div className="bg-gradient-to-br from-purple-50 to-white rounded-xl shadow-lg p-6 border border-purple-100">
            <div className="flex items-center mb-4">
              <div className="w-2 h-8 bg-purple-500 rounded-full mr-3"></div>
              <h3 className="text-lg font-bold text-gray-900">Activity Distribution</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">Breakdown by activity type</p>
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={activityDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={90}
                  innerRadius={50}
                  fill="#8884d8"
                  dataKey="value"
                  paddingAngle={2}
                >
                  {activityDistribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.color}
                      stroke="#fff"
                      strokeWidth={2}
                    />
                  ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Row 2: Provider Usage and Success Rate */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Provider Usage */}
        {providerData.length > 0 && (
          <div className="bg-gradient-to-br from-green-50 to-white rounded-xl shadow-lg p-6 border border-green-100">
            <div className="flex items-center mb-4">
              <div className="w-2 h-8 bg-green-500 rounded-full mr-3"></div>
              <h3 className="text-lg font-bold text-gray-900">Provider Usage</h3>
            </div>
            <p className="text-sm text-gray-600 mb-4">API provider comparison</p>
            <ResponsiveContainer width="100%" height={240}>
              <BarChart data={providerData} margin={{ top: 5, right: 20, left: 0, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                <XAxis 
                  dataKey="name" 
                  tick={{ fill: '#6B7280', fontSize: 13, fontWeight: 600 }}
                  tickLine={{ stroke: '#E5E7EB' }}
                />
                <YAxis 
                  tick={{ fill: '#6B7280', fontSize: 12 }}
                  tickLine={{ stroke: '#E5E7EB' }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Bar 
                  dataKey="count" 
                  fill="#3B82F6"
                  radius={[8, 8, 0, 0]}
                >
                  {providerData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.fill}
                    />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {/* Success Rate */}
        <div className="bg-gradient-to-br from-emerald-50 to-white rounded-xl shadow-lg p-6 border border-emerald-100">
          <div className="flex items-center mb-4">
            <div className="w-2 h-8 bg-emerald-500 rounded-full mr-3"></div>
            <h3 className="text-lg font-bold text-gray-900">Success Rate</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">System reliability metric</p>
          <div className="flex flex-col items-center justify-center h-[240px]">
            <div className="relative w-44 h-44">
              <svg className="w-full h-full transform -rotate-90">
                <defs>
                  <linearGradient id="successGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" stopColor={successRate >= 90 ? '#10B981' : successRate >= 70 ? '#F59E0B' : '#EF4444'} />
                    <stop offset="100%" stopColor={successRate >= 90 ? '#059669' : successRate >= 70 ? '#D97706' : '#DC2626'} />
                  </linearGradient>
                </defs>
                <circle
                  cx="88"
                  cy="88"
                  r="75"
                  stroke="#E5E7EB"
                  strokeWidth="14"
                  fill="none"
                />
                <circle
                  cx="88"
                  cy="88"
                  r="75"
                  stroke="url(#successGradient)"
                  strokeWidth="14"
                  fill="none"
                  strokeDasharray={`${(successRate / 100) * 471.2} 471.2`}
                  strokeLinecap="round"
                  style={{ transition: 'stroke-dasharray 1s ease-in-out' }}
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-5xl font-bold bg-gradient-to-r from-emerald-600 to-green-600 bg-clip-text text-transparent">
                  {successRate}%
                </span>
                <span className="text-sm font-medium text-gray-600 mt-1">Success Rate</span>
              </div>
            </div>
            <div className="mt-6 flex gap-6 text-sm font-medium">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-gradient-to-r from-green-400 to-emerald-500 mr-2 shadow-sm"></div>
                <span className="text-gray-700">Success: <span className="font-bold text-green-600">{stats.by_status?.success || 0}</span></span>
              </div>
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-gradient-to-r from-red-400 to-red-500 mr-2 shadow-sm"></div>
                <span className="text-gray-700">Failed: <span className="font-bold text-red-600">{stats.by_status?.failed || 0}</span></span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Row 3: Language Distribution */}
      {languageData.length > 0 && (
        <div className="bg-gradient-to-br from-amber-50 to-white rounded-xl shadow-lg p-6 border border-amber-100">
          <div className="flex items-center mb-4">
            <div className="w-2 h-8 bg-amber-500 rounded-full mr-3"></div>
            <h3 className="text-lg font-bold text-gray-900">Top Translation Languages</h3>
          </div>
          <p className="text-sm text-gray-600 mb-4">Most popular target languages</p>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={languageData} layout="vertical" margin={{ top: 5, right: 50, left: 10, bottom: 5 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
              <XAxis 
                type="number" 
                tick={{ fill: '#6B7280', fontSize: 12 }}
                tickLine={{ stroke: '#E5E7EB' }}
              />
              <YAxis 
                dataKey="language" 
                type="category" 
                tick={{ fill: '#374151', fontSize: 13, fontWeight: 600 }}
                tickLine={{ stroke: '#E5E7EB' }}
                width={90}
              />
              <Tooltip content={<CustomTooltip />} />
              <Bar 
                dataKey="count" 
                radius={[0, 8, 8, 0]}
              >
                <LabelList 
                  dataKey="count" 
                  position="right" 
                  style={{ fill: '#374151', fontWeight: 'bold', fontSize: 13 }}
                />
                {languageData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.color}
                  />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
};

export default ActivityCharts;
