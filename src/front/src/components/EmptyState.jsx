import React from 'react';

export default function EmptyState() {
  return (
    <div className="empty-state">
      <div style={{ fontSize: '64px', color: '#cbd5e1', marginBottom: '16px' }}>
        <i className="fas fa-inbox"></i>
      </div>
      <h2>No listings yet</h2>
      <p>There are no active listings. Check back later or create a new opportunity.</p>
    </div>
  );
}
