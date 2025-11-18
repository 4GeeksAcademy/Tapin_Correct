import React, { useState } from 'react';
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function LoginForm({ onLogin, onForgotPassword, mode = 'login' }) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState('volunteer'); // 'volunteer' or 'organization'
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      const url = mode === 'login' ? `${API_URL}/login` : `${API_URL}/register`;
      const body = { email, password };

      // Include user_type only during registration
      if (mode === 'register') {
        body.user_type = userType;
      }

      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || 'auth failed');
      onLogin && onLogin(data);
    } catch (error_) {
      setError(error_.message);
    }
  }

  return (
    <form onSubmit={submit} className="auth-form">
      {mode === 'register' && (
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontWeight: '500' }}>
            I am a:
          </label>
          <div style={{ display: 'flex', gap: '1rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name="userType"
                value="volunteer"
                checked={userType === 'volunteer'}
                onChange={(e) => setUserType(e.target.value)}
                style={{ marginRight: '0.5rem' }}
              />
              <span>Volunteer</span>
            </label>
            <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
              <input
                type="radio"
                name="userType"
                value="organization"
                checked={userType === 'organization'}
                onChange={(e) => setUserType(e.target.value)}
                style={{ marginRight: '0.5rem' }}
              />
              <span>Organization</span>
            </label>
          </div>
        </div>
      )}

      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        type="email"
        required
      />
      <input
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        type="password"
        required
      />
      <button type="submit" className="chip">
        {mode === 'login' ? 'Login' : 'Register'}
      </button>
      {mode === 'login' && onForgotPassword && (
        <button
          type="button"
          className="link-button"
          onClick={onForgotPassword}
          style={{ fontSize: '0.85rem', marginTop: '4px' }}
        >
          Forgot Password?
        </button>
      )}
      {error && <div className="error">{error}</div>}
    </form>
  );
}
