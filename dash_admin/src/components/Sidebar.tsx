import React from 'react';
import { Link, useLocation } from 'react-router-dom';

// Iconos para la barra lateral
const DashboardIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>
  </svg>
);

const UsersIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path>
  </svg>
);

const PostsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 20H5a2 2 0 01-2-2V6a2 2 0 012-2h10a2 2 0 012 2v1m2 13a2 2 0 01-2-2V7m2 13a2 2 0 002-2V9a2 2 0 00-2-2h-2m-4-3H9M7 16h6M7 8h6v4H7V8z"></path>
  </svg>
);

const StatsIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"></path>
  </svg>
);

const LogoutIcon = () => (
  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
  </svg>
);

interface SidebarProps {
  onLogout: () => void;
}

const Sidebar: React.FC<SidebarProps> = ({ onLogout }) => {
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-indigo-800 text-white' : 'text-gray-300 hover:bg-indigo-700 hover:text-white';
  };

  return (
    <div className="h-screen w-64 bg-indigo-900 text-white flex flex-col">
      <div className="p-5 border-b border-indigo-800">
        <h1 className="text-2xl font-bold">لوحة الإدارة</h1>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        <ul className="space-y-2 px-2">
          <li>
            <Link to="/admin" className={`flex items-center p-3 rounded-md ${isActive('/admin')}`}>
              <DashboardIcon />
              <span className="mr-3">الرئيسية</span>
            </Link>
          </li>
          <li>
            <Link to="/admin/users" className={`flex items-center p-3 rounded-md ${isActive('/admin/users')}`}>
              <UsersIcon />
              <span className="mr-3">المستخدمين</span>
            </Link>
          </li>
          <li>
            <Link to="/admin/posts" className={`flex items-center p-3 rounded-md ${isActive('/admin/posts')}`}>
              <PostsIcon />
              <span className="mr-3">المنشورات</span>
            </Link>
          </li>
          <li>
            <Link to="/admin/stats" className={`flex items-center p-3 rounded-md ${isActive('/admin/stats')}`}>
              <StatsIcon />
              <span className="mr-3">الإحصائيات</span>
            </Link>
          </li>
        </ul>
      </nav>
      
      <div className="p-4 border-t border-indigo-800">
        <button 
          onClick={onLogout}
          className="flex items-center p-3 w-full text-left rounded-md text-gray-300 hover:bg-indigo-700 hover:text-white"
        >
          <LogoutIcon />
          <span className="mr-3">تسجيل الخروج</span>
        </button>
      </div>
    </div>
  );
};

export default Sidebar;
