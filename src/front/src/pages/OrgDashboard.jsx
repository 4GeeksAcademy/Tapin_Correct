import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import { useNavigate } from 'react-router-dom';

const OrgDashboard = () => {
    const [orgProfile, setOrgProfile] = useState(null);
    const [stats, setStats] = useState({ events: 0, volunteers: 0, views: 0 });
    const navigate = useNavigate();

    useEffect(() => {
        // Fetch Org Data
        const fetchOrgData = async () => {
            const token = localStorage.getItem('token');
            // Mock data fetching - replace with real endpoints
            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/me`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            const data = await res.json();
            setOrgProfile(data.profile);

            // Set dummy stats for demo
            setStats({ events: 5, volunteers: 128, views: 4500 });
        };
        fetchOrgData();
    }, []);

    return (
        <div className="max-w-6xl mx-auto p-6 text-white">
            <header className="mb-8 flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold mb-2">Organization Dashboard</h1>
                    <p className="text-white/60">Welcome back, {orgProfile?.organization_name || 'Admin'}</p>
                </div>
                <button
                    onClick={() => navigate('/org/events/create')}
                    className="px-6 py-3 bg-green-500 hover:bg-green-600 rounded-lg font-bold shadow-lg transition flex items-center gap-2"
                >
                    + Create New Event
                </button>
            </header>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <GlassCard className="p-6 text-center hover:bg-white/5 transition cursor-pointer">
                    <div className="text-4xl font-bold text-blue-400 mb-1">{stats.events}</div>
                    <div className="text-white/60 uppercase text-sm tracking-wide">Active Events</div>
                </GlassCard>
                <GlassCard className="p-6 text-center hover:bg-white/5 transition cursor-pointer">
                    <div className="text-4xl font-bold text-purple-400 mb-1">{stats.volunteers}</div>
                    <div className="text-white/60 uppercase text-sm tracking-wide">Registered Volunteers</div>
                </GlassCard>
                <GlassCard className="p-6 text-center hover:bg-white/5 transition cursor-pointer">
                    <div className="text-4xl font-bold text-pink-400 mb-1">{stats.views}</div>
                    <div className="text-white/60 uppercase text-sm tracking-wide">Total Views</div>
                </GlassCard>
            </div>

            {/* Main Content Area */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Events List */}
                <div className="lg:col-span-2">
                    <GlassCard className="h-full">
                        <div className="p-6 border-b border-white/10 flex justify-between items-center">
                            <h2 className="text-xl font-bold">Your Events</h2>
                            <span className="text-sm text-blue-400 cursor-pointer">View All</span>
                        </div>
                        <div className="p-6 space-y-4">
                            {/* Event Item Mockup */}
                            {[1, 2, 3].map((_, i) => (
                                <div key={i} className="flex items-center gap-4 p-4 bg-white/5 rounded-lg hover:bg-white/10 transition">
                                    <div className="w-16 h-16 bg-gray-700 rounded-md overflow-hidden">
                                        <img src={`https://source.unsplash.com/random/100x100?sig=${i}`} alt="Event" className="w-full h-full object-cover" />
                                    </div>
                                    <div className="flex-1">
                                        <h3 className="font-bold">Community Beach Cleanup</h3>
                                        <p className="text-sm text-white/60">Nov 24 • 15/20 Volunteers</p>
                                    </div>
                                    <div className="flex gap-2">
                                        <button className="text-xs bg-blue-500/20 text-blue-300 px-3 py-1 rounded border border-blue-500/30">Edit</button>
                                        <button className="text-xs bg-white/10 text-white px-3 py-1 rounded border border-white/20">Stats</button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </GlassCard>
                </div>

                {/* Verification Status / Quick Actions */}
                <div className="space-y-6">
                    <GlassCard className="p-6 border-l-4 border-yellow-400">
                        <h3 className="font-bold text-lg mb-2">Verification Status</h3>
                        <div className="flex items-center gap-2 mb-4">
                            <span className="w-3 h-3 rounded-full bg-yellow-400 animate-pulse"></span>
                            <span className="text-yellow-400 font-semibold">Pending Review</span>
                        </div>
                        <p className="text-sm text-white/70 mb-4">
                            Your documents are being reviewed by our admin team. Full features will unlock upon approval.
                        </p>
                        <button className="w-full py-2 bg-white/10 hover:bg-white/20 rounded text-sm font-semibold transition">
                            Upload Documents
                        </button>
                    </GlassCard>

                    <GlassCard className="p-6">
                        <h3 className="font-bold text-lg mb-4">Quick Actions</h3>
                        <div className="space-y-2">
                            <button className="w-full text-left px-4 py-3 bg-white/5 hover:bg-white/10 rounded transition flex items-center gap-3">
                                <span>📩</span> Check Messages <span className="ml-auto bg-red-500 text-xs px-2 py-0.5 rounded-full">3</span>
                            </button>
                            <button className="w-full text-left px-4 py-3 bg-white/5 hover:bg-white/10 rounded transition flex items-center gap-3">
                                <span>🔍</span> Browse Volunteers
                            </button>
                            <button className="w-full text-left px-4 py-3 bg-white/5 hover:bg-white/10 rounded transition flex items-center gap-3">
                                <span>⚙️</span> Organization Settings
                            </button>
                        </div>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
};

export default OrgDashboard;
