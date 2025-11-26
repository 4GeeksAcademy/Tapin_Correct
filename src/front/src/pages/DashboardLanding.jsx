import React, { useState } from 'react';
import pandaWaving from '@/assets/mascot/panda-waving.svg';
import volunteerIcon from '@/assets/icons/volunteer.svg';
import organizationIcon from '@/assets/icons/organization.svg';
import locationIcon from '@/assets/icons/location.svg';
import AuthForm from '../components/AuthForm';
import HeroVideo from '../components/HeroVideo';

export default function DashboardLanding({ onLogin, onEnter, user }) {
  const [showAuth, setShowAuth] = useState(false);

  if (showAuth) {
    return (
      <div className="landing-root">
        <div className="landing-hero" style={{ maxWidth: '500px' }}>
          <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 24 }}>
            <img
              src={pandaWaving}
              alt="Tapin panda mascot waving"
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
              } catch { }
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
        <img src={pandaWaving} alt="Tapin panda mascot waving" className="landing-logo" />
        <h1 className="landing-title">TapIn — connect your community</h1>
        <p className="landing-sub">
          Find volunteer opportunities to give back, or discover local services from small
          businesses and professionals. One platform to strengthen your community.
        </p>

        <div className="landing-cta-row">
          <button
            className="btn btn-primary landing-cta"
            onClick={() => setShowAuth(true)}
            data-testid="get-started-btn"
            aria-label="Get started with registration"
          >
            Get Started
          </button>
          <button
            className="btn btn-outline landing-cta"
            onClick={() => setShowAuth(true)}
            data-testid="login-btn"
            aria-label="Log in to your account"
          >
            Log In
          </button>
        </div>

        <HeroVideo />

        <ul className="landing-features">
          <li><img src={volunteerIcon} alt="" className="icon" /> Volunteer opportunities: Find meaningful ways to give back</li>
          <li><img src={organizationIcon} alt="" className="icon" /> Local services: Discover small businesses and professionals</li>
          <li><img src={locationIcon} alt="" className="icon" /> Map view: Browse opportunities by location</li>
        </ul>

        <div className="landing-footer-note">Free to use • School Project</div>
      </div>
    </div>
  );
}
