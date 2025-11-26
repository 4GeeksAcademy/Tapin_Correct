import React, { useState, useEffect } from 'react';
import { API_URL } from '../lib/api';
import './ListingCard.css';

export default function ListingCard({ listing = {}, onOpen, onSelect }) {
  const { title, description, image_url, location, id, category } = listing;
  const [averageRating, setAverageRating] = useState(null);
  const [reviewCount, setReviewCount] = useState(0);

  useEffect(() => {
    if (!id) return;

    async function fetchRating() {
      try {
        const [ratingRes, reviewsRes] = await Promise.all([
          fetch(`${API_URL}/listings/${id}/average-rating`),
          fetch(`${API_URL}/listings/${id}/reviews`),
        ]);

        if (ratingRes.ok) {
          const ratingData = await ratingRes.json();
          setAverageRating(ratingData.average_rating);
        }

        if (reviewsRes.ok) {
          const reviewsData = await reviewsRes.json();
          const count = Array.isArray(reviewsData)
            ? reviewsData.length
            : (reviewsData?.reviews?.length || 0);
          setReviewCount(count);
        }
      } catch (err) {
        console.error('Error fetching rating:', err);
      }
    }

    fetchRating();
  }, [id]);

  // Category styling - updated to use design system colors
  const getCategoryColor = (cat) => {
    const colors = {
      'Community': 'var(--primary)',
      'Environment': 'var(--success)',
      'Education': 'var(--info)',
      'Health': 'var(--error)',
      'Animals': 'var(--warning)',
    };
    return colors[cat] || 'var(--text-secondary)';
  };

  return (
    <article className="card listing-card" role="article" aria-label={title || 'Listing'}>
      <div className="listing-card-media" aria-hidden={image_url ? 'false' : 'true'}>
        {image_url ? (
          <img src={image_url} alt={title || 'Listing image'} loading="lazy" className="listing-card-img" />
        ) : (
          <div className="listing-card-placeholder" aria-hidden="true">
            📷
          </div>
        )}
        {category && (
          <div
            className="listing-card-category"
            style={{
              backgroundColor: getCategoryColor(category),
            }}
          >
            {category}
          </div>
        )}
      </div>

      <div className="listing-card-content">
        <h3 className="listing-card-title">{title || 'Untitled listing'}</h3>

        {averageRating !== null && (
          <div className="listing-card-rating">
            <span className="listing-card-star">★</span>
            <span className="listing-card-score">{averageRating.toFixed(1)}</span>
            <span className="listing-card-count">({reviewCount})</span>
          </div>
        )}

        <p className="listing-card-description">{description || 'No description provided.'}</p>

        {location && (
          <div className="listing-card-location">
            <span>📍</span> {location}
          </div>
        )}
      </div>

      <div className="listing-card-footer">
        <button
          className="btn btn-primary"
          onClick={() => {
            if (typeof onSelect === 'function') return onSelect(listing);
            if (typeof onOpen === 'function') return onOpen(listing);
          }}
        >
          View Details
        </button>
      </div>
    </article>
  );
}
