import { useEffect, useState } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import {
  LayoutDashboard,
  FileText,
  Upload,
  Calculator,
  LogOut,
  GraduationCap,
  Shield,
  Menu,
  X,
  Moon,
  Sun,
} from 'lucide-react';
import { cn } from '../lib/utils';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

export default function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [isMobileNavOpen, setIsMobileNavOpen] = useState(false);

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

  const navItems = getNavItems();

  useEffect(() => {
    setIsMobileNavOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        setIsMobileNavOpen(false);
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, []);

  const SidebarContent = ({ mobile = false }: { mobile?: boolean }) => (
    <>
      <div className="p-6 flex items-center justify-between gap-3 border-b border-neutral-100 dark:border-neutral-800">
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-emerald-500 flex items-center justify-center text-white">
            <GraduationCap size={20} />
          </div>
          <span className="font-semibold text-lg tracking-tight">EduLend</span>
        </div>

        {mobile && (
          <button
            onClick={() => setIsMobileNavOpen(false)}
            className="p-2 rounded-lg hover:bg-neutral-100"
            aria-label="Close navigation"
          >
            <X size={18} />
          </button>
        )}
      </div>

      <div className="p-4 border-b border-neutral-100 dark:border-neutral-800">
        <div className="text-xs text-neutral-500 uppercase tracking-wider mb-1">Welcome</div>
        <div className="font-medium text-sm break-words">{user?.full_name}</div>
        <div className="text-xs text-neutral-500 capitalize">{user?.user_type}</div>
      </div>

      <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          const Icon = item.icon;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={cn(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-neutral-900 text-white shadow-md'
                  : 'text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900'
              )}
            >
              <Icon size={18} className={isActive ? 'text-emerald-400' : 'text-neutral-400'} />
              {item.label}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-neutral-100 dark:border-neutral-800 space-y-2">
        <button
          onClick={toggleTheme}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-xl text-sm font-medium text-neutral-600 hover:bg-neutral-100 hover:text-neutral-900 transition-colors"
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
          {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
        </button>

        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2.5 w-full rounded-xl text-sm font-medium text-neutral-600 hover:bg-red-50 hover:text-red-600 transition-colors"
        >
          <LogOut size={18} />
          Sign Out
        </button>
      </div>
    </>
  );

  return (
    <div className="min-h-screen bg-neutral-50 text-neutral-900 font-sans">
      <header className="lg:hidden sticky top-0 z-30 bg-white/95 backdrop-blur border-b border-neutral-200 px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <button
            onClick={() => setIsMobileNavOpen(true)}
            className="p-2 rounded-lg border border-neutral-200 hover:bg-neutral-100"
            aria-label="Open navigation"
          >
            <Menu size={18} />
          </button>
          <div className="w-7 h-7 rounded-lg bg-emerald-500 flex items-center justify-center text-white">
            <GraduationCap size={16} />
          </div>
          <span className="font-semibold tracking-tight">EduLend</span>
        </div>

        <button
          onClick={toggleTheme}
          className="p-2 rounded-lg border border-neutral-200 hover:bg-neutral-100"
          aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
        >
          {theme === 'dark' ? <Sun size={18} /> : <Moon size={18} />}
        </button>
      </header>

      <div className="flex min-h-[calc(100vh-61px)] lg:min-h-screen">
        <aside className="hidden lg:flex w-64 shrink-0 bg-white border-r border-neutral-200 flex-col">
          <SidebarContent />
        </aside>

        {isMobileNavOpen && (
          <>
            <button
              type="button"
              className="lg:hidden fixed inset-0 z-40 bg-neutral-900/40"
              onClick={() => setIsMobileNavOpen(false)}
              aria-label="Close navigation overlay"
            />
            <motion.aside
              initial={{ x: -280 }}
              animate={{ x: 0 }}
              exit={{ x: -280 }}
              transition={{ type: 'tween', duration: 0.2 }}
              className="lg:hidden fixed left-0 top-0 z-50 h-full w-72 max-w-[84vw] bg-white border-r border-neutral-200 flex flex-col"
            >
              <SidebarContent mobile />
            </motion.aside>
          </>
        )}

        <main className="flex-1 overflow-x-hidden overflow-y-auto">
          <div className="p-4 sm:p-6 lg:p-8 max-w-6xl mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
