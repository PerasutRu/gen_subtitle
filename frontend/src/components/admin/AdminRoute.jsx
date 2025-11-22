import React from 'react';
import { Navigate } from 'react-router-dom';

const AdminRoute = ({ children, user }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  if (user.role !== 'admin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center">
          <h2 className="text-2xl font-bold text-red-600 mb-4">Access Denied</h2>
          <p className="text-gray-600">คุณไม่มีสิทธิ์เข้าถึงหน้านี้</p>
          <p className="text-sm text-gray-500 mt-2">ต้องเป็น Admin เท่านั้น</p>
        </div>
      </div>
    );
  }

  return children;
};

export default AdminRoute;
