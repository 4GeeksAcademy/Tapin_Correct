import React, { useState, useEffect, useRef } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Tinder-style Event Swiper
 *
 * Swipe right = Like/Interested
 * Swipe left = Not interested
 * Swipe up = Super like
 * Tap = View details
 */
export default function EventSwiper({ token, userLocation, onComplete }) {
  const [events, setEvents] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(false);
  const [animating, setAnimating] = useState(false);
  const [swipeDirection, setSwipeDirection] = useState(null);

  const cardRef = useRef(null);
  const startXRef = useRef(0);
  const startYRef = useRef(0);
  const isDraggingRef = useRef(false);

  useEffect(() => {
    if (userLocation && token) {
      loadEvents();
    }
  }, [userLocation, token]);

  async function loadEvents() {
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/api/events/personalized`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          location: userLocation,
          limit: 50
        })
      });

      if (res.ok) {
        const data = await res.json();
        setEvents(data.events || []);
        setCurrentIndex(0);
      }
    } catch (error) {
      console.error('Error loading events:', error);
    } finally {
      setLoading(false);
    }
  }

  async function recordInteraction(eventId, interactionType, swipeDir = null) {
    try {
      await fetch(`${API_URL}/api/events/interact`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          event_id: eventId,
          interaction_type: interactionType,
          metadata: {
            swipe_direction: swipeDir,
            timestamp: new Date().toISOString()
          }
        })
      });
    } catch (error) {
      console.error('Error recording interaction:', error);
    }
  }

  function handleSwipe(direction) {
    if (animating || currentIndex >= events.length) return;

    const currentEvent = events[currentIndex];
    setSwipeDirection(direction);
    setAnimating(true);

    // Record interaction
    const interactionMap = {
      'left': 'dislike',
      'right': 'like',
      'up': 'super_like',
      'down': 'skip'
    };

    recordInteraction(currentEvent.id, interactionMap[direction], direction);

    // Animate out and move to next
    setTimeout(() => {
      setCurrentIndex(currentIndex + 1);
      setSwipeDirection(null);
      setAnimating(false);

      // Check if completed
      if (currentIndex + 1 >= events.length) {
        if (onComplete) onComplete();
      }
    }, 300);
  }

  function handleTouchStart(e) {
    startXRef.current = e.touches[0].clientX;
    startYRef.current = e.touches[0].clientY;
    isDraggingRef.current = true;
  }

  function handleTouchMove(e) {
    if (!isDraggingRef.current || !cardRef.current) return;

    const currentX = e.touches[0].clientX;
    const currentY = e.touches[0].clientY;
    const diffX = currentX - startXRef.current;
    const diffY = currentY - startYRef.current;

    // Apply transform
    cardRef.current.style.transform = `translate(${diffX}px, ${diffY}px) rotate(${diffX * 0.1}deg)`;

    // Update opacity based on direction
    const opacity = 1 - Math.abs(diffX) / 300;
    cardRef.current.style.opacity = Math.max(0.5, opacity);
  }

  function handleTouchEnd(e) {
    if (!isDraggingRef.current || !cardRef.current) return;

    const endX = e.changedTouches[0].clientX;
    const endY = e.changedTouches[0].clientY;
    const diffX = endX - startXRef.current;
    const diffY = endY - startYRef.current;

    isDraggingRef.current = false;

    // Reset transform
    cardRef.current.style.transform = '';
    cardRef.current.style.opacity = '1';

    // Determine swipe direction
    const threshold = 100;

    if (Math.abs(diffX) > threshold) {
      if (diffX > 0) {
        handleSwipe('right');
      } else {
        handleSwipe('left');
      }
    } else if (Math.abs(diffY) > threshold && diffY < 0) {
      handleSwipe('up'); // Super like
    } else {
      // No significant swipe, reset position
      cardRef.current.style.transition = 'transform 0.2s';
      setTimeout(() => {
        if (cardRef.current) {
          cardRef.current.style.transition = '';
        }
      }, 200);
    }
  }

  if (loading) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary mb-3"></div>
        <p>Loading events...</p>
      </div>
    );
  }

  if (events.length === 0) {
    return (
      <div className="text-center py-5">
        <div className="display-1 mb-3">🎉</div>
        <h3>No more events!</h3>
        <p className="text-muted">Check back later for new discoveries</p>
        <button className="btn btn-primary mt-3" onClick={loadEvents}>
          <i className="fas fa-sync me-2"></i>
          Refresh
        </button>
      </div>
    );
  }

  if (currentIndex >= events.length) {
    return (
      <div className="text-center py-5">
        <div className="display-1 mb-3">✨</div>
        <h3>You've seen all events!</h3>
        <p className="text-muted">Great job exploring!</p>
        <button className="btn btn-primary mt-3" onClick={loadEvents}>
          <i className="fas fa-sync me-2"></i>
          Load More
        </button>
      </div>
    );
  }

  const currentEvent = events[currentIndex];
  const remainingCount = events.length - currentIndex;

  return (
    <div className="event-swiper">
      {/* Counter */}
      <div className="text-center mb-3">
        <span className="badge bg-secondary">
          {currentIndex + 1} / {events.length}
        </span>
      </div>

      {/* Swipe cards stack */}
      <div className="swipe-container">
        {/* Next card (background) */}
        {currentIndex + 1 < events.length && (
          <div className="swipe-card swipe-card-next">
            <img
              src={events[currentIndex + 1].image_url || 'https://via.placeholder.com/400x600/607D8B/fff?text=Event'}
              alt="Next event"
            />
          </div>
        )}

        {/* Current card */}
        <div
          ref={cardRef}
          className={`swipe-card swipe-card-current ${animating ? `swipe-${swipeDirection}` : ''}`}
          onTouchStart={handleTouchStart}
          onTouchMove={handleTouchMove}
          onTouchEnd={handleTouchEnd}
        >
          <img
            src={currentEvent.image_url || 'https://via.placeholder.com/400x600/667eea/fff?text=Event'}
            alt={currentEvent.title}
            className="swipe-card-image"
          />

          <div className="swipe-card-content">
            <h3 className="swipe-card-title">{currentEvent.title}</h3>

            {currentEvent.match_score && (
              <div className="match-badge">
                <span className="badge bg-success">
                  {currentEvent.match_score}% Match
                </span>
              </div>
            )}

            <div className="swipe-card-details">
              {currentEvent.venue && (
                <div className="mb-2">
                  <i className="fas fa-map-marker-alt me-2"></i>
                  <small>{currentEvent.venue}</small>
                </div>
              )}

              {currentEvent.date_start && (
                <div className="mb-2">
                  <i className="far fa-clock me-2"></i>
                  <small>{new Date(currentEvent.date_start).toLocaleDateString()}</small>
                </div>
              )}

              {currentEvent.price && (
                <div className="mb-2">
                  <i className="fas fa-tag me-2"></i>
                  <small className="text-success fw-bold">{currentEvent.price}</small>
                </div>
              )}

              <span className="badge" style={{
                backgroundColor: currentEvent.category_color || '#667eea'
              }}>
                {currentEvent.category}
              </span>
            </div>

            {currentEvent.match_explanation && (
              <div className="mt-3">
                <small className="text-muted">
                  <i className="fas fa-lightbulb me-1"></i>
                  {currentEvent.match_explanation}
                </small>
              </div>
            )}
          </div>

          {/* Swipe indicators */}
          <div className="swipe-indicator swipe-indicator-left">
            <i className="fas fa-times"></i>
          </div>
          <div className="swipe-indicator swipe-indicator-right">
            <i className="fas fa-heart"></i>
          </div>
          <div className="swipe-indicator swipe-indicator-up">
            <i className="fas fa-star"></i>
          </div>
        </div>
      </div>

      {/* Action buttons */}
      <div className="swipe-actions mt-4">
        <button
          className="swipe-btn swipe-btn-dislike"
          onClick={() => handleSwipe('left')}
          disabled={animating}
        >
          <i className="fas fa-times"></i>
        </button>

        <button
          className="swipe-btn swipe-btn-superlike"
          onClick={() => handleSwipe('up')}
          disabled={animating}
        >
          <i className="fas fa-star"></i>
        </button>

        <button
          className="swipe-btn swipe-btn-like"
          onClick={() => handleSwipe('right')}
          disabled={animating}
        >
          <i className="fas fa-heart"></i>
        </button>
      </div>

      <style jsx>{`
        .event-swiper {
          max-width: 500px;
          margin: 0 auto;
          padding: 20px;
        }

        .swipe-container {
          position: relative;
          height: 600px;
          margin-bottom: 20px;
        }

        .swipe-card {
          position: absolute;
          width: 100%;
          height: 100%;
          background: white;
          border-radius: 20px;
          box-shadow: 0 10px 30px rgba(0,0,0,0.2);
          overflow: hidden;
          cursor: grab;
          user-select: none;
          -webkit-user-select: none;
        }

        .swipe-card:active {
          cursor: grabbing;
        }

        .swipe-card-next {
          transform: scale(0.95);
          opacity: 0.8;
          z-index: 1;
        }

        .swipe-card-current {
          z-index: 2;
          transition: none;
        }

        .swipe-card.swipe-left {
          animation: swipeLeft 0.3s forwards;
        }

        .swipe-card.swipe-right {
          animation: swipeRight 0.3s forwards;
        }

        .swipe-card.swipe-up {
          animation: swipeUp 0.3s forwards;
        }

        @keyframes swipeLeft {
          to {
            transform: translateX(-150%) rotate(-30deg);
            opacity: 0;
          }
        }

        @keyframes swipeRight {
          to {
            transform: translateX(150%) rotate(30deg);
            opacity: 0;
          }
        }

        @keyframes swipeUp {
          to {
            transform: translateY(-150%) scale(1.1);
            opacity: 0;
          }
        }

        .swipe-card-image {
          width: 100%;
          height: 400px;
          object-fit: cover;
        }

        .swipe-card-content {
          padding: 20px;
          background: linear-gradient(to bottom, transparent, rgba(0,0,0,0.7));
          position: absolute;
          bottom: 0;
          left: 0;
          right: 0;
          color: white;
        }

        .swipe-card-title {
          font-size: 1.5rem;
          font-weight: bold;
          margin-bottom: 10px;
          text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .match-badge {
          margin-bottom: 10px;
        }

        .swipe-card-details {
          margin-bottom: 10px;
        }

        .swipe-indicator {
          position: absolute;
          top: 50px;
          font-size: 4rem;
          opacity: 0;
          transition: opacity 0.2s;
          pointer-events: none;
        }

        .swipe-indicator-left {
          left: 50px;
          color: #ff4458;
        }

        .swipe-indicator-right {
          right: 50px;
          color: #2ecc71;
        }

        .swipe-indicator-up {
          top: 50px;
          left: 50%;
          transform: translateX(-50%);
          color: #f39c12;
        }

        .swipe-actions {
          display: flex;
          justify-content: center;
          gap: 20px;
        }

        .swipe-btn {
          width: 60px;
          height: 60px;
          border-radius: 50%;
          border: none;
          font-size: 1.5rem;
          cursor: pointer;
          transition: transform 0.2s, box-shadow 0.2s;
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }

        .swipe-btn:hover:not(:disabled) {
          transform: scale(1.1);
          box-shadow: 0 6px 12px rgba(0,0,0,0.3);
        }

        .swipe-btn:disabled {
          opacity: 0.5;
          cursor: not-allowed;
        }

        .swipe-btn-dislike {
          background: linear-gradient(135deg, #ff4458 0%, #ff1744 100%);
          color: white;
        }

        .swipe-btn-like {
          background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
          color: white;
        }

        .swipe-btn-superlike {
          background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
          color: white;
          width: 70px;
          height: 70px;
          font-size: 1.8rem;
        }

        @media (max-width: 768px) {
          .swipe-container {
            height: 500px;
          }

          .swipe-card-image {
            height: 300px;
          }
        }
      `}</style>
    </div>
  );
}
