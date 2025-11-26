import React, { useState, useEffect } from 'react';
import LocationDropdown from './LocationDropdown';
import EventCard from './EventCard';

import { API_URL } from '../lib/api';

export default function EnhancedEventSearch({ onEventsLoaded }) {
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [searchMode, setSearchMode] = useState('both'); // 'database', 'web', 'both'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);
  const [searched, setSearched] = useState(false);
  const [userCoords, setUserCoords] = useState(null);
  const [stats, setStats] = useState({ database: 0, web: 0 });
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // Check if user is logged in
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    setIsLoggedIn(!!token);
  }, []);

  // Auto-detect location
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserCoords([position.coords.latitude, position.coords.longitude]);
        },
        (error) => {
          console.log('Geolocation not available:', error);
        }
      );
    }
  }, []);

  const handleCitySelect = (city) => {
    if (!city) return;
    setSelectedCity(city.name);
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
      const token = localStorage.getItem('access_token');
      const parts = selectedCity.split(',').map(p => p.trim());
      const cityName = parts[0];
      const stateCode = parts.length > 1 ? parts[parts.length - 1] : selectedState;

      if (!stateCode || stateCode.length > 3 || stateCode === 'USA') {
        setError('Please select a city with a valid state (e.g., Boston, MA)');
        setLoading(false);
        return;
      }

      const location = `${cityName}, ${stateCode}`;
      let allEvents = [];
      let dbCount = 0;
      let webCount = 0;

      // Search database if requested
      if (searchMode === 'database' || searchMode === 'both') {
        try {
          const dbRes = await fetch(`${API_URL}/api/events/search`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ location, limit: 50 })
          });

          if (dbRes.ok) {
            const dbData = await dbRes.json();
            const dbEvents = (dbData.events || []).map(e => ({
              ...e,
              sourceType: 'database'
            }));
            allEvents = [...allEvents, ...dbEvents];
            dbCount = dbEvents.length;
          }
        } catch (err) {
          console.error('Database search error:', err);
        }
      }

      // Search web if requested
      if (searchMode === 'web' || searchMode === 'both') {
        try {
          // Build web search query
          const webQuery = searchQuery || `volunteer opportunities ${cityName} ${stateCode}`;

          const webRes = await fetch(`${API_URL}/api/web-search`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              query: webQuery,
              location: { city: cityName, state: stateCode }
            })
          });

          if (webRes.ok) {
            const webData = await webRes.json();
            const webEvents = (webData.events || []).map(e => ({
              ...e,
              sourceType: 'web',
              source: 'google_custom_search'
            }));
            allEvents = [...allEvents, ...webEvents];
            webCount = webEvents.length;
          }
        } catch (err) {
          console.error('Web search error:', err);
        }
      }

      setEvents(allEvents);
      setStats({ database: dbCount, web: webCount });

      if (onEventsLoaded) {
        onEventsLoaded(allEvents);
      }

      if (allEvents.length === 0 && !error) {
        setError('No events found. Try adjusting your search criteria.');
      }
    } catch (err) {
      setError(err.message);
      setEvents([]);
    } finally {
      setLoading(false);
    }
  };

  // Show login required message if not logged in
  if (!isLoggedIn) {
    return (
      <div
        style={{
          padding: '60px 24px',
          background: '#fff',
          borderRadius: '12px',
          boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
          maxWidth: '800px',
          margin: '40px auto',
          textAlign: 'center',
        }}
      >
        <div style={{ fontSize: '64px', marginBottom: '20px' }}>🔒</div>
        <h2 style={{
          margin: '0 0 16px 0',
          fontSize: '28px',
          fontWeight: '700',
          color: '#333',
        }}>
          Login Required
        </h2>
        <p style={{
          fontSize: '16px',
          color: '#666',
          lineHeight: '1.6',
          marginBottom: '24px',
        }}>
          Please log in to search for volunteer opportunities and discover events in your community.
        </p>
        <button
          onClick={() => {
            // Scroll to top where login form is
            window.scrollTo({ top: 0, behavior: 'smooth' });
          }}
          style={{
            padding: '16px 32px',
            fontSize: '16px',
            fontWeight: '700',
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: '#fff',
            border: 'none',
            borderRadius: '12px',
            cursor: 'pointer',
            boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
            transition: 'transform 0.2s',
          }}
          onMouseEnter={(e) => e.target.style.transform = 'translateY(-2px)'}
          onMouseLeave={(e) => e.target.style.transform = 'translateY(0)'}
        >
          Go to Login
        </button>
      </div>
    );
  }

  return (
    <div
      style={{
        padding: '24px',
        background: '#fff',
        borderRadius: '12px',
        boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        maxWidth: '1200px',
        margin: '20px auto',
      }}
    >
      <h2
        style={{
          margin: '0 0 20px 0',
          fontSize: '28px',
          fontWeight: '700',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent',
          backgroundClip: 'text',
        }}
      >
        🔍 Discover Volunteer Opportunities
      </h2>

      {/* Search Mode Toggle */}
      <div style={{ marginBottom: '20px' }}>
        <label
          style={{
            display: 'block',
            marginBottom: '12px',
            fontWeight: '600',
            color: '#555',
          }}
        >
          Search Mode
        </label>
        <div style={{ display: 'flex', gap: '12px' }}>
          {[
            { value: 'database', label: '💾 Our Database', desc: 'Curated events' },
            { value: 'web', label: '🌐 Web Search', desc: 'Search entire web' },
            { value: 'both', label: '🚀 Both', desc: 'Maximum results' }
          ].map(mode => (
            <button
              key={mode.value}
              onClick={() => setSearchMode(mode.value)}
              style={{
                flex: 1,
                padding: '16px',
                background: searchMode === mode.value
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : '#f9f9f9',
                color: searchMode === mode.value ? '#fff' : '#333',
                border: searchMode === mode.value ? 'none' : '2px solid #eee',
                borderRadius: '12px',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                fontWeight: '600',
                fontSize: '14px',
                textAlign: 'center',
              }}
            >
              <div>{mode.label}</div>
              <div style={{
                fontSize: '11px',
                opacity: 0.8,
                marginTop: '4px'
              }}>
                {mode.desc}
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Search Inputs */}
      <div style={{ display: 'grid', gridTemplateColumns: searchMode !== 'database' ? '1fr 1fr' : '1fr', gap: '12px', marginBottom: '16px' }}>
        <div>
          <label
            htmlFor="location-input"
            style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#555',
            }}
          >
            📍 Location {userCoords && <span style={{ fontSize: '12px', color: '#10b981', fontWeight: 'normal' }}>• Nearby cities first</span>}
          </label>
          <LocationDropdown
            value={selectedCity}
            onChange={(val) => setSelectedCity(val)}
            onSelect={handleCitySelect}
            userCoords={userCoords}
            countryFilter="US"
            placeholder="Enter city (e.g., Austin, TX)"
          />
        </div>

        {searchMode !== 'database' && (
          <div>
            <label
              style={{
                display: 'block',
                marginBottom: '8px',
                fontWeight: '600',
                color: '#555',
              }}
            >
              🔍 Search Keywords (optional)
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="e.g., animal shelter, food bank, education"
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '15px',
                transition: 'border 0.2s',
              }}
              onFocus={(e) => e.target.style.borderColor = '#667eea'}
              onBlur={(e) => e.target.style.borderColor = '#e5e7eb'}
            />
          </div>
        )}
      </div>

      {/* Search Button */}
      <button
        onClick={handleSearch}
        disabled={loading || !selectedState}
        style={{
          width: '100%',
          padding: '16px 24px',
          fontSize: '16px',
          fontWeight: '700',
          background: loading || !selectedState
            ? '#ccc'
            : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: '12px',
          cursor: loading || !selectedState ? 'not-allowed' : 'pointer',
          transition: 'all 0.3s ease',
          boxShadow: loading || !selectedState ? 'none' : '0 4px 15px rgba(102, 126, 234, 0.4)',
        }}
      >
        {loading ? '🔄 Searching...' : '🚀 Search Events'}
      </button>

      {/* Error Message */}
      {error && (
        <div
          style={{
            marginTop: '20px',
            padding: '16px',
            background: '#fee2e2',
            borderLeft: '4px solid #ef4444',
            borderRadius: '8px',
            color: '#991b1b',
            fontWeight: '500',
          }}
        >
          ⚠️ {error}
        </div>
      )}

      {/* Results Stats */}
      {searched && !loading && events.length > 0 && (
        <div style={{
          marginTop: '24px',
          padding: '16px',
          background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
          borderRadius: '12px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          flexWrap: 'wrap',
          gap: '16px',
        }}>
          <div>
            <h3 style={{ margin: 0, fontSize: '20px', color: '#333', fontWeight: '700' }}>
              Found {events.length} Event{events.length !== 1 ? 's' : ''}
            </h3>
            <p style={{ margin: '4px 0 0 0', fontSize: '14px', color: '#666' }}>
              {stats.database > 0 && `${stats.database} from database`}
              {stats.database > 0 && stats.web > 0 && ' • '}
              {stats.web > 0 && `${stats.web} from web search`}
            </p>
          </div>
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
            {stats.database > 0 && (
              <span style={{
                padding: '6px 12px',
                background: '#10b981',
                color: 'white',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600',
              }}>
                💾 {stats.database} Curated
              </span>
            )}
            {stats.web > 0 && (
              <span style={{
                padding: '6px 12px',
                background: '#3b82f6',
                color: 'white',
                borderRadius: '20px',
                fontSize: '12px',
                fontWeight: '600',
              }}>
                🌐 {stats.web} Web
              </span>
            )}
          </div>
        </div>
      )}

      {/* Empty State */}
      {searched && !loading && events.length === 0 && !error && (
        <div style={{
          marginTop: '40px',
          padding: '60px 20px',
          textAlign: 'center',
          background: '#f9fafb',
          borderRadius: '12px',
        }}>
          <div style={{ fontSize: '64px', marginBottom: '16px' }}>🔍</div>
          <h3 style={{ margin: '0 0 12px 0', color: '#444', fontSize: '20px' }}>
            No Events Found
          </h3>
          <p style={{ margin: 0, color: '#666', lineHeight: '1.6' }}>
            We couldn't find any volunteer opportunities matching your search.
            <br />
            Try different keywords or search in a different location.
          </p>
        </div>
      )}

      {/* Event Cards Grid */}
      {events.length > 0 && (
        <div style={{
          marginTop: '24px',
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
          gap: '20px',
        }}>
          {events.map((event) => (
            <EventCard
              key={`${event.sourceType}-${event.id}`}
              event={event}
              onClick={() => {
                // Open event URL in new tab or show detail modal
                if (event.url) {
                  window.open(event.url, '_blank', 'noopener,noreferrer');
                }
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
