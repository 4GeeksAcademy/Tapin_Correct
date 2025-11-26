import React, { useState, useEffect } from 'react';
import GlassCard from '../components/GlassCard';
import { useNavigate } from 'react-router-dom';

const VolunteerProfile = () => {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const navigate = useNavigate();

    useEffect(() => {
        const fetchProfile = async () => {
            try {
                const token = localStorage.getItem('token');
                if (!token) return navigate('/login');

                const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/me`, {
                    headers: { Authorization: `Bearer ${token}` }
                });
                const data = await res.json();
                setProfile(data.profile);
                setFormData(data.profile);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchProfile();
    }, [navigate]);

    const handleSave = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/profile/volunteer`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(formData)
            });

            if (res.ok) {
                const data = await res.json();
                setProfile(data.profile);
                setIsEditing(false);
            }
        } catch (err) {
            console.error("Failed to save profile", err);
        }
    };

    if (loading) return <div className="text-center text-white mt-10">Loading Profile...</div>;

    return (
        <div className="max-w-4xl mx-auto p-4 text-white">
            {/* Header Card */}
            <GlassCard className="mb-6 flex flex-col md:flex-row items-center gap-6 p-8">
                <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white/20 shadow-lg">
                    <img
                        src={profile?.avatar_url || "https://via.placeholder.com/150"}
                        alt="Profile"
                        className="w-full h-full object-cover"
                    />
                </div>
                <div className="flex-1 text-center md:text-left">
                    {isEditing ? (
                        <div className="space-y-2">
                            <input
                                className="bg-white/10 border border-white/20 rounded px-3 py-1 w-full"
                                placeholder="First Name"
                                value={formData.first_name || ''}
                                onChange={e => setFormData({ ...formData, first_name: e.target.value })}
                            />
                            <input
                                className="bg-white/10 border border-white/20 rounded px-3 py-1 w-full"
                                placeholder="Last Name"
                                value={formData.last_name || ''}
                                onChange={e => setFormData({ ...formData, last_name: e.target.value })}
                            />
                        </div>
                    ) : (
                        <h1 className="text-3xl font-bold">{profile?.first_name} {profile?.last_name}</h1>
                    )}
                    <p className="text-white/70 mt-1">
                        {profile?.city || 'Location not set'} • {profile?.total_hours_volunteered || 0} Volunteer Hours
                    </p>

                    <button
                        onClick={() => isEditing ? handleSave() : setIsEditing(true)}
                        className="mt-4 px-6 py-2 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full font-semibold shadow-lg hover:scale-105 transition"
                    >
                        {isEditing ? 'Save Changes' : 'Edit Profile'}
                    </button>
                </div>
            </GlassCard>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* About Me */}
                <GlassCard className="p-6">
                    <h2 className="text-xl font-bold mb-4 border-b border-white/10 pb-2">About Me</h2>
                    {isEditing ? (
                        <textarea
                            className="w-full bg-white/10 border border-white/20 rounded p-3 min-h-[100px]"
                            value={formData.bio || ''}
                            onChange={e => setFormData({ ...formData, bio: e.target.value })}
                        />
                    ) : (
                        <p className="text-white/80 leading-relaxed">
                            {profile?.bio || "No bio yet. Tell organizations about yourself!"}
                        </p>
                    )}
                </GlassCard>

                {/* Skills & Interests */}
                <GlassCard className="p-6">
                    <h2 className="text-xl font-bold mb-4 border-b border-white/10 pb-2">Skills & Interests</h2>
                    <div className="mb-4">
                        <h3 className="text-sm text-white/60 mb-2">SKILLS</h3>
                        <div className="flex flex-wrap gap-2">
                            {(profile?.skills || []).map((skill, i) => (
                                <span key={i} className="px-3 py-1 bg-blue-500/30 rounded-full text-sm border border-blue-400/30">
                                    {skill}
                                </span>
                            ))}
                            {(!profile?.skills?.length) && <span className="text-white/40 italic">No skills listed</span>}
                        </div>
                    </div>
                    <div>
                        <h3 className="text-sm text-white/60 mb-2">INTERESTS</h3>
                        <div className="flex flex-wrap gap-2">
                            {(profile?.interests || []).map((interest, i) => (
                                <span key={i} className="px-3 py-1 bg-purple-500/30 rounded-full text-sm border border-purple-400/30">
                                    {interest}
                                </span>
                            ))}
                        </div>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
};

export default VolunteerProfile;
