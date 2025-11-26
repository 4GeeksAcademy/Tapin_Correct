import React, { useState, useEffect } from 'react';

import { API_URL } from '../lib/api';

export default function ResetPasswordConfirm({ token: tokenFromProps = '' }) {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [token, setToken] = useState('');

  useEffect(() => {
    if (tokenFromProps) {
      setToken(tokenFromProps);
      return;
    }

    const params = new URLSearchParams(globalThis.location?.search || '');
    const queryToken = params.get('token');
    if (queryToken) {
      setToken(queryToken);
      return;
    }

    const path = globalThis.location?.pathname || '';
    const match = path.match(/\/reset-password\/confirm\/([^/]+)/);
    if (match) {
      setToken(match[1]);
      return;
    }

    setError('Invalid or missing reset token');
  }, [tokenFromProps]);

  async function handleSubmit(e) {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/reset-password/confirm/${token}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to reset password');
      }

      setSuccess(true);
      setTimeout(() => {
        window.location.href = '/';
      }, 2000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  if (!token && !error) {
    return <div>Loading...</div>;
  }

  return (
    <div className="reset-password-page">
      <div className="reset-password-card">
        <h1>Reset Your Password</h1>

        {error && !success && (
          <div className="error" role="alert">
            {error}
          </div>
        )}

        {success ? (
          <div className="success" role="alert">
            ✓ Password reset successful! Redirecting to login...
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="new-password">New Password</label>
              <input
                id="new-password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter new password"
                required
                minLength={6}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirm-password">Confirm Password</label>
              <input
                id="confirm-password"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Confirm new password"
                required
                minLength={6}
              />
            </div>

            <button type="submit" className="btn btn-primary" disabled={loading} style={{ width: '100%' }}>
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}
      </div>
    </div>
  );
}
