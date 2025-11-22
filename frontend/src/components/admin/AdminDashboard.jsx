import React, { useState } from 'react';
import { LayoutDashboard, Users, Database, BarChart3, Activity, LogOut } from 'lucide-react';
import UserManagement from './UserManagement';
import SessionManagement from './SessionManagement';
import SystemStats from './SystemStats';
import ActivityLogs from './ActivityLogs';

const AdminDashboard = ({ user, onLogout }) => {
  const [activeTab, setActiveTab] = useState('stats');

  const tabs = [
    { id: 'stats', label: 'สถิติระบบ', icon: BarChart3 },
    { id: 'activities', label: 'Activity Logs', icon: Activity },
    { id: 'users', label: 'จัดการ Users', icon: Users },
    { id: 'sessions', label: 'จัดการ Sessions', icon: Database },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 to-pink-100">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <LayoutDashboard className="h-8 w-8 text-purple-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
                <p className="text-gray-600">ระบบจัดการ Video Subtitle Generator</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-right">
                <p className="text-sm text-gray-600">Admin</p>
                <p className="font-semibold text-gray-900">{user.username}</p>
              </div>
              <button
                onClick={onLogout}
                className="flex items-center space-x-2 px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
              >
                <LogOut className="h-4 w-4" />
                <span>ออกจากระบบ</span>
              </button>
            </div>
          </div>
        </div>

        {/* Tabs */}
        <div className="bg-white rounded-lg shadow-lg mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center space-x-2 px-6 py-4 border-b-2 font-medium text-sm transition-colors ${
                      activeTab === tab.id
                        ? 'border-purple-500 text-purple-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{tab.label}</span>
                  </button>
                );
              })}
            </nav>
          </div>
        </div>

        {/* Content */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          {activeTab === 'stats' && <SystemStats />}
          {activeTab === 'activities' && <ActivityLogs />}
          {activeTab === 'users' && <UserManagement />}
          {activeTab === 'sessions' && <SessionManagement />}
        </div>
      </div>
    </div>
  );
};

export default AdminDashboard;
