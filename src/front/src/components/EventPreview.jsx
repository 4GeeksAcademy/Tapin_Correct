import React, { useState } from 'react';

/**
 * Immersive Event Preview Component
 *
 * Multi-sensory event discovery with:
 * - Image gallery
 * - Venue street view
 * - Similar events
 * - User-generated content
 */
export default function EventPreview({ event, onClose }) {
  const [activeTab, setActiveTab] = useState('photos');
  const [currentImageIndex, setCurrentImageIndex] = useState(0);

  const images = event.image_urls
    ? (typeof event.image_urls === 'string' ? JSON.parse(event.image_urls) : event.image_urls)
    : (event.image_url ? [event.image_url] : []);

  const tabs = [
    { id: 'photos', label: 'Photos', icon: '📷' },
    { id: 'venue', label: 'Venue', icon: '🏛️' },
    { id: 'vibe', label: 'Vibe', icon: '🎵' },
    { id: 'reviews', label: 'Reviews', icon: '⭐' },
  ];

  function nextImage() {
    setCurrentImageIndex((currentImageIndex + 1) % images.length);
  }

  function prevImage() {
    setCurrentImageIndex((currentImageIndex - 1 + images.length) % images.length);
  }

  return (
    <div className="event-preview-modal">
      <div className="modal-backdrop" onClick={onClose}></div>

      <div className="modal-content">
        {/* Header */}
        <div className="modal-header">
          <h4 className="mb-0">{event.title}</h4>
          <button className="btn-close" onClick={onClose}></button>
        </div>

        {/* Tab navigation */}
        <div className="preview-tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={`preview-tab ${activeTab === tab.id ? 'active' : ''}`}
              onClick={() => setActiveTab(tab.id)}
            >
              <span className="tab-icon">{tab.icon}</span>
              <span className="tab-label">{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Content */}
        <div className="preview-content">
          {/* Photos tab */}
          {activeTab === 'photos' && (
            <div className="photos-tab">
              {images.length > 0 ? (
                <div className="image-gallery">
                  <div className="main-image">
                    <img
                      src={images[currentImageIndex]}
                      alt={`${event.title} - Photo ${currentImageIndex + 1}`}
                      className="gallery-image"
                    />

                    {images.length > 1 && (
                      <>
                        <button className="gallery-btn gallery-btn-prev" onClick={prevImage}>
                          <i className="fas fa-chevron-left"></i>
                        </button>
                        <button className="gallery-btn gallery-btn-next" onClick={nextImage}>
                          <i className="fas fa-chevron-right"></i>
                        </button>

                        <div className="gallery-indicators">
                          {images.map((_, idx) => (
                            <button
                              key={idx}
                              className={`gallery-dot ${idx === currentImageIndex ? 'active' : ''}`}
                              onClick={() => setCurrentImageIndex(idx)}
                            />
                          ))}
                        </div>
                      </>
                    )}
                  </div>

                  {/* Thumbnail strip */}
                  {images.length > 1 && (
                    <div className="thumbnail-strip">
                      {images.map((img, idx) => (
                        <img
                          key={idx}
                          src={img}
                          alt={`Thumbnail ${idx + 1}`}
                          className={`thumbnail ${idx === currentImageIndex ? 'active' : ''}`}
                          onClick={() => setCurrentImageIndex(idx)}
                        />
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="empty-state">
                  <i className="fas fa-images mb-3" style={{ fontSize: '3rem' }}></i>
                  <p>No photos available</p>
                </div>
              )}
            </div>
          )}

          {/* Venue tab */}
          {activeTab === 'venue' && (
            <div className="venue-tab">
              {event.venue ? (
                <>
                  <div className="venue-info mb-3">
                    <h5>{event.venue}</h5>
                    {event.location_address && (
                      <p className="text-muted mb-2">
                        <i className="fas fa-map-marker-alt me-2"></i>
                        {event.location_address}
                      </p>
                    )}
                  </div>

                  {/* Google Street View embed (would need actual coordinates) */}
                  <div className="street-view-container">
                    <div className="street-view-placeholder">
                      <i className="fas fa-street-view mb-3" style={{ fontSize: '3rem' }}></i>
                      <p>360° Street View</p>
                      <small className="text-muted">
                        See the venue from outside
                      </small>
                    </div>
                  </div>

                  {/* Venue amenities */}
                  <div className="venue-amenities mt-3">
                    <h6>Amenities</h6>
                    <div className="amenity-grid">
                      <div className="amenity-item">
                        <i className="fas fa-parking"></i>
                        <span>Parking</span>
                      </div>
                      <div className="amenity-item">
                        <i className="fas fa-wheelchair"></i>
                        <span>Accessible</span>
                      </div>
                      <div className="amenity-item">
                        <i className="fas fa-wifi"></i>
                        <span>WiFi</span>
                      </div>
                      <div className="amenity-item">
                        <i className="fas fa-utensils"></i>
                        <span>Food</span>
                      </div>
                    </div>
                  </div>
                </>
              ) : (
                <div className="empty-state">
                  <p>Venue information not available</p>
                </div>
              )}
            </div>
          )}

          {/* Vibe tab */}
          {activeTab === 'vibe' && (
            <div className="vibe-tab">
              <div className="mb-3">
                <h5>Event Vibe</h5>
                <p className="text-muted">Get a feel for the atmosphere</p>
              </div>

              {/* Music/Playlist preview */}
              <div className="vibe-section">
                <div className="vibe-card">
                  <i className="fas fa-music mb-2" style={{ fontSize: '2rem', color: '#1DB954' }}></i>
                  <h6>Music Vibe</h6>
                  <p className="small text-muted">Curated playlist matching this event</p>
                  <button className="btn btn-sm btn-outline-success">
                    <i className="fab fa-spotify me-2"></i>
                    Listen on Spotify
                  </button>
                </div>

                {/* Mood indicators */}
                <div className="mood-indicators mt-3">
                  <h6>Atmosphere</h6>
                  <div className="mood-tags">
                    <span className="mood-tag">⚡ Energetic</span>
                    <span className="mood-tag">👥 Social</span>
                    <span className="mood-tag">🎉 Fun</span>
                  </div>
                </div>
              </div>

              {/* Past event highlights (if available) */}
              <div className="highlights-section mt-3">
                <h6>Past Event Highlights</h6>
                <div className="highlight-placeholder">
                  <i className="fas fa-video mb-2" style={{ fontSize: '2rem' }}></i>
                  <p className="small">Video highlights from similar events</p>
                </div>
              </div>
            </div>
          )}

          {/* Reviews tab */}
          {activeTab === 'reviews' && (
            <div className="reviews-tab">
              <div className="review-summary mb-3">
                <div className="rating-display">
                  <span className="rating-number">4.5</span>
                  <div className="stars">
                    <i className="fas fa-star"></i>
                    <i className="fas fa-star"></i>
                    <i className="fas fa-star"></i>
                    <i className="fas fa-star"></i>
                    <i className="fas fa-star-half-alt"></i>
                  </div>
                  <p className="text-muted small mb-0">Based on past events</p>
                </div>
              </div>

              {/* Sample reviews */}
              <div className="reviews-list">
                {[1, 2, 3].map((idx) => (
                  <div key={idx} className="review-card mb-3">
                    <div className="d-flex align-items-start mb-2">
                      <img
                        src={`https://i.pravatar.cc/40?img=${idx}`}
                        alt="Reviewer"
                        className="review-avatar me-2"
                      />
                      <div className="flex-grow-1">
                        <div className="fw-bold small">User {idx}</div>
                        <div className="stars-small">
                          {'★'.repeat(5)}
                        </div>
                      </div>
                      <small className="text-muted">2w ago</small>
                    </div>
                    <p className="small mb-0">
                      "Amazing event! Great atmosphere and met lots of interesting people. Would definitely recommend!"
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Footer actions */}
        <div className="modal-footer">
          <button className="btn btn-outline-secondary" onClick={onClose}>
            Close
          </button>
          <button className="btn btn-primary">
            <i className="fas fa-heart me-2"></i>
            I'm Interested
          </button>
        </div>
      </div>

      <style jsx>{`
        .event-preview-modal {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          z-index: 1050;
          display: flex;
          align-items: center;
          justify-content: center;
          padding: 20px;
        }

        .modal-backdrop {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.7);
          backdrop-filter: blur(4px);
        }

        .modal-content {
          position: relative;
          background: white;
          border-radius: 20px;
          max-width: 800px;
          width: 100%;
          max-height: 90vh;
          overflow: hidden;
          display: flex;
          flex-direction: column;
          animation: slideUp 0.3s ease-out;
        }

        @keyframes slideUp {
          from {
            transform: translateY(50px);
            opacity: 0;
          }
          to {
            transform: translateY(0);
            opacity: 1;
          }
        }

        .modal-header {
          padding: 20px;
          border-bottom: 1px solid #eee;
          display: flex;
          align-items: center;
          justify-content: space-between;
        }

        .preview-tabs {
          display: flex;
          border-bottom: 1px solid #eee;
          padding: 0 20px;
        }

        .preview-tab {
          flex: 1;
          padding: 15px 10px;
          background: none;
          border: none;
          border-bottom: 3px solid transparent;
          cursor: pointer;
          transition: all 0.2s;
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 5px;
        }

        .preview-tab.active {
          border-bottom-color: #667eea;
          color: #667eea;
        }

        .tab-icon {
          font-size: 1.5rem;
        }

        .tab-label {
          font-size: 0.875rem;
          font-weight: 500;
        }

        .preview-content {
          flex: 1;
          overflow-y: auto;
          padding: 20px;
        }

        .main-image {
          position: relative;
          width: 100%;
          height: 400px;
          background: #f0f0f0;
          border-radius: 12px;
          overflow: hidden;
        }

        .gallery-image {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .gallery-btn {
          position: absolute;
          top: 50%;
          transform: translateY(-50%);
          background: rgba(0, 0, 0, 0.5);
          color: white;
          border: none;
          width: 40px;
          height: 40px;
          border-radius: 50%;
          cursor: pointer;
          transition: background 0.2s;
        }

        .gallery-btn:hover {
          background: rgba(0, 0, 0, 0.7);
        }

        .gallery-btn-prev {
          left: 10px;
        }

        .gallery-btn-next {
          right: 10px;
        }

        .gallery-indicators {
          position: absolute;
          bottom: 10px;
          left: 50%;
          transform: translateX(-50%);
          display: flex;
          gap: 8px;
        }

        .gallery-dot {
          width: 8px;
          height: 8px;
          border-radius: 50%;
          background: rgba(255, 255, 255, 0.5);
          border: none;
          cursor: pointer;
          transition: all 0.2s;
        }

        .gallery-dot.active {
          background: white;
          width: 24px;
          border-radius: 4px;
        }

        .thumbnail-strip {
          display: flex;
          gap: 10px;
          margin-top: 15px;
          overflow-x: auto;
        }

        .thumbnail {
          width: 80px;
          height: 80px;
          border-radius: 8px;
          object-fit: cover;
          cursor: pointer;
          opacity: 0.6;
          transition: opacity 0.2s;
        }

        .thumbnail:hover,
        .thumbnail.active {
          opacity: 1;
        }

        .empty-state {
          text-align: center;
          padding: 60px 20px;
          color: #999;
        }

        .street-view-placeholder {
          height: 300px;
          background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
          border-radius: 12px;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: #667eea;
        }

        .amenity-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 15px;
        }

        .amenity-item {
          text-align: center;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .amenity-item i {
          font-size: 1.5rem;
          color: #667eea;
          display: block;
          margin-bottom: 8px;
        }

        .amenity-item span {
          font-size: 0.875rem;
        }

        .vibe-card {
          text-align: center;
          padding: 30px;
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          border-radius: 12px;
        }

        .mood-tags {
          display: flex;
          gap: 10px;
          flex-wrap: wrap;
        }

        .mood-tag {
          padding: 8px 16px;
          background: #667eea20;
          color: #667eea;
          border-radius: 20px;
          font-size: 0.875rem;
          font-weight: 500;
        }

        .highlight-placeholder {
          text-align: center;
          padding: 40px;
          background: #f8f9fa;
          border-radius: 12px;
          color: #999;
        }

        .rating-display {
          text-align: center;
          padding: 20px;
          background: #f8f9fa;
          border-radius: 12px;
        }

        .rating-number {
          font-size: 3rem;
          font-weight: bold;
          color: #667eea;
          display: block;
          margin-bottom: 10px;
        }

        .stars {
          color: #FFD700;
          font-size: 1.2rem;
          margin-bottom: 5px;
        }

        .review-card {
          padding: 15px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .review-avatar {
          width: 40px;
          height: 40px;
          border-radius: 50%;
        }

        .stars-small {
          color: #FFD700;
          font-size: 0.875rem;
        }

        .modal-footer {
          padding: 20px;
          border-top: 1px solid #eee;
          display: flex;
          gap: 10px;
          justify-content: flex-end;
        }

        @media (max-width: 768px) {
          .amenity-grid {
            grid-template-columns: repeat(2, 1fr);
          }

          .main-image {
            height: 250px;
          }
        }
      `}</style>
    </div>
  );
}
