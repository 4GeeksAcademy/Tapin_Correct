import React, { useState } from 'react';
import LocationDropdown from './LocationDropdown';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function EventSearch({ onEventsLoaded }) {
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);
  const [searched, setSearched] = useState(false);

  const handleCitySelect = (city) => {
    if (!city) return;
    setSelectedCity(city.name);
    // Extract state from city name (format: "City, ST")
    const parts = city.name.split(', ');
    if (parts.length >= 2) {
      setSelectedState(parts[parts.length - 1]);
    }
  };

  const handleSearch = async () => {
    if (!selectedCity) {
      setError('Please select a city to search for events');
      return;
    }

    setLoading(true);
    setError(null);
    setSearched(true);

    try {
      // Extract city and state from selectedCity format "City, ST"
      const parts = selectedCity.split(',').map(p => p.trim());
      const cityName = parts[0];
      const stateCode = parts.length > 1 ? parts[parts.length - 1] : selectedState;

      // Validate state code (should be 2 letters)
      if (!stateCode || stateCode.length > 3 || stateCode === 'USA') {
        setError('Please select a city with a valid state (e.g., Boston, MA)');
        return;
      }

      const params = new URLSearchParams();
      params.set('city', cityName);
      params.set('state', stateCode);

      const url = `${API_URL}/events/search?${params.toString()}`;
      console.log('Searching:', url);
      const res = await fetch(url);

      if (!res.ok) {
        const errorData = await res.json();
        throw new Error(errorData.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setEvents(data.events || []);

      if (onEventsLoaded) {
        onEventsLoaded(data.events || []);
      }
    } catch (err) {
      setError(err.message);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date TBD';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        year: 'numeric',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <div
      style={{
        padding: '24px',
        background: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        maxWidth: '900px',
        margin: '20px auto',
      }}
    >
      <h2
        style={{
          margin: '0 0 20px 0',
          fontSize: '24px',
          fontWeight: '700',
          color: '#333',
        }}
      >
        Discover Volunteer Events
      </h2>

      <div
        style={{
          display: 'flex',
          gap: '12px',
          marginBottom: '20px',
          alignItems: 'flex-end',
        }}
      >
        <div style={{ flex: 1 }}>
          <label
            style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#555',
            }}
          >
            Location
          </label>
          <LocationDropdown
            value={selectedCity}
            onChange={(val) => setSelectedCity(val)}
            onSelect={handleCitySelect}
            placeholder="Enter city (e.g., Austin, TX)"
          />
        </div>

        <button
          onClick={handleSearch}
          disabled={loading || !selectedState}
          style={{
            padding: '12px 24px',
            fontSize: '16px',
            fontWeight: '600',
            background:
              loading || !selectedState
                ? '#ccc'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '8px',
            cursor: loading || !selectedState ? 'not-allowed' : 'pointer',
            transition: 'all 0.3s ease',
            minWidth: '140px',
            height: '48px',
          }}
        >
          {loading ? 'Searching...' : 'Search Events'}
        </button>
      </div>

      {error && (
        <div
          style={{
            padding: '12px 16px',
            background: '#fee',
            borderRadius: '8px',
            color: '#c00',
            marginBottom: '16px',
          }}
        >
          {error}
        </div>
      )}

      {searched && !loading && events.length === 0 && !error && (
        <div
          style={{
            padding: '40px 20px',
            textAlign: 'center',
            color: '#666',
          }}
        >
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>
            {' '}
          </div>
          <h3 style={{ margin: '0 0 8px 0', color: '#444' }}>
            No Events Found
          </h3>
          <p style={{ margin: 0 }}>
            We&apos;re searching for volunteer opportunities in your area.
            <br />
            Try a different location or check back later.
          </p>
        </div>
      )}

      {events.length > 0 && (
        <div>
          <h3
            style={{
              margin: '0 0 16px 0',
              fontSize: '18px',
              color: '#444',
            }}
          >
            Found {events.length} Event{events.length !== 1 ? 's' : ''}
          </h3>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
              gap: '16px',
            }}
          >
            {events.map((event) => (
              <div
                key={event.id}
                style={{
                  background: '#f9f9f9',
                  borderRadius: '10px',
                  padding: '16px',
                  border: '1px solid #eee',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow =
                    '0 8px 24px rgba(0,0,0,0.12)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                {/* Event Image */}
                {event.image_url && (
                  <div
                    style={{
                      marginBottom: '12px',
                      borderRadius: '8px',
                      overflow: 'hidden',
                    }}
                  >
                    <img
                      src={event.image_url}
                      alt={event.title}
                      style={{
                        width: '100%',
                        height: '160px',
                        objectFit: 'cover',
                      }}
                      onError={(e) => {
                        e.target.style.display = 'none';
                      }}
                    />
                  </div>
                )}

                {/* Event Title */}
                <h4
                  style={{
                    margin: '0 0 8px 0',
                    fontSize: '16px',
                    fontWeight: '600',
                    color: '#333',
                    lineHeight: '1.3',
                  }}
                >
                  {event.title}
                </h4>

                {/* Organization */}
                <div
                  style={{
                    fontSize: '14px',
                    color: '#667eea',
                    fontWeight: '500',
                    marginBottom: '8px',
                  }}
                >
                  {event.organization}
                </div>

                {/* Date */}
                <div
                  style={{
                    fontSize: '13px',
                    color: '#666',
                    marginBottom: '8px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <span>&#128197;</span>
                  {formatDate(event.date_start)}
                </div>

                {/* Location */}
                <div
                  style={{
                    fontSize: '13px',
                    color: '#666',
                    marginBottom: '12px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                  }}
                >
                  <span>&#128205;</span>
                  {event.location_city}, {event.location_state}
                </div>

                {/* Description */}
                {event.description && (
                  <p
                    style={{
                      margin: '0 0 12px 0',
                      fontSize: '13px',
                      color: '#555',
                      lineHeight: '1.5',
                      display: '-webkit-box',
                      WebkitLineClamp: 3,
                      WebkitBoxOrient: 'vertical',
                      overflow: 'hidden',
                    }}
                  >
                    {event.description}
                  </p>
                )}

                {/* Category Badge */}
                {event.category && (
                  <div
                    style={{
                      display: 'inline-block',
                      padding: '4px 10px',
                      background: '#e8f4f8',
                      color: '#0077b6',
                      borderRadius: '20px',
                      fontSize: '11px',
                      fontWeight: '600',
                      marginBottom: '12px',
                    }}
                  >
                    {event.category}
                  </div>
                )}

                {/* Link to Event */}
                {event.url && (
                  <a
                    href={event.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    style={{
                      display: 'inline-block',
                      padding: '8px 16px',
                      background: '#667eea',
                      color: '#fff',
                      textDecoration: 'none',
                      borderRadius: '6px',
                      fontSize: '13px',
                      fontWeight: '600',
                      transition: 'background 0.2s',
                    }}
                    onMouseEnter={(e) => {
                      e.target.style.background = '#5a6fd6';
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.background = '#667eea';
                    }}
                  >
                    View Details
                  </a>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
