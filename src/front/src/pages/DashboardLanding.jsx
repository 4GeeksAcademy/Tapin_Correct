import React, { useState } from 'react';
import logoTransparent from '@/assets/brand/logo-transparent.svg';
import AuthForm from '../components/AuthForm';

export default function DashboardLanding({ onLogin, onEnter, user }) {
  const [showAuth, setShowAuth] = useState(false);

  if (showAuth) {
    return (
      <div className="landing-root">
        <div className="landing-hero" style={{ maxWidth: '500px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
            <img
              src={logoTransparent}
              alt="Tapin logo"
              className="landing-logo"
              style={{ width: 220, height: 220, objectFit: 'contain' }}
            />
          </div>

          <AuthForm
            onLogin={(data) => {
              try {
                // Prefer tokens from response
                if (data?.access_token) {
                  localStorage.setItem('access_token', data.access_token);
                }
              } catch {}
              // Notify parent if provided
              if (typeof onLogin === 'function') {
                const user = data?.user || null;
                const token = data?.access_token || null;
                onLogin(user, token);
              }
              setShowAuth(false);
              if (typeof onEnter === 'function') onEnter();
            }}
          />

          <button
            onClick={() => setShowAuth(false)}
            style={{
              marginTop: '16px',
              background: 'none',
              border: 'none',
              color: '#666',
              cursor: 'pointer',
              textDecoration: 'underline',
              fontSize: '14px'
            }}
          >
            ← Back to home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="landing-root">
      <div className="landing-hero">
        <img src={logoTransparent} alt="Tapin logo" className="landing-logo" />
        <h1 className="landing-title">TapIn — connect your community</h1>
        <p className="landing-sub">
          Find volunteer opportunities to give back, or discover local services from small
          businesses and professionals. One platform to strengthen your community.
        </p>

        <div className="landing-cta-row">
          <button className="btn btn-primary landing-cta" onClick={() => setShowAuth(true)}>
            Get Started
          </button>
          <button className="btn btn-outline landing-cta" onClick={() => setShowAuth(true)}>
            Log In
          </button>
        </div>

        <ul className="landing-features">
          <li>🤝 Volunteer opportunities: Find meaningful ways to give back</li>
          <li>💼 Local services: Discover small businesses and professionals</li>
          <li>📍 Map view: Browse opportunities by location</li>
        </ul>

        <div className="landing-footer-note">Free to use • School Project</div>
      </div>
    </div>
  );
}
