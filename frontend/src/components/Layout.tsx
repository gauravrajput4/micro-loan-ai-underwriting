import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { LayoutDashboard, FileText, Upload, Calculator, LogOut, GraduationCap, Shield } from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();

  const getNavItems = () => {
    const baseItems = [
      { path: '/dashboard', label: 'My Dashboard', icon: LayoutDashboard },
      { path: '/calculator', label: 'EMI Calculator', icon: Calculator },
    ];

    if (user?.user_type === 'admin') {
      return [
        { path: '/admin', label: 'Admin Dashboard', icon: Shield },
        ...baseItems,
      ];
    }

    return [
      ...baseItems,
      { path: '/apply', label: 'Apply for Loan', icon: FileText },
      { path: '/upload', label: 'Bank Statement', icon: Upload },
    ];
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-neutral-50 text-neutral-900 font-sans">
      {/* Sidebar */}
      <motion.aside 
        initial={{ x: -250 }}
        animate={{ x: 0 }}
        className="w-64 bg-white border-r border-neutral-200 flex flex-col"
      >
        <div className="p-6 flex items-center gap-3 border-b border-neutral-100">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-white">
            <GraduationCap size={20} />
          </div>
          <span className="font-semibold text-lg tracking-tight">EduLend</span>
        </div>
        
        <div className="p-4 border-b border-neutral-100">
          <div className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Welcome</div>
          <div className="font-medium text-sm">{user?.full_name}</div>
          <div className="text-xs text-neutral-500 capitalize">{user?.user_type}</div>
        </div>
        
        <nav className="flex-1 p-4 space-y-1">
          {getNavItems().map((item) => {
            const isActive = location.pathname === item.path;
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={cn(
                  "flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200",
                  isActive 
                    ? "bg-neutral-900 text-white shadow-md" 
                    : "text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900"
                )}
              >
                <Icon size={18} className={isActive ? "text-emerald-400" : "text-neutral-400"} />
                {item.label}
              </Link>
            );
          })}
        </nav>

        <div className="p-4 border-t border-neutral-100">
          <button 
            onClick={handleLogout}
            className="flex items-center gap-3 px-3 py-2.5 w-full rounded-xl text-sm font-medium text-neutral-600 hover:bg-red-50 hover:text-red-600 transition-colors"
          >
            <LogOut size={18} />
            Sign Out
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8 max-w-6xl mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
