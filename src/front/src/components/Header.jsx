import React from 'react';
import logo from '../assets/brand/logo-new.svg';
import icon from '../assets/brand/icon.svg';

export default function Header({ user, onLogout }) {
  return (
    <header className="app-header">
      <div
        className="header-row"
        style={{
          display: 'grid',
          gridTemplateColumns: '1fr auto 1fr',
          alignItems: 'center',
        }}
      >
        <div className="brand" style={{ gridColumn: 2, justifySelf: 'center', textAlign: 'center' }}>
          <img
            src={logo}
            alt="Tapin - Volunteer Connect"
            style={{
              height: '60px',
              width: 'auto',
              maxWidth: '240px',
              display: 'block',
              margin: '0 auto'
            }}
            className="logo-desktop"
          />
          <img
            src={icon}
            alt="Tapin"
            style={{
              height: '48px',
              width: '48px',
              display: 'none',
              margin: '0 auto'
            }}
            className="logo-mobile"
          />
        </div>

        {user && (
          <div
            className="header-actions"
            style={{ display: 'flex', alignItems: 'center', gap: 8, gridColumn: 3, justifySelf: 'end' }}
          >
            <span style={{ color: '#475569' }}>Hi, {user.email}</span>
            <button
              className="chip"
              onClick={() => {
                try { localStorage.removeItem('access_token'); } catch {}
                if (typeof onLogout === 'function') onLogout();
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>

      <div className="search-row">
        <input
          className="search"
          placeholder="Search volunteer opportunities, services, or location"
        />
      </div>
    </header>
  );
}
