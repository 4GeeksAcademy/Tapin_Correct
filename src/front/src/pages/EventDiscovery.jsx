import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import EventCard from '../components/EventCard';
import CategoryFilter from '../components/CategoryFilter';
import LocationDropdown from '../components/LocationDropdown';
import EventSwiper from '../components/EventSwiper';
import SurpriseMe from '../components/SurpriseMe';
import AchievementsPanel from '../components/AchievementsPanel';
import EventPreview from '../components/EventPreview';
import ARWayfinding from '../components/ARWayfinding';
import GlassCard from '../components/GlassCard';

import { API_URL } from '../lib/api';

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
  const [locationInput, setLocationInput] = useState(''); // For the location dropdown

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
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="hero-header"
        style={{
          background: 'linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%)',
          color: 'white',
          padding: 'var(--space-8) 0',
          marginBottom: 'var(--space-8)'
        }}
      >
        <div className="container">
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
            <div>
              <h1 style={{ fontSize: 'var(--fs-4xl)', fontWeight: 'var(--fw-bold)', marginBottom: 'var(--space-2)' }}>
                <span style={{ marginRight: 'var(--space-3)' }}>🎉</span>
                Discover Events
              </h1>
              <p style={{ margin: 0, opacity: 0.9 }}>
                AI-powered event discovery with personalization
              </p>
            </div>

            {/* Achievements Button */}
            <button
              className="btn btn-secondary btn-lg"
              onClick={() => setShowAchievements(!showAchievements)}
            >
              <i className="fas fa-trophy"></i> Achievements
            </button>
          </div>

          {/* Discovery Mode Tabs */}
          <div className="mode-tabs mb-6">
            <button
              className={`mode-tab ${discoveryMode === 'personalized' ? 'active' : ''}`}
              onClick={() => setDiscoveryMode('personalized')}
            >
              <i className="fas fa-magic"></i> AI Personalized
            </button>
            <button
              className={`mode-tab ${discoveryMode === 'swipe' ? 'active' : ''}`}
              onClick={() => setDiscoveryMode('swipe')}
            >
              <i className="fas fa-hand-pointer"></i> Swipe Mode
            </button>
            <button
              className={`mode-tab ${discoveryMode === 'surprise' ? 'active' : ''}`}
              onClick={() => setDiscoveryMode('surprise')}
            >
              <i className="fas fa-gift"></i> Surprise Me
            </button>
            <button
              className={`mode-tab ${discoveryMode === 'browse' ? 'active' : ''}`}
              onClick={() => setDiscoveryMode('browse')}
            >
              <i className="fas fa-th"></i> Browse All
            </button>
          </div>

          {/* Location selector */}
          <div className="location-search">
            <div style={{ flex: 1 }}>
              <LocationDropdown
                value={locationInput}
                onChange={setLocationInput}
                onSelect={(city) => {
                  setLocationInput(city.name);
                  if (onLocationChange) {
                    onLocationChange({ coords: [city.lat, city.lon], name: city.name, type: 'city' });
                  }
                }}
                userCoords={userCoords ? [userCoords.latitude, userCoords.longitude] : null}
                placeholder="Enter city, state (e.g., Dallas, TX)"
                countryFilter="US"
              />
            </div>
            <button
              className="btn btn-secondary"
              onClick={discoverEvents}
              disabled={!userLocation || loading}
            >
              {loading ? (
                <span className="spinner" />
              ) : (
                <><i className="fas fa-search"></i> Discover</>
              )}
            </button>
          </div>
        </div>
      </motion.div>

      <div className="container">
        {/* Achievements Panel (Slide-out) */}
        {showAchievements && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mb-8"
          >
            <GlassCard>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                <h4 style={{ margin: 0 }}>
                  <i className="fas fa-trophy" style={{ marginRight: 'var(--space-2)', color: 'var(--warning)' }}></i>
                  Your Achievements
                </h4>
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => setShowAchievements(false)}
                >
                  <i className="fas fa-times"></i>
                </button>
              </div>
              <AchievementsPanel token={token} />
            </GlassCard>
          </motion.div>
        )}

        {/* Surprise Me Mode */}
        {discoveryMode === 'surprise' && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8"
          >
            <SurpriseMe
              location={userLocation}
              token={token}
              onEventFound={(event) => {
                setSelectedEvent(event);
                // Record view interaction
                handleEventInteraction(event, 'view');
              }}
            />
          </motion.div>
        )}

        {/* Swipe Mode */}
        {discoveryMode === 'swipe' && !loading && filteredEvents.length > 0 && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mb-8"
          >
            <GlassCard>
              <h4 className="text-center mb-4">
                <i className="fas fa-hand-pointer" style={{ marginRight: 'var(--space-2)' }}></i>
                Swipe Mode
              </h4>
              <p className="text-muted text-center mb-6">
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
          </motion.div>
        )}

        {/* Personalized & Browse Modes */}
        {(discoveryMode === 'personalized' || discoveryMode === 'browse') && (
          <>
            {/* AI Search Bar */}
            <div className="card mb-6">
              <div className="search-bar">
                <i className="fas fa-magic text-primary"></i>
                <input
                  type="text"
                  className="form-input"
                  placeholder="🤖 Search events: 'live music', 'food', 'outdoor'..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
                {searchQuery && (
                  <button
                    className="btn btn-ghost btn-sm"
                    onClick={() => setSearchQuery('')}
                  >
                    <i className="fas fa-times"></i>
                  </button>
                )}
              </div>
              {discoveryMode === 'personalized' && (
                <small className="text-muted" style={{ display: 'block', marginTop: 'var(--space-2)' }}>
                  <i className="fas fa-sparkles" style={{ marginRight: 'var(--space-1)' }}></i>
                  AI-powered personalization based on your preferences
                </small>
              )}
            </div>

            {/* Category Filter */}
            <div className="mb-6">
              <CategoryFilter
                selectedCategory={selectedCategory}
                onCategoryChange={setSelectedCategory}
              />
            </div>

            {/* Results Summary */}
            {!loading && events.length > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-4)' }}>
                <h5 style={{ margin: 0 }}>
                  {filteredEvents.length} Events Found
                  {selectedCategory !== 'All' && ` • ${selectedCategory}`}
                  {discoveryMode === 'personalized' && (
                    <span className="badge-primary">AI Personalized</span>
                  )}
                </h5>

                <div className="view-toggle">
                  <button className="btn btn-ghost btn-sm active">
                    <i className="fas fa-th"></i>
                  </button>
                  <button className="btn btn-ghost btn-sm">
                    <i className="fas fa-list"></i>
                  </button>
                </div>
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className="text-center" style={{ padding: 'var(--space-16) 0' }}>
                <div className="spinner" style={{ width: '48px', height: '48px', margin: '0 auto var(--space-4)' }}></div>
                <p className="text-muted">
                  {discoveryMode === 'personalized'
                    ? 'AI is analyzing your preferences...'
                    : 'Discovering events...'}
                </p>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="alert alert-warning mb-6">
                <i className="fas fa-exclamation-triangle" style={{ marginRight: 'var(--space-2)' }}></i>
                {error}
                <br />
                <small className="text-muted">Showing cached events or falling back to basic search.</small>
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && events.length === 0 && userLocation && (
              <div className="empty-state">
                <div className="empty-state-icon">🔍</div>
                <h3 className="empty-state-title">No events found</h3>
                <p className="empty-state-description">
                  Try selecting a different location or mode
                </p>
                <button
                  className="btn btn-primary"
                  onClick={() => setDiscoveryMode('surprise')}
                >
                  <i className="fas fa-gift"></i> Try Surprise Me
                </button>
              </div>
            )}

            {/* Events Grid */}
            {!loading && filteredEvents.length > 0 && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ duration: 0.4 }}
                className="grid grid-3"
              >
                {filteredEvents.map((event, index) => (
                  <motion.div
                    key={event.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.3 }}
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
                        <i className="fas fa-magic"></i> {event.ai_match_score}% match
                      </div>
                    )}
                  </motion.div>
                ))}
              </motion.div>
            )}

            {/* No Results After Filter */}
            {!loading && events.length > 0 && filteredEvents.length === 0 && (
              <div className="empty-state">
                <div className="empty-state-icon">🎭</div>
                <h3 className="empty-state-title">No matching events</h3>
                <p className="empty-state-description">
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
            >
              <i className="fas fa-directions"></i> Navigate
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
        .hero-header {
          position: relative;
          overflow: hidden;
        }

        .hero-header::before {
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
          pointer-events: none;
        }

        .mode-tabs {
          display: flex;
          gap: var(--space-2);
          flex-wrap: wrap;
        }

        .mode-tab {
          flex: 1;
          min-width: 120px;
          padding: var(--space-3) var(--space-4);
          background: rgba(255, 255, 255, 0.2);
          border: 1px solid rgba(255, 255, 255, 0.3);
          color: white;
          border-radius: var(--radius-lg);
          font-weight: var(--fw-semibold);
          cursor: pointer;
          transition: all var(--transition-fast);
        }

        .mode-tab:hover {
          background: rgba(255, 255, 255, 0.3);
          transform: translateY(-2px);
        }

        .mode-tab.active {
          background: white;
          color: var(--primary);
          box-shadow: var(--shadow-md);
        }

        .location-search {
          display: flex;
          gap: var(--space-3);
          align-items: center;
        }

        .search-bar {
          display: flex;
          align-items: center;
          gap: var(--space-3);
          padding: var(--space-4);
        }

        .search-bar input {
          flex: 1;
          border: none;
          box-shadow: none;
        }

        .search-bar input:focus {
          outline: none;
          box-shadow: none;
          border: none;
        }

        .badge-primary {
          display: inline-block;
          padding: var(--space-1) var(--space-3);
          background: var(--primary);
          color: white;
          border-radius: var(--radius-full);
          font-size: var(--fs-sm);
          font-weight: var(--fw-semibold);
          margin-left: var(--space-2);
        }

        .view-toggle {
          display: flex;
          gap: var(--space-1);
        }

        .view-toggle button.active {
          background: var(--bg-light);
          color: var(--primary);
        }

        .event-card-wrapper {
          position: relative;
          cursor: pointer;
          transition: transform var(--transition-base);
        }

        .event-card-wrapper:hover {
          transform: translateY(-4px);
        }

        .ai-badge {
          position: absolute;
          top: 12px;
          right: 12px;
          background: linear-gradient(135deg, var(--primary) 0%, var(--accent) 100%);
          color: white;
          padding: var(--space-2) var(--space-3);
          border-radius: var(--radius-full);
          font-size: var(--fs-sm);
          font-weight: var(--fw-bold);
          box-shadow: var(--shadow-primary);
          z-index: 10;
        }

        .ar-nav-button {
          position: fixed;
          bottom: 80px;
          right: 20px;
          z-index: 1055;
          border-radius: var(--radius-full);
          box-shadow: var(--shadow-xl);
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0%, 100% {
            box-shadow: var(--shadow-xl);
          }
          50% {
            box-shadow: var(--shadow-primary);
          }
        }

        @media (max-width: 768px) {
          .mode-tabs {
            flex-direction: column;
          }

          .mode-tab {
            min-width: 100%;
          }

          .location-search {
            flex-direction: column;
          }

          .location-search button {
            width: 100%;
          }
        }
      `}</style>
    </div>
  );
}
