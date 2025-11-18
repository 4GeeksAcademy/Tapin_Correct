import React, { useState } from 'react';
import ForgotPassword from './ForgotPassword';
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function AuthForm({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('volunteer'); // 'volunteer' or 'organization'
  const [organizationName, setOrganizationName] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [showForgotPassword, setShowForgotPassword] = useState(false);

  async function handleSubmit(e) {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (mode === 'register' && password !== confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (mode === 'register' && role === 'organization' && !organizationName.trim()) {
      setError('Organization name is required');
      setLoading(false);
      return;
    }

    try {
      const endpoint = mode === 'login' ? '/login' : '/register';
      const payload = { email, password };

      // Add role and organization name for registration
      if (mode === 'register') {
        payload.role = role;
        if (role === 'organization') {
          payload.organization_name = organizationName;
        }
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || data.message || `HTTP ${res.status}`);
      }

      const data = await res.json();
      onLogin(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <>
      <div className="auth-form">
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            onClick={() => setMode('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            onClick={() => setMode('register')}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {mode === 'register' && (
            <div className="role-selector" style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: 'bold' }}>
                I am a:
              </label>
              <div className="btn-group w-100" role="group">
                <button
                  type="button"
                  className={`btn ${role === 'volunteer' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setRole('volunteer')}
                >
                  <i className="fas fa-hands-helping me-2"></i>
                  Volunteer
                </button>
                <button
                  type="button"
                  className={`btn ${role === 'organization' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setRole('organization')}
                >
                  <i className="fas fa-building me-2"></i>
                  Organization
                </button>
              </div>
            </div>
          )}

          {mode === 'register' && role === 'organization' && (
            <input
              type="text"
              placeholder="Organization Name"
              value={organizationName}
              onChange={(e) => setOrganizationName(e.target.value)}
              required
              className="form-input"
            />
          )}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="form-input"
          />

          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="form-input"
          />

          {mode === 'register' && (
            <input
              type="password"
              placeholder="Confirm Password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              className="form-input"
            />
          )}

          {error && <p className="error" style={{ marginBottom: 'var(--space-3)' }}>{error}</p>}

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '...' : mode === 'login' ? 'Login' : 'Register'}
          </button>

          {mode === 'login' && (
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="forgot-password-link"
            >
              Forgot Password?
            </button>
          )}
        </form>
      </div>

      {showForgotPassword && (
        <ForgotPassword
          onClose={() => setShowForgotPassword(false)}
          onSuccess={() => setShowForgotPassword(false)}
        />
      )}
    </>
  );
}
