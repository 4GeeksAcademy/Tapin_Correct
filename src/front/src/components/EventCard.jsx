import React, { useState } from 'react';
import { getCategoryByName, getCategoryColor } from '../config/categories';
import './EventCard.css';

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

  // Get category color from unified system
  const category = getCategoryByName(event.category);
  const categoryColor = category.color;

  return (
    <div
      className="card event-card"
      data-testid={`event-card-${event.id}`}
      style={{ cursor: onClick ? 'pointer' : 'default', borderTop: `4px solid ${categoryColor}` }}
      onClick={onClick}
    >
      {images.length > 0 && (
        <div className="event-card-image">
          <img
            src={images[imageIndex]}
            alt={event.title}
            className="event-card-img"
            onError={(e) => {
              e.target.src = 'https://via.placeholder.com/800x600/607D8B/ffffff?text=No+Image';
            }}
          />

          {images.length > 1 && (
            <div className="event-card-indicators">
              {images.map((_, idx) => (
                <button
                  key={idx}
                  className="event-card-indicator"
                  aria-label={`View image ${idx + 1}`}
                  style={{
                    backgroundColor: idx === imageIndex ? 'var(--white)' : 'rgba(255,255,255,0.5)',
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
            className="event-card-badge"
            style={{ backgroundColor: categoryColor }}
          >
            {event.category}
          </span>
        </div>
      )}

      <div className="event-card-body">
        <h3 className="event-card-title">{event.title}</h3>

        <div className="event-card-meta">
          <small className="text-muted">
            <i className="far fa-clock me-1"></i>
            {formatDate(event.date_start)}
          </small>
        </div>

        {event.venue && (
          <div className="event-card-meta">
            <small className="text-muted">
              <i className="fas fa-map-marker-alt me-1"></i>
              {event.venue}
            </small>
          </div>
        )}

        {event.price && (
          <div className="event-card-meta">
            <small style={{ color: 'var(--success)', fontWeight: 'var(--fw-bold)' }}>
              <i className="fas fa-tag me-1"></i>
              {event.price}
            </small>
          </div>
        )}

        <p className="event-card-description">
          {event.description}
        </p>

        {event.source && (
          <div className="event-card-source">
            <span className="event-card-source-badge">{event.source}</span>
          </div>
        )}

        {/* Volunteer Button - Shows if event has contact info */}
        {(event.contact_email || event.contact_phone || event.contact_person) && (
          <div className="event-card-actions">
            <button
              className="btn btn-primary"
              data-testid={`volunteer-btn-${event.id}`}
              onClick={(e) => {
                e.stopPropagation();
                // Show contact modal or expand contact info
                alert(`Volunteer Contact Info:\n\n${event.contact_person ? `Contact: ${event.contact_person}\n` : ''}${event.contact_email ? `Email: ${event.contact_email}\n` : ''}${event.contact_phone ? `Phone: ${event.contact_phone}` : ''}`);
              }}
            >
              <i className="fas fa-hands-helping me-2"></i>
              Volunteer for this Event
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
