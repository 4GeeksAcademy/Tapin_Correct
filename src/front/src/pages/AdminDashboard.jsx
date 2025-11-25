import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function AdminDashboard() {
    const [token, setToken] = useState(localStorage.getItem('admin_token') || '');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [pending, setPending] = useState([]);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');

    async function handleLogin(e) {
        e.preventDefault();
        setError('');
        setSuccess('');
        try {
            const res = await fetch(`${API_URL}/admin/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password }),
            });
            const data = await res.json();
            if (!res.ok) throw new Error(data.error || 'Login failed');
            setToken(data.access_token);
            localStorage.setItem('admin_token', data.access_token);
            setSuccess('Login successful!');
        } catch (err) {
            setError(err.message);
        }
    }

    async function fetchPending() {
        if (!token) return;
        try {
            const res = await fetch(`${API_URL}/admin/pending`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            const data = await res.json();
            if (res.ok) setPending(data.pending_admins || []);
        } catch { }
    }

    async function approve(emailToApprove) {
        if (!token) return;
        try {
            const res = await fetch(`${API_URL}/admin/approve`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${token}`,
                },
                body: JSON.stringify({ email: emailToApprove }),
            });
            const data = await res.json();
            if (res.ok) {
                setSuccess(`Approved: ${emailToApprove}`);
                setPending(pending.filter(e => e !== emailToApprove));
            } else {
                setError(data.error || 'Approval failed');
            }
        } catch (err) {
            setError(err.message);
        }
    }

    async function triggerEnrichment() {
        if (!token) return;
        try {
            const res = await fetch(`${API_URL}/admin/enrich_organizations`, {
                method: 'POST',
                headers: { Authorization: `Bearer ${token}` },
                body: JSON.stringify({ results: [] }), // Replace with actual results if needed
            });
            const data = await res.json();
            if (res.ok) setSuccess('Enrichment triggered!');
            else setError(data.error || 'Enrichment failed');
        } catch (err) {
            setError(err.message);
        }
    }

    useEffect(() => {
        fetchPending();
    }, [token]);

    if (!token) {
        return (
            <div className="admin-login">
                <h2>Admin Login</h2>
                <form onSubmit={handleLogin}>
                    <input
                        type="email"
                        placeholder="Admin Email"
                        value={email}
                        onChange={e => setEmail(e.target.value)}
                        required
                    />
                    <input
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={e => setPassword(e.target.value)}
                        required
                    />
                    <button type="submit">Login</button>
                </form>
                {error && <p style={{ color: 'red' }}>{error}</p>}
                {success && <p style={{ color: 'green' }}>{success}</p>}
            </div>
        );
    }

    return (
        <div className="admin-dashboard">
            <h2>Admin Dashboard</h2>
            {success && <p style={{ color: 'green' }}>{success}</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <button onClick={triggerEnrichment}>Trigger Organization Enrichment</button>
            <h3>Pending Admin Requests</h3>
            <ul>
                {pending.length === 0 && <li>No pending requests.</li>}
                {pending.map(email => (
                    <li key={email}>
                        {email}
                        <button onClick={() => approve(email)} style={{ marginLeft: 8 }}>
                            Approve
                        </button>
                    </li>
                ))}
            </ul>
        </div>
    );
}
