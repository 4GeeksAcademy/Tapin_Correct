import React, { useState, useEffect } from 'react';
import EventCard from '../components/EventCard';
import CategoryFilter from '../components/CategoryFilter';
import LocationSelector from '../components/LocationSelector';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Modern event discovery page with AI-powered search
 * Features:
 * - Tonight's local events discovery
 * - Volunteer opportunities
 * - Category-based filtering
 * - AI-enhanced search
 * - Image galleries
 */
export default function EventDiscovery({ token, userLocation, onLocationChange }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [eventType, setEventType] = useState('tonight'); // 'tonight' or 'volunteer'
  const [selectedEvent, setSelectedEvent] = useState(null);

  useEffect(() => {
    if (userLocation && token) {
      discoverEvents();
    }
  }, [userLocation, eventType, token]);

  async function discoverEvents() {
    if (!userLocation) return;

    setLoading(true);
    setError(null);

    try {
      const endpoint = eventType === 'tonight'
        ? '/api/local-events/tonight'
        : '/api/discover-events';

      const res = await fetch(`${API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          location: userLocation,
          limit: 50,
        }),
      });

      if (!res.ok) throw new Error(`Failed to fetch events: ${res.status}`);

      const data = await res.json();
      setEvents(data.events || []);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }

  // Filter events by category and search query
  const filteredEvents = events.filter((event) => {
    // Category filter
    if (selectedCategory !== 'All' && event.category !== selectedCategory) {
      return false;
    }

    // Search filter (AI-enhanced)
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

  return (
    <div className="event-discovery">
      {/* Header */}
      <div className="bg-gradient text-white py-5 mb-4" style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <div className="container">
          <h1 className="display-4 fw-bold mb-2">
            <span className="me-3">🎉</span>
            Discover Local Events
          </h1>
          <p className="lead mb-4">
            AI-powered event discovery • Find what's happening tonight near you
          </p>

          {/* Location selector */}
          <div className="row g-3 align-items-end">
            <div className="col-md-6">
              <label className="form-label text-white-50 small">Location</label>
              <LocationSelector
                value={userLocation}
                onChange={onLocationChange}
                placeholder="Enter city, state (e.g., Dallas, TX)"
              />
            </div>

            <div className="col-md-3">
              <label className="form-label text-white-50 small">Event Type</label>
              <select
                className="form-select"
                value={eventType}
                onChange={(e) => setEventType(e.target.value)}
              >
                <option value="tonight">Tonight's Events</option>
                <option value="volunteer">Volunteer Opportunities</option>
              </select>
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
                Discover Events
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="container">
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
                placeholder="🤖 AI-powered search: Try 'live music', 'food events', 'outdoor activities'..."
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
            <small className="text-muted d-block mt-2">
              <i className="fas fa-lightbulb me-1"></i>
              Powered by LangChain AI • Natural language search across all events
            </small>
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
              {filteredEvents.length} {eventType === 'tonight' ? "Events Tonight" : "Volunteer Opportunities"}
              {selectedCategory !== 'All' && ` • ${selectedCategory}`}
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
            <p className="text-muted">Discovering events using AI...</p>
          </div>
        )}

        {/* Error State */}
        {error && (
          <div className="alert alert-danger">
            <i className="fas fa-exclamation-circle me-2"></i>
            {error}
          </div>
        )}

        {/* Empty State */}
        {!loading && !error && events.length === 0 && userLocation && (
          <div className="text-center py-5">
            <div className="display-1 mb-3">🔍</div>
            <h3>No events found</h3>
            <p className="text-muted">
              Try selecting a different location or event type
            </p>
          </div>
        )}

        {/* Events Grid */}
        {!loading && filteredEvents.length > 0 && (
          <div className="row g-4">
            {filteredEvents.map((event) => (
              <div key={event.id} className="col-md-6 col-lg-4">
                <EventCard
                  event={event}
                  onClick={() => setSelectedEvent(event)}
                />
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
      </div>

      {/* Event Detail Modal */}
      {selectedEvent && (
        <div
          className="modal d-block"
          style={{ backgroundColor: 'rgba(0,0,0,0.5)' }}
          onClick={() => setSelectedEvent(null)}
        >
          <div
            className="modal-dialog modal-lg modal-dialog-centered"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="modal-content">
              <div className="modal-header border-0">
                <h5 className="modal-title">{selectedEvent.title}</h5>
                <button
                  type="button"
                  className="btn-close"
                  onClick={() => setSelectedEvent(null)}
                ></button>
              </div>
              <div className="modal-body">
                {selectedEvent.image_url && (
                  <img
                    src={selectedEvent.image_url}
                    alt={selectedEvent.title}
                    className="img-fluid rounded mb-3"
                  />
                )}

                <div className="mb-3">
                  <span className="badge bg-primary me-2">{selectedEvent.category}</span>
                  {selectedEvent.price && (
                    <span className="badge bg-success">{selectedEvent.price}</span>
                  )}
                </div>

                <p className="mb-3">{selectedEvent.description}</p>

                <div className="row g-3 mb-3">
                  {selectedEvent.date_start && (
                    <div className="col-md-6">
                      <i className="far fa-clock me-2 text-muted"></i>
                      <small>{new Date(selectedEvent.date_start).toLocaleString()}</small>
                    </div>
                  )}

                  {selectedEvent.venue && (
                    <div className="col-md-6">
                      <i className="fas fa-map-marker-alt me-2 text-muted"></i>
                      <small>{selectedEvent.venue}</small>
                    </div>
                  )}

                  {selectedEvent.organization && (
                    <div className="col-md-6">
                      <i className="fas fa-building me-2 text-muted"></i>
                      <small>{selectedEvent.organization}</small>
                    </div>
                  )}

                  {selectedEvent.source && (
                    <div className="col-md-6">
                      <i className="fas fa-globe me-2 text-muted"></i>
                      <small>{selectedEvent.source}</small>
                    </div>
                  )}
                </div>

                {selectedEvent.url && (
                  <a
                    href={selectedEvent.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="btn btn-primary w-100"
                  >
                    <i className="fas fa-external-link-alt me-2"></i>
                    Learn More
                  </a>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .event-card {
          transition: transform 0.2s, box-shadow 0.2s;
        }

        .event-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
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
      `}</style>
    </div>
  );
}
