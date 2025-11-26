import React, { useState } from 'react';

import { API_URL } from '../lib/api';

/**
 * Surprise Me! - AI Event Generator
 *
 * Generates unexpected but relevant event recommendations
 * based on mood, budget, and adventure level
 */
export default function SurpriseMe({ token, userLocation }) {
  const [loading, setLoading] = useState(false);
  const [surpriseEvent, setSurpriseEvent] = useState(null);
  const [showSettings, setShowSettings] = useState(false);

  // User preferences
  const [mood, setMood] = useState('adventurous');
  const [budget, setBudget] = useState(50);
  const [timeAvailable, setTimeAvailable] = useState(3);
  const [adventureLevel, setAdventureLevel] = useState('high');

  const moods = [
    { value: 'energetic', icon: '⚡', label: 'Energetic' },
    { value: 'chill', icon: '😌', label: 'Chill' },
    { value: 'creative', icon: '🎨', label: 'Creative' },
    { value: 'social', icon: '👥', label: 'Social' },
    { value: 'romantic', icon: '💕', label: 'Romantic' },
    { value: 'adventurous', icon: '🚀', label: 'Adventurous' }
  ];

  async function generateSurprise() {
    if (!userLocation) {
      alert('Please set your location first');
      return;
    }

    setLoading(true);
    setSurpriseEvent(null);

    try {
      const res = await fetch(`${API_URL}/api/events/surprise-me`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          location: userLocation,
          mood,
          budget,
          time_available: timeAvailable,
          adventure_level: adventureLevel
        })
      });

      if (res.ok) {
        const data = await res.json();
        setSurpriseEvent(data.event);
      } else {
        const error = await res.json();
        alert(error.error || 'Failed to generate surprise');
      }
    } catch (error) {
      console.error('Error generating surprise:', error);
      alert('Failed to generate surprise');
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="surprise-me">
      <div className="surprise-header text-center mb-4">
        <div className="display-1 mb-3">🎲</div>
        <h2 className="fw-bold">Feeling Lucky?</h2>
        <p className="text-muted">
          Let AI surprise you with the perfect event
        </p>
      </div>

      {/* Mood selector */}
      <div className="mb-4">
        <label className="form-label fw-bold">How are you feeling?</label>
        <div className="mood-grid">
          {moods.map((m) => (
            <button
              key={m.value}
              className={`mood-btn ${mood === m.value ? 'active' : ''}`}
              onClick={() => setMood(m.value)}
              data-testid={`mood-${m.value}`}
            >
              <div className="mood-icon">{m.icon}</div>
              <div className="mood-label">{m.label}</div>
            </button>
          ))}
        </div>
      </div>

      {/* Quick settings */}
      <div className="card mb-4">
        <div className="card-body">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <h6 className="mb-0">Preferences</h6>
            <button
              className="btn btn-sm btn-link"
              onClick={() => setShowSettings(!showSettings)}
            >
              {showSettings ? 'Hide' : 'Customize'}
            </button>
          </div>

          {showSettings && (
            <div className="settings-expanded">
              {/* Budget */}
              <div className="mb-3">
                <label className="form-label small">
                  Max Budget: <strong>${budget}</strong>
                </label>
                <input
                  type="range"
                  className="form-range"
                  min="0"
                  max="200"
                  step="10"
                  value={budget}
                  onChange={(e) => setBudget(parseInt(e.target.value))}
                />
                <div className="d-flex justify-content-between">
                  <small className="text-muted">Free</small>
                  <small className="text-muted">$200+</small>
                </div>
              </div>

              {/* Time available */}
              <div className="mb-3">
                <label className="form-label small">
                  Time Available: <strong>{timeAvailable} hours</strong>
                </label>
                <input
                  type="range"
                  className="form-range"
                  min="1"
                  max="12"
                  value={timeAvailable}
                  onChange={(e) => setTimeAvailable(parseInt(e.target.value))}
                />
                <div className="d-flex justify-content-between">
                  <small className="text-muted">1 hour</small>
                  <small className="text-muted">All day</small>
                </div>
              </div>

              {/* Adventure level */}
              <div className="mb-3">
                <label className="form-label small">Adventure Level</label>
                <div className="btn-group w-100">
                  {['low', 'medium', 'high'].map((level) => (
                    <button
                      key={level}
                      type="button"
                      className={`btn ${adventureLevel === level ? 'btn-primary' : 'btn-outline-secondary'} btn-sm`}
                      onClick={() => setAdventureLevel(level)}
                    >
                      {level === 'low' && '😌 Comfort Zone'}
                      {level === 'medium' && '🌟 Mix it up'}
                      {level === 'high' && '🚀 Wild Card'}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Generate button */}
      <button
        className="btn btn-lg btn-primary w-100 mb-4 surprise-btn"
        onClick={generateSurprise}
        disabled={loading}
        data-testid="surprise-btn"
      >
        {loading ? (
          <>
            <span className="spinner-border spinner-border-sm me-2"></span>
            Generating surprise...
          </>
        ) : (
          <>
            <i className="fas fa-magic me-2"></i>
            Surprise Me!
          </>
        )}
      </button>

      {/* Surprise event reveal */}
      {surpriseEvent && (
        <div className="surprise-reveal animate__animated animate__fadeInUp">
          <div className="card border-0 shadow-lg">
            {surpriseEvent.image_url && (
              <img
                src={surpriseEvent.image_url}
                alt={surpriseEvent.title}
                className="card-img-top"
                style={{ height: '300px', objectFit: 'cover' }}
              />
            )}

            <div className="card-body">
              <div className="mb-3">
                <span className="badge bg-primary">🎉 Your Surprise Event</span>
                {surpriseEvent.match_score && (
                  <span className="badge bg-success ms-2">
                    {surpriseEvent.match_score}% Match
                  </span>
                )}
              </div>

              <h3 className="card-title">{surpriseEvent.title}</h3>

              {surpriseEvent.surprise_explanation && (
                <div className="alert alert-info mb-3">
                  <i className="fas fa-lightbulb me-2"></i>
                  {surpriseEvent.surprise_explanation}
                </div>
              )}

              <p className="card-text">{surpriseEvent.description}</p>

              <div className="event-details mb-3">
                {surpriseEvent.venue && (
                  <div className="mb-2">
                    <i className="fas fa-map-marker-alt me-2 text-muted"></i>
                    <small>{surpriseEvent.venue}</small>
                  </div>
                )}

                {surpriseEvent.date_start && (
                  <div className="mb-2">
                    <i className="far fa-clock me-2 text-muted"></i>
                    <small>{new Date(surpriseEvent.date_start).toLocaleString()}</small>
                  </div>
                )}

                {surpriseEvent.price && (
                  <div className="mb-2">
                    <i className="fas fa-tag me-2 text-muted"></i>
                    <small className="text-success fw-bold">{surpriseEvent.price}</small>
                  </div>
                )}

                <span
                  className="badge"
                  style={{ backgroundColor: surpriseEvent.category_color || '#667eea' }}
                >
                  {surpriseEvent.category}
                </span>
              </div>

              <div className="d-flex gap-2">
                <button className="btn btn-success flex-grow-1">
                  <i className="fas fa-heart me-2"></i>
                  I'm Going!
                </button>
                <button
                  className="btn btn-outline-secondary"
                  onClick={generateSurprise}
                  data-testid="surprise-tryagain-btn"
                >
                  <i className="fas fa-sync me-2"></i>
                  Try Again
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .surprise-me {
          max-width: 600px;
          margin: 0 auto;
          padding: 20px;
        }

        .mood-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
          gap: 10px;
        }

        .mood-btn {
          background: white;
          border: 2px solid #e0e0e0;
          border-radius: 12px;
          padding: 15px 10px;
          cursor: pointer;
          transition: all 0.2s;
          text-align: center;
        }

        .mood-btn:hover {
          border-color: #667eea;
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .mood-btn.active {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border-color: #667eea;
          color: white;
        }

        .mood-icon {
          font-size: 2rem;
          margin-bottom: 5px;
        }

        .mood-label {
          font-size: 0.875rem;
          font-weight: 500;
        }

        .surprise-btn {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          border: none;
          border-radius: 12px;
          padding: 15px;
          font-size: 1.125rem;
          font-weight: bold;
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .surprise-btn:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 16px rgba(102, 126, 234, 0.4);
        }

        .surprise-reveal {
          animation-duration: 0.5s;
        }

        .settings-expanded {
          animation: slideDown 0.3s ease-out;
        }

        @keyframes slideDown {
          from {
            opacity: 0;
            transform: translateY(-10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @media (max-width: 576px) {
          .mood-grid {
            grid-template-columns: repeat(3, 1fr);
          }
        }
      `}</style>
    </div>
  );
}
