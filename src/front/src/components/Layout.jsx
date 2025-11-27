import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { FaHome, FaSearch, FaUser, FaCog, FaSignOutAlt, FaBuilding } from 'react-icons/fa';

const Layout = ({ children }) => {
    const navigate = useNavigate();
    const location = useLocation();
    const isOrg = localStorage.getItem('user_type') === 'organization';

    // Hide layout on public pages
    if (['/', '/login', '/signup', '/claim'].includes(location.pathname)) {
        return <div className="min-h-screen">{children}</div>;
    }

    const menuItems = isOrg
        ? [
            { icon: <FaHome />, label: 'Dashboard', path: '/org/dashboard' },
            { icon: <FaBuilding />, label: 'My Events', path: '/org/events' },
            { icon: <FaUser />, label: 'Volunteers', path: '/org/volunteers' },
        ]
        : [
            { icon: <FaHome />, label: 'Dashboard', path: '/dashboard' },
            { icon: <FaSearch />, label: 'Discover', path: '/events' },
            { icon: <FaUser />, label: 'Profile', path: '/profile' },
        ];

    return (
        <div className="flex min-h-screen bg-transparent">
            {/* Desktop Sidebar */}
            <aside className="hidden md:flex flex-col w-64 h-screen sticky top-0 border-r border-white/10 bg-black/20 backdrop-blur-xl p-6">
                <h1 className="text-2xl font-bold mb-10 bg-gradient-to-r from-blue-400 to-purple-500 bg-clip-text text-transparent">
                    Tapin.
                </h1>

                <nav className="flex-1 space-y-2">
                    {menuItems.map((item) => (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            className={`w-full flex items-center gap-4 px-4 py-3 rounded-xl transition-all ${location.pathname === item.path
                                    ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/20'
                                    : 'text-white/60 hover:bg-white/10 hover:text-white'
                                }`}
                        >
                            <span className="text-lg">{item.icon}</span>
                            <span className="font-medium">{item.label}</span>
                        </button>
                    ))}
                </nav>

                <button
                    onClick={() => { localStorage.clear(); navigate('/login'); }}
                    className="flex items-center gap-4 px-4 py-3 text-red-400 hover:bg-red-500/10 rounded-xl transition mt-auto"
                >
                    <FaSignOutAlt />
                    <span>Logout</span>
                </button>
            </aside>

            {/* Main Content Area */}
            <main className="flex-1 p-6 md:p-10 overflow-y-auto">
                {children}
            </main>

            {/* Mobile Bottom Nav */}
            <div className="md:hidden fixed bottom-0 left-0 right-0 bg-[#0f172a]/95 backdrop-blur-xl border-t border-white/10 px-6 py-4 flex justify-between z-50">
                {menuItems.map((item) => (
                    <button
                        key={item.path}
                        onClick={() => navigate(item.path)}
                        className={`flex flex-col items-center gap-1 ${location.pathname === item.path ? 'text-blue-400' : 'text-white/50'
                            }`}
                    >
                        <span className="text-xl">{item.icon}</span>
                        <span className="text-[10px] font-medium">{item.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default Layout;
