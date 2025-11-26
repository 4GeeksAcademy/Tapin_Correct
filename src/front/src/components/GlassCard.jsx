import React from 'react';
import './GlassCard.css';

/**
 * Glassmorphism Card Component
 *
 * Modern glass-effect card with blur and transparency
 * Uses design system CSS variables for consistency
 */
export default function GlassCard({ children, className = '', style = {}, hover = true, variant = 'default' }) {
  return (
    <div
      className={`glass-card glass-card-${variant} ${hover ? 'glass-card-hover' : ''} ${className}`}
      style={style}
    >
      {children}
    </div>
  );
}
