import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ForgotPassword from './ForgotPassword';
import { API_URL } from '../lib/api';

export default function AuthForm({ onLogin }) {
  const [mode, setMode] = useState('login'); // 'login' or 'register'
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [userType, setUserType] = useState('volunteer'); // 'volunteer' or 'organization'
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

    if (mode === 'register' && userType === 'organization' && !organizationName.trim()) {
      setError('Organization name is required');
      setLoading(false);
      return;
    }

    try {
      const endpoint = mode === 'login' ? '/login' : '/register';
      const body = { email, password };

      // Add user_type and organization name for registration
      if (mode === 'register') {
        body.user_type = userType;
        if (userType === 'organization') {
          body.organization_name = organizationName;
        }
      }

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
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
      <div className="auth-form" data-testid="auth-form">
        {/* Mode Tabs */}
        <div className="auth-tabs">
          <button
            type="button"
            className={`auth-tab ${mode === 'login' ? 'active' : ''}`}
            data-testid="auth-tab-login"
            onClick={() => setMode('login')}
          >
            Login
          </button>
          <button
            type="button"
            className={`auth-tab ${mode === 'register' ? 'active' : ''}`}
            data-testid="auth-tab-register"
            onClick={() => setMode('register')}
          >
            Register
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          {/* User Type Selector (Register only) */}
          <AnimatePresence>
            {mode === 'register' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="form-group"
              >
                <label className="form-label">I am a:</label>
                <div className="radio-group">
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="userType"
                      value="volunteer"
                      checked={userType === 'volunteer'}
                      onChange={(e) => setUserType(e.target.value)}
                    />
                    <span>Volunteer</span>
                  </label>
                  <label className="radio-label">
                    <input
                      type="radio"
                      name="userType"
                      value="organization"
                      checked={userType === 'organization'}
                      onChange={(e) => setUserType(e.target.value)}
                    />
                    <span>Organization</span>
                  </label>
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Organization Name (Register + Organization only) */}
          <AnimatePresence>
            {mode === 'register' && userType === 'organization' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="form-group"
              >
                <input
                  id="organization-name"
                  type="text"
                  placeholder="Organization Name"
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  required
                  className="form-input"
                  autoComplete="organization"
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Email */}
          <div className="form-group">
            <input
              id="email"
              type="email"
              placeholder="Email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="form-input"
              autoComplete="email"
              data-testid="auth-email-input"
            />
          </div>

          {/* Password */}
          <div className="form-group">
            <input
              id="password"
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="form-input"
              autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
              data-testid="auth-password-input"
            />
          </div>

          {/* Confirm Password (Register only) */}
          <AnimatePresence>
            {mode === 'register' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="form-group"
              >
                <input
                  id="confirm-password"
                  type="password"
                  placeholder="Confirm Password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  className="form-input"
                  autoComplete="new-password"
                  data-testid="auth-confirm-password-input"
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error Message */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="alert alert-error mb-4"
              >
                {error}
              </motion.div>
            )}
          </AnimatePresence>

          {/* Submit Button */}
          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
            data-testid={mode === 'login' ? 'login-submit-btn' : 'register-submit-btn'}
            aria-label={mode === 'login' ? 'Submit login' : 'Submit registration'}
          >
            {mode === 'login' ? (loading ? 'Logging in...' : 'Log In') : loading ? 'Registering...' : 'Sign Up'}
          </button>

          {/* Forgot Password Link (Login only) */}
          {mode === 'login' && (
            <button
              type="button"
              onClick={() => setShowForgotPassword(true)}
              className="btn btn-ghost"
              style={{ width: '100%', marginTop: 'var(--space-3)' }}
            >
              Forgot Password?
            </button>
          )}
        </form>
      </div>

      {/* Forgot Password Modal */}
      <AnimatePresence>
        {showForgotPassword && (
          <ForgotPassword
            onClose={() => setShowForgotPassword(false)}
            onSuccess={() => setShowForgotPassword(false)}
          />
        )}
      </AnimatePresence>

      <style jsx>{`
        .auth-form {
          width: 100%;
          max-width: 400px;
          margin: 0 auto;
        }

        .auth-tabs {
          display: flex;
          gap: var(--space-2);
          margin-bottom: var(--space-6);
          border-bottom: 2px solid var(--border-light);
        }

        .auth-tab {
          flex: 1;
          padding: var(--space-3) var(--space-4);
          background: none;
          border: none;
          border-bottom: 2px solid transparent;
          color: var(--text-muted);
          font-size: var(--fs-base);
          font-weight: var(--fw-medium);
          cursor: pointer;
          transition: all var(--transition-fast);
          margin-bottom: -2px;
        }

        .auth-tab:hover {
          color: var(--text);
          background: var(--bg-light);
        }

        .auth-tab.active {
          color: var(--primary);
          border-bottom-color: var(--primary);
          font-weight: var(--fw-semibold);
        }

        .radio-group {
          display: flex;
          gap: var(--space-6);
        }

        .radio-label {
          display: flex;
          align-items: center;
          cursor: pointer;
          font-size: var(--fs-base);
          color: var(--text);
        }

        .radio-label input[type="radio"] {
          margin-right: var(--space-2);
          cursor: pointer;
          accent-color: var(--primary);
        }

        .radio-label:hover {
          color: var(--primary);
        }
      `}</style>
    </>
  );
}
