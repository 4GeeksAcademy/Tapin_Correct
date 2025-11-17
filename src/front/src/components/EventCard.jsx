import React, { useState } from 'react';

/**
 * Modern event card component with image gallery
 * Displays event information with category-based color coding
 */
export default function EventCard({ event, onClick }) {
  const [imageIndex, setImageIndex] = useState(0);

  // Parse image URLs
  const images = event.image_urls
    ? (typeof event.image_urls === 'string'
        ? JSON.parse(event.image_urls)
        : event.image_urls)
    : (event.image_url ? [event.image_url] : []);

  // Format date
  const formatDate = (dateStr) => {
    if (!dateStr) return 'Date TBD';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
      weekday: 'short',
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  // Category colors
  const categoryColors = {
    'Music & Concerts': '#673AB7',
    'Comedy': '#FF5722',
    'Arts & Theater': '#E91E63',
    'Food & Dining': '#FF9800',
    'Sports': '#4CAF50',
    'Fitness': '#8BC34A',
    'Tech & Innovation': '#00BCD4',
    'Nightlife': '#673AB7',
    'Volunteer': '#4CAF50',
    'Hunger Relief': '#4CAF50',
    'Animal Welfare': '#FF9800',
    'Environment': '#2196F3',
    'Education': '#9C27B0',
  };

  const categoryColor = categoryColors[event.category] || '#607D8B';

  return (
    <div
      className="card h-100 shadow-sm event-card"
      style={{ cursor: onClick ? 'pointer' : 'default', borderTop: `4px solid ${categoryColor}` }}
      onClick={onClick}
    >
      {images.length > 0 && (
        <div className="position-relative" style={{ height: '200px', overflow: 'hidden' }}>
          <img
            src={images[imageIndex]}
            className="card-img-top"
            alt={event.title}
            style={{
              height: '200px',
              objectFit: 'cover',
              transition: 'transform 0.3s ease'
            }}
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/800x600/607D8B/ffffff?text=No+Image';
            }}
          />

          {images.length > 1 && (
            <div className="position-absolute bottom-0 start-0 end-0 d-flex justify-content-center pb-2">
              {images.map((_, idx) => (
                <button
                  key={idx}
                  className="btn btn-sm mx-1"
                  style={{
                    width: '8px',
                    height: '8px',
                    borderRadius: '50%',
                    padding: 0,
                    backgroundColor: idx === imageIndex ? '#fff' : 'rgba(255,255,255,0.5)',
                    border: 'none'
                  }}
                  onClick={(e) => {
                    e.stopPropagation();
                    setImageIndex(idx);
                  }}
                />
              ))}
            </div>
          )}

          <span
            className="badge position-absolute top-0 end-0 m-2"
            style={{ backgroundColor: categoryColor }}
          >
            {event.category}
          </span>
        </div>
      )}

      <div className="card-body">
        <h5 className="card-title">{event.title}</h5>

        <div className="mb-2">
          <small className="text-muted">
            <i className="far fa-clock me-1"></i>
            {formatDate(event.date_start)}
          </small>
        </div>

        {event.venue && (
          <div className="mb-2">
            <small className="text-muted">
              <i className="fas fa-map-marker-alt me-1"></i>
              {event.venue}
            </small>
          </div>
        )}

        {event.price && (
          <div className="mb-2">
            <small className="text-success fw-bold">
              <i className="fas fa-tag me-1"></i>
              {event.price}
            </small>
          </div>
        )}

        <p className="card-text small" style={{
          display: '-webkit-box',
          WebkitLineClamp: 3,
          WebkitBoxOrient: 'vertical',
          overflow: 'hidden'
        }}>
          {event.description}
        </p>

        {event.source && (
          <div className="mt-2">
            <span className="badge bg-secondary small">{event.source}</span>
          </div>
        )}
      </div>
    </div>
  );
}
