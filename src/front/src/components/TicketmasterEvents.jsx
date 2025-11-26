import React, { useState, useEffect } from 'react';

import { API_URL } from '../lib/api';

export default function TicketmasterEvents({ token, defaultLocation = 'Dallas, TX' }) {
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (token) {
      fetchTicketmasterEvents();
    }
  }, [token]);

  async function fetchTicketmasterEvents() {
    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`${API_URL}/api/events/ticketmaster`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          location: defaultLocation,
          limit: 6
        })
      });

      if (!res.ok) {
        throw new Error(`Failed to fetch Ticketmaster events: ${res.status}`);
      }

      const data = await res.json();
      setEvents(data.events || []);
    } catch (err) {
      console.error('Ticketmaster fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date TBD';
    try {
      const date = new Date(dateStr);
      return date.toLocaleDateString('en-US', {
        weekday: 'short',
        month: 'short',
        day: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  if (!token) return null;

  return (
    <div style={{
      marginTop: '40px',
      padding: '24px',
      background: '#fff',
      borderRadius: '12px',
      boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '20px'
      }}>
        <h3 style={{
          margin: 0,
          fontSize: '24px',
          fontWeight: '700',
          color: '#333',
        }}>
          <span style={{ marginRight: '8px' }}>🎟️</span>
          Ticketmaster Events
        </h3>
        <span style={{
          padding: '4px 12px',
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: '#fff',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: '600',
        }}>
          Live Events
        </span>
      </div>

      {loading && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div style={{ fontSize: '40px', marginBottom: '12px' }}>🎫</div>
          <p>Loading events...</p>
        </div>
      )}

      {error && (
        <div style={{
          padding: '16px',
          background: '#fee',
          borderRadius: '8px',
          color: '#c00',
          marginBottom: '16px',
        }}>
          {error}
        </div>
      )}

      {!loading && !error && events.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎭</div>
          <h4 style={{ margin: '0 0 8px 0', color: '#444' }}>
            No Events Found
          </h4>
          <p style={{ margin: 0 }}>
            Check back later for upcoming events in your area.
          </p>
        </div>
      )}

      {!loading && events.length > 0 && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
          gap: '16px',
        }}>
          {events.map((event) => (
            <div
              key={event.id}
              style={{
                background: '#f9f9f9',
                borderRadius: '10px',
                padding: '16px',
                border: '1px solid #eee',
                transition: 'transform 0.2s, box-shadow 0.2s',
                cursor: 'pointer',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-4px)';
                e.currentTarget.style.boxShadow = '0 8px 24px rgba(0,0,0,0.12)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              {/* Event Image */}
              {event.image_url && (
                <div style={{
                  marginBottom: '12px',
                  borderRadius: '8px',
                  overflow: 'hidden',
                }}>
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

              {/* Category Badge */}
              {event.category && (
                <div style={{
                  display: 'inline-block',
                  padding: '4px 10px',
                  background: '#667eea',
                  color: '#fff',
                  borderRadius: '20px',
                  fontSize: '11px',
                  fontWeight: '600',
                  marginBottom: '8px',
                }}>
                  {event.category}
                </div>
              )}

              {/* Event Title */}
              <h4 style={{
                margin: '0 0 8px 0',
                fontSize: '16px',
                fontWeight: '600',
                color: '#333',
                lineHeight: '1.3',
              }}>
                {event.title}
              </h4>

              {/* Venue */}
              {event.venue && (
                <div style={{
                  fontSize: '14px',
                  color: '#667eea',
                  fontWeight: '500',
                  marginBottom: '8px',
                }}>
                  📍 {event.venue}
                </div>
              )}

              {/* Date */}
              <div style={{
                fontSize: '13px',
                color: '#666',
                marginBottom: '8px',
              }}>
                📅 {formatDate(event.date_start)}
              </div>

              {/* Location */}
              {event.city && event.state && (
                <div style={{
                  fontSize: '13px',
                  color: '#666',
                  marginBottom: '8px',
                }}>
                  📍 {event.city}, {event.state}
                </div>
              )}

              {/* Price */}
              {event.price && (
                <div style={{
                  fontSize: '13px',
                  color: '#10b981',
                  fontWeight: '600',
                  marginBottom: '12px',
                }}>
                  💰 {event.price}
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
                  Get Tickets →
                </a>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
