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
                  <span className="nav-icon">{link.icon}</span>
                  {link.label}
                </Link>
              </li>
            );
          })}
        </ul>

        {/* User Actions */}
        <div className="nav-actions">
          {user ? (
            <>
              <div className="nav-user-chip">
                <div className="nav-avatar">{user.email?.[0]?.toUpperCase() || '?'}</div>
                <span className="nav-username">{user.email?.split('@')[0] || 'User'}</span>
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
        >
          <ul className="mobile-menu-list">
            {navLinks.map((link) => {
              if (link.authRequired && !user) return null;
              return (
                <li key={link.path} className="mobile-menu-item">
                  <Link
                    to={link.path}
                    className={`nav-link mobile-menu-link ${isActive(link.path) ? 'active' : ''}`}
                    onClick={() => setMobileMenuOpen(false)}
                  >
                    <span className="nav-icon nav-icon-mobile">{link.icon}</span>
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </motion.div>
      )}


    </motion.nav>
  );
}
