import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ClaimProfile = () => {
    const [orgs, setOrgs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');

    useEffect(() => {
        async function fetchOrgs() {
            try {
                const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/organizations/unclaimed`);
                const data = await res.json();
                setOrgs(data.organizations || []);
            } catch (err) {
                setError('Failed to load organizations');
            } finally {
                setLoading(false);
            }
        }

        fetchOrgs();
    }, []);

    const handleClaim = async (orgId) => {
        if (!token) {
            navigate('/signup');
            return;
        }
        try {
            const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/organizations/${orgId}/claim`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
                body: JSON.stringify({ verification_documents: {} }),
            });
            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.error || 'Claim failed');
            }
            const data = await res.json();
            // After claiming, steer user to their org dashboard
            navigate('/org/dashboard');
        } catch (err) {
            setError(err.message);
        }
    };

    if (loading) return <div className="p-6">Loading unclaimed organizations...</div>;

    return (
        <div className="p-6">
            <h2 className="text-2xl font-bold mb-4">Claim an Organization Profile</h2>
            {error && <div className="text-red-500 mb-4">{error}</div>}
            {orgs.length === 0 && <div>No unclaimed organizations available.</div>}
            <ul>
                {orgs.map((o) => (
                    <li key={o.id} className="mb-3 p-3 border rounded bg-white/5">
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="font-semibold">{o.organization_name}</div>
                                <div className="text-sm text-white/60">{o.city}</div>
                            </div>
                            <div>
                                <button
                                    className="btn btn-primary"
                                    onClick={() => handleClaim(o.id)}
                                >
                                    Claim
                                </button>
                            </div>
                        </div>
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ClaimProfile;
