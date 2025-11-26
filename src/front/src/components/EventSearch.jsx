import React, { useState, useEffect } from 'react';
import LocationDropdown from './LocationDropdown';
import Filters from './Filters';
import { filterByCategory } from '../config/categories';

import { API_URL } from '../lib/api';

export default function EventSearch({ onEventsLoaded }) {
  const [selectedCity, setSelectedCity] = useState('');
  const [selectedState, setSelectedState] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [events, setEvents] = useState([]);
  const [searched, setSearched] = useState(false);
  const [userCoords, setUserCoords] = useState(null);
  const [includeWebSearch, setIncludeWebSearch] = useState(true); // NEW: Web search toggle
  const [searchStats, setSearchStats] = useState({ database: 0, web: 0 }); // NEW: Track sources
  const [selectedCategory, setSelectedCategory] = useState('All'); // Category filter

  // Auto-detect location on mount
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
      // Get access token for authentication
      const token = localStorage.getItem('access_token');

      // Extract city and state from selectedCity format "City, ST"
      const parts = selectedCity.split(',').map(p => p.trim());
      const cityName = parts[0];
      const stateCode = parts.length > 1 ? parts[parts.length - 1] : selectedState;

      // Validate state code (should be 2 letters)
      if (!stateCode || stateCode.length > 3 || stateCode === 'USA') {
        setError('Please select a city with a valid state (e.g., Boston, MA)');
        setLoading(false);
        return;
      }

      // Build location string
      const location = `${cityName}, ${stateCode}`;
      let allEvents = [];
      let dbCount = 0;
      let webCount = 0;

      // Always search database first
      try {
        const res = await fetch(`${API_URL}/api/events/search`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            location: location,
            limit: 50
          })
        });

        if (res.ok) {
          const data = await res.json();
          const dbEvents = (data.events || []).map(e => ({ ...e, sourceType: 'database' }));
          allEvents = [...dbEvents];
          dbCount = dbEvents.length;
        }
      } catch (dbErr) {
        console.error('Database search error:', dbErr);
      }

      // Also search web if toggle is enabled
      if (includeWebSearch) {
        try {
          const webQuery = `volunteer opportunities ${cityName} ${stateCode}`;
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
              sourceType: 'web'
            }));
            allEvents = [...allEvents, ...webEvents];
            webCount = webEvents.length;
          }
        } catch (webErr) {
          console.error('Web search error:', webErr);
          // Don't fail if web search fails - we still have database results
        }
      }

      setEvents(allEvents);
      setSearchStats({ database: dbCount, web: webCount });

      if (onEventsLoaded) {
        onEventsLoaded(allEvents);
      }

      if (allEvents.length === 0) {
        setError('No events found in this location. Try a different city or enable web search.');
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

      {/* Web Search Toggle */}
      <div style={{
        marginBottom: '20px',
        padding: '16px',
        background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
        borderRadius: '10px',
        border: '2px solid #e5e7eb'
      }}>
        <label style={{
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          cursor: 'pointer',
          userSelect: 'none'
        }}>
          <input
            type="checkbox"
            checked={includeWebSearch}
            onChange={(e) => setIncludeWebSearch(e.target.checked)}
            style={{
              width: '20px',
              height: '20px',
              cursor: 'pointer'
            }}
          />
          <div>
            <div style={{
              fontWeight: '600',
              color: '#333',
              fontSize: '15px'
            }}>
              🌐 Include Web Search
            </div>
            <div style={{
              fontSize: '13px',
              color: '#666',
              marginTop: '2px'
            }}>
              Search the entire web for more volunteer opportunities (powered by Google)
            </div>
          </div>
        </label>
      </div>

      {/* Category Filters */}
      {events.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <label style={{
            display: 'block',
            marginBottom: '12px',
            fontWeight: '600',
            color: '#555',
            fontSize: '15px'
          }}>
            Filter by Category
          </label>
          <Filters active={selectedCategory} onChange={setSelectedCategory} />
        </div>
      )}

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
            htmlFor="location-input"
            style={{
              display: 'block',
              marginBottom: '8px',
              fontWeight: '600',
              color: '#555',
            }}
          >
            Location {userCoords && <span style={{ fontSize: '12px', color: '#10b981' }}>📍 Nearby cities first</span>}
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

      {events.length > 0 && (() => {
        // Apply category filter
        const filteredEvents = filterByCategory(events, selectedCategory);

        return (
          <div>
            <h3
              style={{
                margin: '0 0 16px 0',
                fontSize: '18px',
                color: '#444',
              }}
            >
              {selectedCategory === 'All'
                ? `Found ${events.length} Event${events.length !== 1 ? 's' : ''}`
                : `Showing ${filteredEvents.length} of ${events.length} Event${filteredEvents.length !== 1 ? 's' : ''}`
              }
            </h3>

            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
                gap: '16px',
              }}
            >
              {filteredEvents.map((event) => (
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
        );
      })()}
    </div>
  );
}
