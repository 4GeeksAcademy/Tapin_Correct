import React, { useState } from 'react';
import GlassCard from './GlassCard';

const EventSwiper = ({ events = [], onSwipe = () => { } }) => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [direction, setDirection] = useState(null);

  const handleSwipe = (dir) => {
    if (currentIndex >= events.length) return;
    setDirection(dir);

    setTimeout(() => {
      const ev = events[currentIndex];
      try { onSwipe(ev, dir); } catch (e) { console.error(e); }
      setCurrentIndex((prev) => prev + 1);
      setDirection(null);
    }, 300);
  };

  if (!events || events.length === 0 || currentIndex >= events.length) {
    return (
      <div style={{ textAlign: 'center', padding: '3rem', opacity: 0.9 }}>
        <h3>🎉 All caught up!</h3>
        <p>Check back later for more events.</p>
      </div>
    );
  }

  const currentEvent = events[currentIndex];
  const nextEvent = events[currentIndex + 1];

  return (
    <div style={{ position: 'relative', height: '400px', maxWidth: '100%', perspective: '1000px' }}>
      {nextEvent && (
        <GlassCard
          style={{
            position: 'absolute',
            top: 0, left: 0, width: '100%', height: '100%',
            transform: 'scale(0.95) translateY(10px)',
            opacity: 0.6,
            zIndex: 1,
            filter: 'blur(1px)'
          }}
        >
          <div style={{ height: '200px', background: '#222', borderRadius: '12px', marginBottom: '1rem', overflow: 'hidden' }}>
            <img src={nextEvent.image || nextEvent.image_url || "https://via.placeholder.com/400x200?text=Event"} alt="Next" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          </div>
          <h3 style={{ color: 'white' }}>{nextEvent.title}</h3>
        </GlassCard>
      )}

      <GlassCard
        style={{
          position: 'absolute',
          top: 0, left: 0, width: '100%', height: '100%',
          zIndex: 2,
          cursor: 'grab',
          transition: 'transform 0.3s ease, opacity 0.3s ease',
          transform: direction === 'left' ? 'translateX(-150%) rotate(-20deg)' : direction === 'right' ? 'translateX(150%) rotate(20deg)' : 'translateX(0) rotate(0)',
          opacity: direction ? 0 : 1,
          display: 'flex',
          flexDirection: 'column'
        }}
      >
        <div style={{ height: '200px', background: '#222', borderRadius: '12px', marginBottom: '1rem', overflow: 'hidden', position: 'relative' }}>
          <img src={currentEvent.image || currentEvent.image_url || "https://via.placeholder.com/400x200?text=Event"} alt={currentEvent.title} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
          <div style={{ position: 'absolute', top: 10, right: 10, background: 'rgba(0,0,0,0.5)', padding: '4px 8px', borderRadius: '4px', fontSize: '0.8rem', color: 'white' }}>
            {currentEvent.category}
          </div>
        </div>

        <h3 style={{ marginBottom: '0.5rem', color: 'white' }}>{currentEvent.title}</h3>
        <p style={{ fontSize: '0.9rem', opacity: 0.85, marginBottom: '1rem', color: 'var(--text-muted)' }}>
          📍 {currentEvent.location || currentEvent.venue || 'Location TBD'} <br />
          📅 {currentEvent.date || currentEvent.date_start ? new Date(currentEvent.date || currentEvent.date_start).toLocaleDateString() : 'TBD'}
        </p>

        <div style={{ display: 'flex', gap: '1rem', marginTop: 'auto' }}>
          <button onClick={() => handleSwipe('left')} style={{ flex: 1, padding: '0.8rem', borderRadius: '8px', border: '1px solid #ff6b6b', background: 'rgba(255,107,107,0.08)', color: '#ff6b6b', cursor: 'pointer', fontWeight: '700' }}>
            Skip
          </button>
          <button onClick={() => handleSwipe('right')} style={{ flex: 1, padding: '0.8rem', borderRadius: '8px', border: '1px solid #51cf66', background: 'rgba(81,207,102,0.08)', color: '#51cf66', cursor: 'pointer', fontWeight: '700' }}>
            I'm In!
          </button>
        </div>
      </GlassCard>
    </div>
  );
};

export default EventSwiper;
