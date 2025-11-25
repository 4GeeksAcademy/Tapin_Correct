import React, { useState } from 'react';

export default function ReviewForm({ listing, token, onClose, onReviewAdded }) {
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [hoveredRating, setHoveredRating] = useState(0);

  // Get panda feedback based on rating
  const getPandaFeedback = (rating) => {
    if (rating <= 2) {
      return {
        emoji: '😢🐼',
        message: "We're sorry this experience didn't meet expectations. Your feedback helps us improve!",
        color: '#FF9D42',  // Orange - attention needed
        bgColor: '#FFF3E0'
      };
    } else if (rating === 3) {
      return {
        emoji: '🐼',
        message: "Thank you for your honest feedback. We appreciate your thoughts!",
        color: '#17B8A3',  // Teal - neutral
        bgColor: '#E0F7F4'
      };
    } else {
      return {
        emoji: '🐼✨',
        message: "Thank you for your positive feedback! Together we build stronger communities.",
        color: '#10b981',  // Green - success
        bgColor: '#ECFDF5'
      };
    }
  };

  const pandaFeedback = getPandaFeedback(hoveredRating || rating);

  async function handleSubmit(e) {
    e.preventDefault();

    if (!token) {
      setError('Please log in to submit a review');
      return;
    }

    if (rating < 1 || rating > 5) {
      setError('Rating must be between 1 and 5 stars');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await fetch(`http://127.0.0.1:5000/listings/${listing.id}/reviews`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ rating, comment }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to submit review');
      }

      const newReview = await res.json();
      if (onReviewAdded) onReviewAdded(newReview);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="detail-overlay" role="dialog" aria-modal="true">
      <div className="detail-card" style={{ maxWidth: '500px' }}>
        <header className="detail-header">
          <h2>Review: {listing.title}</h2>
          <button className="close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit}>
          <div className="detail-body">
            <div style={{ marginBottom: '20px', position: 'relative' }}>
              <label
                htmlFor="rating-input"
                style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}
              >
                Rating
              </label>
              <input
                type="number"
                id="rating-input"
                value={rating}
                readOnly
                tabIndex={-1}
                style={{
                  position: 'absolute',
                  opacity: 0,
                  pointerEvents: 'none',
                  height: 0,
                  width: 0,
                }}
              />
              <div style={{ display: 'flex', gap: '4px', fontSize: '32px' }}>
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    onClick={() => setRating(star)}
                    onMouseEnter={() => setHoveredRating(star)}
                    onMouseLeave={() => setHoveredRating(0)}
                    style={{
                      background: 'none',
                      border: 'none',
                      cursor: 'pointer',
                      padding: 0,
                      color: star <= (hoveredRating || rating) ? '#ffc107' : '#e0e0e0',
                      transition: 'color 0.2s',
                    }}
                    aria-label={`${star} star${star !== 1 ? 's' : ''}`}
                  >
                    ★
                  </button>
                ))}
              </div>
              <p style={{ marginTop: '8px', color: '#666', fontSize: '14px' }}>
                {rating} star{rating !== 1 ? 's' : ''}
              </p>

              {/* Panda Feedback based on rating */}
              <div style={{
                marginTop: '16px',
                padding: '16px',
                backgroundColor: pandaFeedback.bgColor,
                borderRadius: '12px',
                borderLeft: `4px solid ${pandaFeedback.color}`,
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
                transition: 'all 0.3s ease'
              }}>
                <div style={{ fontSize: '2rem', flexShrink: 0 }}>
                  {pandaFeedback.emoji}
                </div>
                <p style={{
                  margin: 0,
                  color: '#2F3E46',
                  fontSize: '14px',
                  lineHeight: '1.5'
                }}>
                  {pandaFeedback.message}
                </p>
              </div>
            </div>

            <div>
              <label
                htmlFor="comment"
                style={{ display: 'block', marginBottom: '8px', fontWeight: 'bold' }}
              >
                Comment (optional)
              </label>
              <textarea
                id="comment"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Share your experience with this listing..."
                rows={5}
                style={{
                  width: '100%',
                  padding: '8px',
                  borderRadius: '4px',
                  border: '1px solid #ccc',
                  fontFamily: 'inherit',
                  fontSize: '14px',
                }}
                maxLength={500}
              />
              <p style={{ textAlign: 'right', color: '#666', fontSize: '12px', marginTop: '4px' }}>
                {comment.length}/500
              </p>
            </div>

            {error && (
              <div className="error" role="alert" style={{ marginTop: '16px' }}>
                {error}
              </div>
            )}
          </div>

          <footer className="detail-footer">
            <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
              <button type="button" onClick={onClose} disabled={loading}>
                Cancel
              </button>
              <button type="submit" className="cta" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Review'}
              </button>
            </div>
          </footer>
        </form>
      </div>
    </div>
  );
}
