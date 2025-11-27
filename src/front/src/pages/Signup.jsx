import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import GlassCard from '../components/GlassCard';

const Signup = () => {
    const navigate = useNavigate();
    const [userType, setUserType] = useState('volunteer'); // 'volunteer' or 'organization'
    const [formData, setFormData] = useState({ email: '', password: '', name: '' });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleSignup = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ ...formData, user_type: userType })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Signup failed');

            // Prefer access_token (newer API), but keep `token` for backward compatibility
            const accessToken = data.access_token || data.token || data.accessToken;
            if (accessToken) {
                localStorage.setItem('access_token', accessToken);
                localStorage.setItem('token', accessToken);
            }
            localStorage.setItem('user_type', userType);

            // Redirect based on role — organizations should claim profiles first
            navigate(userType === 'organization' ? '/claim' : '/dashboard');

        } catch (err) {
            setError(err.message);
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center p-4">
            <GlassCard className="w-full max-w-md p-8 animate-fadeIn">
                <h1 className="text-3xl font-bold text-center text-white mb-2">Join Tapin</h1>
                <p className="text-center text-white/60 mb-8">Start making an impact today.</p>

                {/* Role Toggle */}
                <div className="flex bg-white/10 p-1 rounded-lg mb-6">
                    <button
                        onClick={() => setUserType('volunteer')}
                        className={`flex-1 py-2 rounded-md text-sm font-bold transition ${userType === 'volunteer' ? 'bg-blue-600 text-white shadow-lg' : 'text-white/50 hover:text-white'}`}
                    >
                        Volunteer
                    </button>
                    <button
                        onClick={() => setUserType('organization')}
                        className={`flex-1 py-2 rounded-md text-sm font-bold transition ${userType === 'organization' ? 'bg-purple-600 text-white shadow-lg' : 'text-white/50 hover:text-white'}`}
                    >
                        Organization
                    </button>
                </div>

                {error && <div className="bg-red-500/20 border border-red-500/50 text-red-200 p-3 rounded mb-4 text-sm text-center">{error}</div>}

                <form onSubmit={handleSignup} className="space-y-4">
                    <div>
                        <label className="block text-sm text-white/70 mb-1">Full Name</label>
                        <input
                            required
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                            placeholder={userType === 'volunteer' ? "Jane Doe" : "Organization Name"}
                            value={formData.name}
                            onChange={e => setFormData({ ...formData, name: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-white/70 mb-1">Email Address</label>
                        <input
                            type="email" required
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                            placeholder="name@example.com"
                            value={formData.email}
                            onChange={e => setFormData({ ...formData, email: e.target.value })}
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-white/70 mb-1">Password</label>
                        <input
                            type="password" required
                            className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-blue-500 transition"
                            placeholder="••••••••"
                            value={formData.password}
                            onChange={e => setFormData({ ...formData, password: e.target.value })}
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={loading}
                        className={`w-full py-3 mt-2 rounded-lg font-bold text-white shadow-lg transition hover:scale-[1.02] active:scale-95 ${userType === 'volunteer' ? 'bg-gradient-to-r from-blue-600 to-blue-500' : 'bg-gradient-to-r from-purple-600 to-purple-500'
                            }`}
                    >
                        {loading ? 'Creating Account...' : 'Create Account'}
                    </button>
                </form>

                <div className="mt-6 text-center text-sm text-white/50">
                    Already have an account? <Link to="/login" className="text-blue-400 hover:text-blue-300 font-semibold">Log in</Link>
                </div>
            </GlassCard>
        </div>
    );
};

export default Signup;
