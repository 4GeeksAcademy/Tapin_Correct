import React from 'react';

/**
 * Glassmorphism Card Component
 *
 * Modern glass-effect card with blur and transparency
 */
export default function GlassCard({ children, className = '', style = {}, hover = true }) {
  return (
    <div className={`glass-card ${hover ? 'glass-card-hover' : ''} ${className}`} style={style}>
      {children}

      <style jsx>{`
        .glass-card {
          background: rgba(255, 255, 255, 0.1);
          backdrop-filter: blur(10px);
          -webkit-backdrop-filter: blur(10px);
          border-radius: 20px;
          border: 1px solid rgba(255, 255, 255, 0.2);
          box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
          padding: 20px;
          transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .glass-card-hover:hover {
          transform: translateY(-4px);
          box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
          background: rgba(255, 255, 255, 0.15);
          border-color: rgba(255, 255, 255, 0.3);
        }

        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
          .glass-card {
            background: rgba(20, 20, 20, 0.7);
            border-color: rgba(255, 255, 255, 0.1);
          }

          .glass-card-hover:hover {
            background: rgba(30, 30, 30, 0.8);
          }
        }

        /* Gradient backgrounds for special cards */
        .glass-card.glass-card-gradient {
          background: linear-gradient(
            135deg,
            rgba(102, 126, 234, 0.2) 0%,
            rgba(118, 75, 162, 0.2) 100%
          );
        }

        .glass-card.glass-card-gradient-success {
          background: linear-gradient(
            135deg,
            rgba(46, 204, 113, 0.2) 0%,
            rgba(39, 174, 96, 0.2) 100%
          );
        }

        .glass-card.glass-card-gradient-warning {
          background: linear-gradient(
            135deg,
            rgba(243, 156, 18, 0.2) 0%,
            rgba(230, 126, 34, 0.2) 100%
          );
        }

        /* Micro-interaction: shine effect */
        .glass-card::before {
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.2),
            transparent
          );
          transition: left 0.5s;
        }

        .glass-card:hover::before {
          left: 100%;
        }
      `}</style>
    </div>
  );
}
