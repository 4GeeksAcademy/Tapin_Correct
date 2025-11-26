import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import BrandLogo from './BrandLogo';

export default function Navigation({ user, onLogout }) {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path) => location.pathname === path;

  const navLinks = [
    { path: '/', label: 'Home', icon: '🏠' },
    { path: '/discover', label: 'Discover', icon: '🎉' },
    { path: '/dashboard', label: 'Dashboard', icon: '📊', authRequired: true },
  ];

  return (
    <motion.nav
      className="nav-container"
      initial={{ y: -100, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
    >
      <div className="nav-content">
        {/* Brand - show only the logo icon (no duplicate text) */}
        <Link to="/" className="nav-brand" aria-label="Tapin home">
          <BrandLogo width={56} variant="icon" alt="Tapin" />
        </Link>

        {/* Desktop Navigation */}
        <ul className="nav-links">
          {navLinks.map((link) => {
            if (link.authRequired && !user) return null;
            return (
              <li key={link.path}>
                <Link
                  to={link.path}
                  className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
                >
                  <span style={{ marginRight: '6px' }}>{link.icon}</span>
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* User Actions */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--space-4)' }}>
          {user ? (
            <>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                gap: 'var(--space-3)',
                padding: 'var(--space-2) var(--space-4)',
                background: 'var(--primary-pale)',
                borderRadius: 'var(--radius-full)',
              }}>
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'var(--fw-bold)',
                  fontSize: 'var(--fs-sm)',
                }}>
                  {user.email?.[0]?.toUpperCase() || '?'}
                </div>
                <span style={{
                  fontSize: 'var(--fs-sm)',
                  fontWeight: 'var(--fw-medium)',
                  color: 'var(--text)',
                }}>
                  {user.email?.split('@')[0] || 'User'}
                </span>
              </div>
              <button
                onClick={onLogout}
                className="btn btn-ghost btn-sm"
                data-testid="logout-btn"
              >
                Logout
              </button>
            </>
          ) : (
            <Link to="/?auth=true" className="btn btn-primary btn-sm">
              Get Started
            </Link>
          )}
        </div>

        {/* Mobile Menu Toggle */}
        <button
          className="mobile-menu-toggle"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label="Toggle menu"
          style={{
            display: 'none',
            background: 'none',
            border: 'none',
            fontSize: 'var(--fs-2xl)',
            cursor: 'pointer',
            padding: 'var(--space-2)',
          }}
        >
          {mobileMenuOpen ? '✕' : '☰'}
        </button>
      </div>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <motion.div
          className="mobile-menu"
          initial={{ height: 0, opacity: 0 }}
          animate={{ height: 'auto', opacity: 1 }}
          exit={{ height: 0, opacity: 0 }}
          style={{
            background: 'var(--surface)',
            borderTop: '1px solid var(--border-light)',
            padding: 'var(--space-4) var(--space-6)',
          }}
        >
          <ul style={{ listStyle: 'none', margin: 0, padding: 0 }}>
            {navLinks.map((link) => {
              if (link.authRequired && !user) return null;
              return (
                <li key={link.path} style={{ marginBottom: 'var(--space-3)' }}>
                  <Link
                    to={link.path}
                    className={`nav-link ${isActive(link.path) ? 'active' : ''}`}
                    onClick={() => setMobileMenuOpen(false)}
                    style={{ display: 'block', width: '100%' }}
                  >
                    <span style={{ marginRight: '8px' }}>{link.icon}</span>
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </motion.div>
      )}

      <style jsx>{`
        @media (max-width: 768px) {
          .nav-links {
            display: none !important;
          }

          .mobile-menu-toggle {
            display: block !important;
          }
        }
      `}</style>
    </motion.nav>
  );
}
