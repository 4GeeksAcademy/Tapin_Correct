import React from 'react';
import clsx from 'clsx';
import './GlassCard.css';

const GlassCard = ({ children, className = '', hover = false, onClick }) => {
  return (
    <div
      onClick={onClick}
      className={clsx(
        'glass-card', // This applies the CSS class from index.css
        hover && 'cursor-pointer hover:-translate-y-1 hover:bg-white/10',
        className
      )}
    >
      {children}
    </div>
  );
};

export default GlassCard;
