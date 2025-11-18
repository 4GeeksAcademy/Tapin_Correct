import React, { useState, useEffect } from 'react';
import EventCard from '../components/EventCard';
import CategoryFilter from '../components/CategoryFilter';
import LocationSelector from '../components/LocationSelector';
import EventSwiper from '../components/EventSwiper';
import SurpriseMe from '../components/SurpriseMe';
import AchievementsPanel from '../components/AchievementsPanel';
import EventPreview from '../components/EventPreview';
import ARWayfinding from '../components/ARWayfinding';
import GlassCard from '../components/GlassCard';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Modern event discovery page with AI-powered features
 * Features:
 * - AI Personalized Feed
 * - Swipe Mode (Tinder-style)
 * - Surprise Me AI
 * - Achievements & Gamification
 * - AR Navigation
 * - Social Discovery
 */
export default function EventDiscovery({ token, userLocation, onLocationChange }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [discoveryMode, setDiscoveryMode] = useState('personalized'); // personalized, swipe, surprise, browse
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [showAchievements, setShowAchievements] = useState(false);
  const [showARNav, setShowARNav] = useState(false);
  const [userCoords, setUserCoords] = useState(null);

  // Get user's geolocation
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserCoords({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          });
        },
        (error) => console.log('Geolocation error:', error)
      );
    }
  }, []);

  useEffect(() => {
    if (userLocation && token) {
      discoverEvents();
    }
  }, [userLocation, token, discoveryMode]);

  async function discoverEvents() {
    if (!userLocation) return;

    setLoading(true);
    setError(null);

    try {
      let endpoint = '/api/local-events/tonight';

      // Use AI personalized endpoint for personalized mode
      if (discoveryMode === 'personalized') {
        endpoint = '/api/events/personalized';
      }

      // Fetch both local volunteer events and Ticketmaster events in parallel
      const [localRes, ticketmasterRes] = await Promise.all([
        fetch(`${API_URL}${endpoint}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({
            location: userLocation,
            limit: 25,  // Reduced to make room for Ticketmaster events
          }),
        }),
        fetch(`${API_URL}/api/events/ticketmaster`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            location: userLocation,
            limit: 25,  // Add 25 Ticketmaster events
          }),
        }).catch(() => null)  // Don't fail if Ticketmaster is unavailable
      ]);

      let allEvents = [];

      // Parse local events
      if (localRes.ok) {
        const localData = await localRes.json();
        allEvents = localData.events || [];
      }

      // Parse and merge Ticketmaster events
      if (ticketmasterRes && ticketmasterRes.ok) {
        const tmData = await ticketmasterRes.json();
        const tmEvents = tmData.events || [];
        allEvents = [...allEvents, ...tmEvents];
      }

      // Shuffle events to mix volunteer and commercial events
      allEvents.sort(() => Math.random() - 0.5);

      setEvents(allEvents);
    } catch (error) {
      console.error('Discovery error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  // Filter events by category and search query
  const filteredEvents = events.filter((event) => {
    if (selectedCategory !== 'All' && event.category !== selectedCategory) {
      return false;
    }

    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase();
      const searchableText = `
        ${event.title}
        ${event.description}
        ${event.venue}
        ${event.category}
        ${event.organization}
      `.toLowerCase();

      return searchableText.includes(query);
    }

    return true;
  });

  // Handle event interaction (from swiper)
  async function handleEventInteraction(event, interactionType) {
    try {
      await fetch(`${API_URL}/api/events/interact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          event_id: event.id,
          interaction_type: interactionType,
        }),
      });
    } catch (error) {
      console.error('Interaction error:', error);
    }
  }

  return (
    <div className="event-discovery">
      {/* Header with Mode Selector */}
      <div className="bg-gradient text-white py-4 mb-4" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div className="container">
          <div className="d-flex justify-content-between align-items-center mb-3">
            <div>
              <h1 className="display-5 fw-bold mb-2">
                <span className="me-3">🎉</span>
                Discover Events
              </h1>
              <p className="mb-0 opacity-75">
                AI-powered event discovery with personalization
              </p>
            </div>

            {/* Achievements Button */}
            <button
              className="btn btn-light btn-lg"
              onClick={() => setShowAchievements(!showAchievements)}
            >
              <i className="fas fa-trophy me-2"></i>
              Achievements
            </button>
          </div>

          {/* Discovery Mode Tabs */}
          <div className="btn-group w-100 mb-3" role="group">
            <button
              className={`btn ${discoveryMode === 'personalized' ? 'btn-light' : 'btn-outline-light'}`}
              onClick={() => setDiscoveryMode('personalized')}
            >
              <i className="fas fa-magic me-2"></i>
              AI Personalized
            </button>
            <button
              className={`btn ${discoveryMode === 'swipe' ? 'btn-light' : 'btn-outline-light'}`}
              onClick={() => setDiscoveryMode('swipe')}
            >
              <i className="fas fa-hand-pointer me-2"></i>
              Swipe Mode
            </button>
            <button
              className={`btn ${discoveryMode === 'surprise' ? 'btn-light' : 'btn-outline-light'}`}
              onClick={() => setDiscoveryMode('surprise')}
            >
              <i className="fas fa-gift me-2"></i>
              Surprise Me
            </button>
            <button
              className={`btn ${discoveryMode === 'browse' ? 'btn-light' : 'btn-outline-light'}`}
              onClick={() => setDiscoveryMode('browse')}
            >
              <i className="fas fa-th me-2"></i>
              Browse All
            </button>
          </div>

          {/* Location selector */}
          <div className="row g-2">
            <div className="col-md-9">
              <LocationSelector
                value={userLocation}
                onChange={onLocationChange}
                placeholder="Enter city, state (e.g., Dallas, TX)"
              />
            </div>
            <div className="col-md-3">
              <button
                className="btn btn-light w-100"
                onClick={discoverEvents}
                disabled={!userLocation || loading}
              >
                {loading ? (
                  <span className="spinner-border spinner-border-sm me-2" />
                ) : (
                  <i className="fas fa-search me-2"></i>
                )}
                Discover
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
        {/* Achievements Panel (Slide-out) */}
        {showAchievements && (
          <div className="mb-4">
            <GlassCard>
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h4 className="mb-0">
                  <i className="fas fa-trophy me-2 text-warning"></i>
                  Your Achievements
                </h4>
                <button
                  className="btn btn-sm btn-outline-secondary"
                  onClick={() => setShowAchievements(false)}
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>
              <AchievementsPanel token={token} />
            </GlassCard>
          </div>
        )}

        {/* Surprise Me Mode */}
        {discoveryMode === 'surprise' && (
          <div className="mb-4">
            <SurpriseMe
              location={userLocation}
              token={token}
              onEventFound={(event) => {
                setSelectedEvent(event);
                // Record view interaction
                handleEventInteraction(event, 'view');
              }}
            />
          </div>
        )}

        {/* Swipe Mode */}
        {discoveryMode === 'swipe' && !loading && filteredEvents.length > 0 && (
          <div className="mb-4">
            <GlassCard>
              <h4 className="mb-3 text-center">
                <i className="fas fa-hand-pointer me-2"></i>
                Swipe Mode
              </h4>
              <p className="text-muted text-center mb-4">
                ⬅️ Swipe left to skip • Swipe right to like ➡️ • Swipe up for super like ⬆️
              </p>
              <EventSwiper
                events={filteredEvents}
                token={token}
                onSwipe={(event, direction) => {
                  const interactionMap = {
                    'left': 'dislike',
                    'right': 'like',
                    'up': 'super_like',
                    'down': 'skip'
                  };
                  handleEventInteraction(event, interactionMap[direction]);
                }}
              />
            </GlassCard>
          </div>
        )}

        {/* Personalized & Browse Modes */}
        {(discoveryMode === 'personalized' || discoveryMode === 'browse') && (
          <>
            {/* AI Search Bar */}
            <div className="card shadow-sm mb-4">
              <div className="card-body">
                <div className="input-group">
                  <span className="input-group-text bg-white border-end-0">
                    <i className="fas fa-magic text-primary"></i>
                  </span>
                  <input
                    type="text"
                    className="form-control border-start-0 border-end-0"
                    placeholder="🤖 Search events: 'live music', 'food', 'outdoor'..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                  />
                  {searchQuery && (
                    <button
                      className="btn btn-outline-secondary"
                      onClick={() => setSearchQuery('')}
                    >
                      <i className="fas fa-times"></i>
                    </button>
                  )}
                </div>
                {discoveryMode === 'personalized' && (
                  <small className="text-muted d-block mt-2">
                    <i className="fas fa-sparkles me-1"></i>
                    AI-powered personalization based on your preferences
                  </small>
                )}
              </div>
            </div>

            {/* Category Filter */}
            <div className="mb-4">
              <CategoryFilter
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
              />
            </div>

            {/* Results Summary */}
            {!loading && events.length > 0 && (
              <div className="d-flex justify-content-between align-items-center mb-3">
                <h5 className="mb-0">
                  {filteredEvents.length} Events Found
                  {selectedCategory !== 'All' && ` • ${selectedCategory}`}
                  {discoveryMode === 'personalized' && (
                    <span className="badge bg-primary ms-2">AI Personalized</span>
                  )}
                </h5>

                <div className="btn-group btn-group-sm">
                  <button className="btn btn-outline-secondary active">
                    <i className="fas fa-th"></i>
                  </button>
                  <button className="btn btn-outline-secondary">
                    <i className="fas fa-list"></i>
                  </button>
                </div>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="text-center py-5">
                <div className="spinner-border text-primary mb-3" role="status">
                  <span className="visually-hidden">Loading...</span>
                </div>
                <p className="text-muted">
                  {discoveryMode === 'personalized'
                    ? 'AI is analyzing your preferences...'
                    : 'Discovering events...'}
                </p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="alert alert-warning">
                <i className="fas fa-exclamation-triangle me-2"></i>
                {error}
                <br />
                <small className="text-muted">Showing cached events or falling back to basic search.</small>
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && events.length === 0 && userLocation && (
              <div className="text-center py-5">
                <div className="display-1 mb-3">🔍</div>
                <h3>No events found</h3>
                <p className="text-muted">
                  Try selecting a different location or mode
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => setDiscoveryMode('surprise')}
                >
                  <i className="fas fa-gift me-2"></i>
                  Try Surprise Me
                </button>
              </div>
            )}

            {/* Events Grid */}
            {!loading && filteredEvents.length > 0 && (
              <div className="row g-4">
                {filteredEvents.map((event) => (
                  <div key={event.id} className="col-md-6 col-lg-4">
                    <div
                      className="event-card-wrapper"
                      onClick={() => {
                        setSelectedEvent(event);
                        handleEventInteraction(event, 'view');
                      }}
                    >
                      <EventCard event={event} />

                      {/* AI Match Score Badge (Personalized Mode) */}
                      {discoveryMode === 'personalized' && event.ai_match_score && (
                        <div className="ai-badge">
                          <i className="fas fa-magic me-1"></i>
                          {event.ai_match_score}% match
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* No Results After Filter */}
            {!loading && events.length > 0 && filteredEvents.length === 0 && (
              <div className="text-center py-5">
                <div className="display-1 mb-3">🎭</div>
                <h3>No matching events</h3>
                <p className="text-muted">
                  Try adjusting your filters or search query
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => {
                    setSelectedCategory('All');
                    setSearchQuery('');
                  }}
                >
                  Clear Filters
                </button>
              </div>
            )}
          </>
        )}
      </div>

      {/* Event Detail Modal with AR Navigation */}
      {selectedEvent && (
        <>
          <EventPreview
            event={selectedEvent}
            onClose={() => setSelectedEvent(null)}
          />

          {/* AR Navigation Button (Overlay) */}
          {userCoords && selectedEvent.latitude && selectedEvent.longitude && (
            <button
              className="btn btn-primary btn-lg ar-nav-button"
              onClick={() => setShowARNav(true)}
              style={{
                position: 'fixed',
                bottom: '80px',
                right: '20px',
                zIndex: 1055,
                borderRadius: '50px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.3)'
              }}
            >
              <i className="fas fa-directions me-2"></i>
              Navigate
            </button>
          )}
        </>
      )}

      {/* AR Wayfinding */}
      {showARNav && selectedEvent && userCoords && (
        <ARWayfinding
          event={selectedEvent}
          userLocation={userCoords}
          onClose={() => setShowARNav(false)}
        />
      )}

      <style jsx>{`
        .event-card-wrapper {
          position: relative;
          cursor: pointer;
        }

        .event-card-wrapper:hover {
          transform: translateY(-4px);
          transition: transform 0.2s;
        }

        .ai-badge {
          position: absolute;
          top: 10px;
          right: 10px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 6px 12px;
          border-radius: 20px;
          font-size: 0.85rem;
          font-weight: bold;
          box-shadow: 0 2px 8px rgba(102, 126, 234, 0.4);
          z-index: 10;
        }

        .bg-gradient {
          position: relative;
          overflow: hidden;
        }

        .bg-gradient::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }

        .btn-group {
          box-shadow: 0 2px 8px rgba(0,0,0,0.15);
        }

        .ar-nav-button {
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% {
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
          }
          50% {
            box-shadow: 0 4px 20px rgba(102, 126, 234, 0.8);
          }
        }
      `}</style>
    </div>
  );
}
