import React, { useState } from 'react';
import './VolunteerSearch.css';

const VolunteerSearch = () => {
  const [query, setQuery] = useState('');
  const [location, setLocation] = useState({ city: '', state: '' });
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [expandedCard, setExpandedCard] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();

    if (!query.trim()) {
      setError('Please enter a search query');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('access_token');

      if (!token) {
        setError('Please log in to search for volunteer opportunities');
        setLoading(false);
        return;
      }

      const response = await fetch('http://127.0.0.1:5000/api/web-search', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          query: query,
          location: location.city && location.state ? location : null
        })
      });

      if (!response.ok) {
        throw new Error('Search failed');
      }

      const data = await response.json();
      setResults(data.events || []);

      if (data.events && data.events.length === 0) {
        setError('No results found. Try a different search term.');
      }
    } catch (err) {
      setError(err.message || 'Failed to search. Please try again.');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const toggleExpand = (eventId) => {
    setExpandedCard(expandedCard === eventId ? null : eventId);
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Animal Welfare': '#10b981',
      'Arts & Culture': '#8b5cf6',
      'Children & Youth': '#f59e0b',
      'Community Development': '#3b82f6',
      'Disaster Relief': '#ef4444',
      'Education & Literacy': '#06b6d4',
      'Environment': '#22c55e',
      'Health & Medicine': '#ec4899',
      'Human Rights': '#f97316',
      'Seniors': '#6366f1',
      'Social Services': '#14b8a6',
      'Sports & Recreation': '#84cc16',
      'Technology': '#a855f7',
      "Women's Issues": '#db2777',
      'Other': '#64748b'
    };
    return colors[category] || colors['Other'];
  };

  return (
    <div className="volunteer-search-container">
      <div className="search-header">
        <h1>🔍 Find Volunteer Opportunities</h1>
        <p>Search the web for volunteer opportunities and connect with organizations</p>
      </div>

      <form onSubmit={handleSearch} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="e.g., animal shelter volunteer San Francisco"
            className="search-input"
            disabled={loading}
          />
          <button
            type="submit"
            className="search-button"
            disabled={loading}
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>

        <div className="location-inputs">
          <input
            type="text"
            value={location.city}
            onChange={(e) => setLocation({ ...location, city: e.target.value })}
            placeholder="City (optional)"
            className="location-input"
            disabled={loading}
          />
          <input
            type="text"
            value={location.state}
            onChange={(e) => setLocation({ ...location, state: e.target.value })}
            placeholder="State (optional)"
            className="location-input"
            disabled={loading}
          />
        </div>
      </form>

      {error && (
        <div className="error-message">
          ⚠️ {error}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-summary">
          Found {results.length} volunteer opportunities
        </div>
      )}

      <div className="results-grid">
        {results.map((event) => (
          <div key={event.id} className="result-card">
            <div className="card-header">
              <h3 className="organization-name">{event.organization}</h3>
              <span
                className="category-badge"
                style={{ backgroundColor: getCategoryColor(event.category) }}
              >
                {event.category}
              </span>
            </div>

            <h4 className="event-title">{event.title}</h4>

            <p className="event-description">
              {event.description && event.description.length > 150
                ? `${event.description.substring(0, 150)}...`
                : event.description}
            </p>

            {event.location_city && event.location_state && (
              <p className="event-location">
                📍 {event.location_city}, {event.location_state}
              </p>
            )}

            <div className="card-actions">
              <button
                className="volunteer-button"
                onClick={() => toggleExpand(event.id)}
              >
                {expandedCard === event.id ? '▼ Hide Details' : '▶ Volunteer Now'}
              </button>

              {event.url && (
                <a
                  href={event.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="website-link"
                >
                  Visit Website →
                </a>
              )}
            </div>

            {expandedCard === event.id && (
              <div className="contact-details">
                <h5>📞 Contact Information</h5>

                {event.contact_email ? (
                  <div className="contact-item">
                    <strong>Email:</strong>{' '}
                    <a href={`mailto:${event.contact_email}`}>
                      {event.contact_email}
                    </a>
                  </div>
                ) : null}

                {event.contact_phone ? (
                  <div className="contact-item">
                    <strong>Phone:</strong>{' '}
                    <a href={`tel:${event.contact_phone}`}>
                      {event.contact_phone}
                    </a>
                  </div>
                ) : null}

                {event.contact_person ? (
                  <div className="contact-item">
                    <strong>Contact Person:</strong> {event.contact_person}
                  </div>
                ) : null}

                {!event.contact_email && !event.contact_phone && !event.contact_person && (
                  <p className="no-contact">
                    Contact information not available. Please visit their website for more details.
                  </p>
                )}

                {event.url && (
                  <div className="contact-item">
                    <strong>Website:</strong>{' '}
                    <a href={event.url} target="_blank" rel="noopener noreferrer">
                      {event.url.length > 50 ? event.url.substring(0, 50) + '...' : event.url}
                    </a>
                  </div>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default VolunteerSearch;
