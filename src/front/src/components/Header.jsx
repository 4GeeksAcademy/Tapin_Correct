import React from 'react';
import BrandLogo from './BrandLogo';
import searchIcon from '@/assets/icons/search.svg';

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
          <BrandLogo />
        </div>

        {user && (
          <div
            className="header-actions"
            style={{ display: 'flex', alignItems: 'center', gap: 8, gridColumn: 3, justifySelf: 'end' }}
          >            <span style={{ color: '#475569' }}>Hi, {user.email}</span>
            <button
              className="chip"
              onClick={() => {
                try { localStorage.removeItem('access_token'); } catch { }
                if (typeof onLogout === 'function') onLogout();
              }}
            >
              Logout
            </button>
          </div>
        )}
      </div>

      <div className="search-row" style={{ position: 'relative' }}>
        <img src={searchIcon} alt="Search" className="icon" style={{ position: 'absolute', left: 16, top: '50%', transform: 'translateY(-50%)', width: 24, height: 24 }} />
        <input
          className="search"
          placeholder="Search volunteer opportunities, services, or location"
          style={{ paddingLeft: 48 }}
        />
      </div>
    </header>
  );
}
