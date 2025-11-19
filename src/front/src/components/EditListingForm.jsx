import React, { useState, useEffect } from 'react';
import LocationDropdown from './LocationDropdown';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function EditListingForm({ listing, token, onClose, onUpdated, userLocation }) {
  const [title, setTitle] = useState(listing.title);
  const [description, setDescription] = useState(listing.description || '');
  const [location, setLocation] = useState(listing.location || '');
  const [latitude, setLatitude] = useState(listing.latitude ?? '');
  const [longitude, setLongitude] = useState(listing.longitude ?? '');
  const [imageUrl, setImageUrl] = useState(listing.image_url || '');
  const [category, setCategory] = useState(listing.category || '');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showCoordinateHint, setShowCoordinateHint] = useState(false);

  const categories = ['Community', 'Environment', 'Education', 'Health', 'Animals'];

  const handleLocationSelect = (city) => {
    if (!city) return;
    setLocation(city.name);
    setLatitude(city.lat);
    setLongitude(city.lon);
    setShowCoordinateHint(true);
    setTimeout(() => setShowCoordinateHint(false), 3000);
  };

  async function handleSubmit(e) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const body = {
        title,
        description,
        location,
        image_url: imageUrl || null,
        category: category || null
      };

      // Only include lat/lng if both are provided
      if (latitude && longitude) {
        body.latitude = parseFloat(latitude);
        body.longitude = parseFloat(longitude);
      }

      const res = await fetch(`${API_URL}/listings/${listing.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.error || 'Failed to update listing');
      }

      const updated = await res.json();
      if (onUpdated) onUpdated(updated);
      onClose();
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="modal-overlay">
      <div className="modal-card" style={{ maxHeight: '90vh', overflowY: 'auto' }}>
        <header className="modal-header">
          <h2>Edit Listing</h2>
          <button className="close" onClick={onClose} aria-label="Close">
            ×
          </button>
        </header>

        <form onSubmit={handleSubmit} className="modal-body">
          {error && (
            <div className="error" role="alert">
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="edit-title">Title *</label>
            <input
              id="edit-title"
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-description">Description</label>
            <textarea
              id="edit-description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={4}
            />
          </div>

          <div className="form-group">
            <label htmlFor="edit-category">Category</label>
            <select
              id="edit-category"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              style={{
                width: '100%',
                padding: '10px 12px',
                fontSize: '14px',
                border: '1px solid #ddd',
                borderRadius: '6px',
                backgroundColor: 'white',
                cursor: 'pointer'
              }}
            >
              <option value="">-- Select a category --</option>
              {categories.map((cat) => (
                <option key={cat} value={cat}>{cat}</option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="edit-location">Location</label>
            <LocationDropdown
              value={location}
              onChange={(val) => setLocation(val)}
              onSelect={handleLocationSelect}
              userCoords={userLocation?.coords}
              placeholder="Enter location or select from list..."
            />
            {showCoordinateHint && latitude && longitude && (
              <small style={{ display: 'block', marginTop: '6px', color: '#28a745', fontWeight: '500' }}>
                ✓ Coordinates: {latitude.toFixed(4)}, {longitude.toFixed(4)}
              </small>
            )}
          </div>

          <div className="form-group">
            <label htmlFor="edit-image-url">Image URL</label>
            <input
              id="edit-image-url"
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
            />
            {imageUrl && (
              <div style={{
                marginTop: '8px',
                maxWidth: '200px',
                borderRadius: '6px',
                overflow: 'hidden',
                border: '1px solid #ddd'
              }}>
                <img
                  src={imageUrl}
                  alt="Preview"
                  style={{
                    width: '100%',
                    height: 'auto',
                    maxHeight: '150px',
                    objectFit: 'cover'
                  }}
                  onError={(e) => {
                    e.target.style.display = 'none';
                  }}
                />
              </div>
            )}
          </div>

          <details style={{ marginTop: '12px', padding: '12px', backgroundColor: '#f8f9fa', borderRadius: '6px', border: '1px solid #e9ecef' }}>
            <summary style={{ cursor: 'pointer', marginBottom: '8px', fontWeight: '600' }}>
              📍 Update map coordinates (optional)
            </summary>
            <div style={{ display: 'flex', gap: '8px', marginTop: '8px' }}>
              <div className="form-group" style={{ flex: 1, margin: 0 }}>
                <label htmlFor="edit-latitude">Latitude</label>
                <input
                  id="edit-latitude"
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  placeholder="e.g., 37.7749"
                />
              </div>
              <div className="form-group" style={{ flex: 1, margin: 0 }}>
                <label htmlFor="edit-longitude">Longitude</label>
                <input
                  id="edit-longitude"
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  placeholder="e.g., -122.4194"
                />
              </div>
            </div>
            <small style={{ display: 'block', marginTop: '4px', color: '#666' }}>
              Tip: Use{' '}
              <a
                href="https://www.latlong.net/"
                target="_blank"
                rel="noopener noreferrer"
                style={{ color: '#007bff' }}
              >
                latlong.net
              </a>{' '}
              to find coordinates
            </small>
          </details>

          <div className="form-actions">
            <button type="button" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="cta" disabled={loading}>
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
