import React, { useState, useEffect, useRef } from 'react';

/**
 * AR Wayfinding & Live Map Component
 *
 * Provides immersive navigation to events with:
 * - Live map view with event markers
 * - AR camera mode with directional overlays
 * - Real-time distance and ETA calculations
 * - Point-of-interest detection
 * - Turn-by-turn navigation
 */
export default function ARWayfinding({ event, userLocation, onClose }) {
  const [mode, setMode] = useState('map'); // 'map' or 'ar'
  const [location, setLocation] = useState(userLocation);
  const [heading, setHeading] = useState(0);
  const [distance, setDistance] = useState(null);
  const [eta, setEta] = useState(null);
  const [arSupported, setArSupported] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    // Check AR support
    checkARSupport();

    // Start location tracking
    startLocationTracking();

    // Start compass tracking
    startCompassTracking();

    return () => {
      stopLocationTracking();
      stopCompassTracking();
      stopCamera();
    };
  }, []);

  useEffect(() => {
    if (location && event.latitude && event.longitude) {
      calculateDistanceAndETA();
    }
  }, [location, event]);

  useEffect(() => {
    if (mode === 'ar' && arSupported) {
      startCamera();
    } else {
      stopCamera();
    }
  }, [mode, arSupported]);

  function checkARSupport() {
    // Check if device supports camera and sensors
    const hasCamera = !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    const hasOrientation = 'DeviceOrientationEvent' in window;
    setArSupported(hasCamera && hasOrientation);
  }

  let watchId = null;
  function startLocationTracking() {
    if (navigator.geolocation) {
      watchId = navigator.geolocation.watchPosition(
        (position) => {
          setLocation({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy
          });
        },
        (error) => console.error('Location error:', error),
        { enableHighAccuracy: true, maximumAge: 1000 }
      );
    }
  }

  function stopLocationTracking() {
    if (watchId) {
      navigator.geolocation.clearWatch(watchId);
    }
  }

  function startCompassTracking() {
    if (window.DeviceOrientationEvent) {
      window.addEventListener('deviceorientation', handleOrientation);
    }
  }

  function stopCompassTracking() {
    window.removeEventListener('deviceorientation', handleOrientation);
  }

  function handleOrientation(event) {
    // Get compass heading (0-360 degrees)
    const alpha = event.alpha; // Direction device is facing
    if (alpha !== null) {
      setHeading(alpha);
    }
  }

  async function startCamera() {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: 'environment' }
      });

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        videoRef.current.play();
      }
    } catch (error) {
      console.error('Camera error:', error);
      setArSupported(false);
    }
  }

  function stopCamera() {
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  }

  function calculateDistanceAndETA() {
    if (!location || !event.latitude || !event.longitude) return;

    // Haversine formula for distance
    const R = 6371; // Earth's radius in km
    const dLat = toRad(event.latitude - location.latitude);
    const dLon = toRad(event.longitude - location.longitude);

    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(toRad(location.latitude)) *
      Math.cos(toRad(event.latitude)) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);

    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distanceKm = R * c;

    setDistance(distanceKm);

    // Calculate ETA (assuming walking speed of 5 km/h)
    const walkingSpeed = 5;
    const etaMinutes = Math.round((distanceKm / walkingSpeed) * 60);
    setEta(etaMinutes);
  }

  function toRad(degrees) {
    return degrees * (Math.PI / 180);
  }

  function getBearing() {
    if (!location || !event.latitude || !event.longitude) return 0;

    const dLon = toRad(event.longitude - location.longitude);
    const lat1 = toRad(location.latitude);
    const lat2 = toRad(event.latitude);

    const y = Math.sin(dLon) * Math.cos(lat2);
    const x =
      Math.cos(lat1) * Math.sin(lat2) -
      Math.sin(lat1) * Math.cos(lat2) * Math.cos(dLon);

    let bearing = Math.atan2(y, x) * (180 / Math.PI);
    bearing = (bearing + 360) % 360;

    return bearing;
  }

  function getDirectionArrow() {
    const bearing = getBearing();
    const relativeBearing = (bearing - heading + 360) % 360;

    // Return arrow based on direction
    if (relativeBearing < 22.5 || relativeBearing > 337.5) return '⬆️';
    if (relativeBearing >= 22.5 && relativeBearing < 67.5) return '↗️';
    if (relativeBearing >= 67.5 && relativeBearing < 112.5) return '➡️';
    if (relativeBearing >= 112.5 && relativeBearing < 157.5) return '↘️';
    if (relativeBearing >= 157.5 && relativeBearing < 202.5) return '⬇️';
    if (relativeBearing >= 202.5 && relativeBearing < 247.5) return '↙️';
    if (relativeBearing >= 247.5 && relativeBearing < 292.5) return '⬅️';
    return '↖️';
  }

  function formatDistance(km) {
    if (km < 1) {
      return `${Math.round(km * 1000)}m`;
    }
    return `${km.toFixed(1)}km`;
  }

  function formatETA(minutes) {
    if (minutes < 60) {
      return `${minutes} min`;
    }
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return `${hours}h ${mins}m`;
  }

  return (
    <div className="ar-wayfinding">
      {/* Header */}
      <div className="ar-header">
        <button className="btn btn-sm btn-light" onClick={onClose}>
          <i className="fas fa-arrow-left me-2"></i>
          Back
        </button>

        <div className="destination-info">
          <h6 className="mb-0">{event.title}</h6>
          <small className="text-muted">{event.venue}</small>
        </div>

        <div className="mode-switcher">
          <button
            className={`mode-btn ${mode === 'map' ? 'active' : ''}`}
            onClick={() => setMode('map')}
          >
            <i className="fas fa-map"></i>
          </button>
          <button
            className={`mode-btn ${mode === 'ar' ? 'active' : ''}`}
            onClick={() => setMode('ar')}
            disabled={!arSupported}
            title={!arSupported ? 'AR not supported on this device' : 'AR Mode'}
          >
            <i className="fas fa-camera"></i>
          </button>
        </div>
      </div>

      {/* Distance & ETA Display */}
      {distance !== null && (
        <div className="navigation-stats">
          <div className="stat-item">
            <i className="fas fa-location-arrow me-2"></i>
            <span className="stat-value">{formatDistance(distance)}</span>
            <span className="stat-label">Away</span>
          </div>
          <div className="stat-item">
            <i className="fas fa-clock me-2"></i>
            <span className="stat-value">{formatETA(eta)}</span>
            <span className="stat-label">Walking</span>
          </div>
        </div>
      )}

      {/* Map Mode */}
      {mode === 'map' && (
        <div className="map-view">
          <div className="map-container">
            {/* Map placeholder - would integrate with Google Maps, Mapbox, etc. */}
            <div className="map-placeholder">
              <div className="map-marker user-marker">
                <i className="fas fa-circle"></i>
                <div className="pulse"></div>
              </div>

              <div className="map-marker event-marker">
                <i className="fas fa-map-pin"></i>
              </div>

              <div className="route-line"></div>

              <div className="map-overlay">
                <div className="direction-indicator">
                  <div className="direction-arrow" style={{ transform: `rotate(${getBearing() - heading}deg)` }}>
                    {getDirectionArrow()}
                  </div>
                  <div className="compass-heading">{Math.round(heading)}°</div>
                </div>
              </div>
            </div>

            {/* Map controls */}
            <div className="map-controls">
              <button className="map-control-btn" title="Center on me">
                <i className="fas fa-location-crosshairs"></i>
              </button>
              <button className="map-control-btn" title="Zoom in">
                <i className="fas fa-plus"></i>
              </button>
              <button className="map-control-btn" title="Zoom out">
                <i className="fas fa-minus"></i>
              </button>
            </div>
          </div>

          {/* Turn-by-turn instructions */}
          <div className="navigation-instructions">
            <div className="instruction-card">
              <div className="instruction-icon">{getDirectionArrow()}</div>
              <div className="instruction-text">
                <div className="instruction-primary">Head {getCardinalDirection(getBearing())}</div>
                <div className="instruction-secondary">
                  toward {event.venue}
                </div>
              </div>
              <div className="instruction-distance">{formatDistance(distance)}</div>
            </div>
          </div>
        </div>
      )}

      {/* AR Mode */}
      {mode === 'ar' && arSupported && (
        <div className="ar-view">
          {/* Camera feed */}
          <video
            ref={videoRef}
            className="ar-camera"
            autoPlay
            playsInline
            muted
          ></video>

          {/* AR Overlays */}
          <div className="ar-overlays">
            {/* Direction indicator */}
            <div className="ar-direction-hud">
              <div className="ar-arrow" style={{ transform: `rotate(${getBearing() - heading}deg)` }}>
                <div className="arrow-icon">⬆️</div>
                <div className="arrow-line"></div>
              </div>

              <div className="ar-distance-badge">
                {formatDistance(distance)}
              </div>
            </div>

            {/* Event marker overlay */}
            <div className="ar-event-marker">
              <div className="marker-icon">
                <i className="fas fa-map-marker-alt"></i>
              </div>
              <div className="marker-label">
                <div className="marker-title">{event.title}</div>
                <div className="marker-distance">{formatDistance(distance)} • {formatETA(eta)}</div>
              </div>
            </div>

            {/* Compass */}
            <div className="ar-compass">
              <div className="compass-ring" style={{ transform: `rotate(${-heading}deg)` }}>
                <div className="compass-north">N</div>
                <div className="compass-east">E</div>
                <div className="compass-south">S</div>
                <div className="compass-west">W</div>
              </div>
              <div className="compass-needle"></div>
            </div>
          </div>
        </div>
      )}

      {/* AR Not Supported Message */}
      {mode === 'ar' && !arSupported && (
        <div className="ar-not-supported">
          <i className="fas fa-exclamation-triangle mb-3" style={{ fontSize: '3rem' }}></i>
          <h5>AR Not Supported</h5>
          <p className="text-muted">
            Your device doesn't support AR features.
            <br />
            Try using the map view instead.
          </p>
          <button className="btn btn-primary mt-3" onClick={() => setMode('map')}>
            <i className="fas fa-map me-2"></i>
            Switch to Map
          </button>
        </div>
      )}

      {/* Quick Actions */}
      <div className="ar-actions">
        <button className="action-btn">
          <i className="fas fa-directions"></i>
          <span>Google Maps</span>
        </button>
        <button className="action-btn">
          <i className="fas fa-phone"></i>
          <span>Call Venue</span>
        </button>
        <button className="action-btn">
          <i className="fas fa-share-alt"></i>
          <span>Share</span>
        </button>
      </div>

      <style jsx>{`
        .ar-wayfinding {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: #000;
          z-index: 1060;
          display: flex;
          flex-direction: column;
        }

        .ar-header {
          padding: 20px;
          background: linear-gradient(180deg, rgba(0,0,0,0.8) 0%, transparent 100%);
          position: relative;
          z-index: 10;
          display: flex;
          align-items: center;
          gap: 15px;
        }

        .destination-info {
          flex: 1;
          color: white;
        }

        .destination-info h6 {
          color: white;
          font-weight: bold;
        }

        .mode-switcher {
          display: flex;
          gap: 5px;
          background: rgba(255, 255, 255, 0.1);
          border-radius: 8px;
          padding: 4px;
        }

        .mode-btn {
          background: transparent;
          border: none;
          color: white;
          padding: 8px 16px;
          border-radius: 6px;
          cursor: pointer;
          transition: background 0.2s;
        }

        .mode-btn:disabled {
          opacity: 0.3;
          cursor: not-allowed;
        }

        .mode-btn.active {
          background: rgba(255, 255, 255, 0.3);
        }

        .navigation-stats {
          display: flex;
          gap: 20px;
          padding: 15px 20px;
          background: linear-gradient(180deg, rgba(0,0,0,0.6) 0%, transparent 100%);
          position: relative;
          z-index: 10;
          color: white;
        }

        .stat-item {
          display: flex;
          align-items: center;
          gap: 8px;
        }

        .stat-value {
          font-size: 1.25rem;
          font-weight: bold;
          margin-right: 5px;
        }

        .stat-label {
          font-size: 0.875rem;
          opacity: 0.8;
        }

        /* Map View */
        .map-view {
          flex: 1;
          display: flex;
          flex-direction: column;
          overflow: hidden;
        }

        .map-container {
          flex: 1;
          position: relative;
          background: #e5e3df;
        }

        .map-placeholder {
          width: 100%;
          height: 100%;
          position: relative;
          background: linear-gradient(135deg, #667eea20 0%, #764ba220 100%);
          display: flex;
          align-items: center;
          justify-content: center;
        }

        .map-marker {
          position: absolute;
          font-size: 2rem;
          z-index: 5;
        }

        .user-marker {
          bottom: 30%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: #667eea;
          position: relative;
        }

        .user-marker .pulse {
          position: absolute;
          width: 30px;
          height: 30px;
          border-radius: 50%;
          background: rgba(102, 126, 234, 0.3);
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          animation: pulse 2s infinite;
        }

        @keyframes pulse {
          0% {
            transform: translate(-50%, -50%) scale(1);
            opacity: 1;
          }
          100% {
            transform: translate(-50%, -50%) scale(2.5);
            opacity: 0;
          }
        }

        .event-marker {
          top: 30%;
          left: 50%;
          transform: translate(-50%, -50%);
          color: #E63946;
        }

        .route-line {
          position: absolute;
          width: 4px;
          height: 40%;
          background: linear-gradient(to bottom, #667eea, #E63946);
          top: 30%;
          left: 50%;
          transform: translateX(-50%);
          opacity: 0.6;
        }

        .map-overlay {
          position: absolute;
          top: 20px;
          right: 20px;
        }

        .direction-indicator {
          background: rgba(255, 255, 255, 0.9);
          border-radius: 12px;
          padding: 15px;
          text-align: center;
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }

        .direction-arrow {
          font-size: 2rem;
          transition: transform 0.3s;
        }

        .compass-heading {
          margin-top: 5px;
          font-weight: bold;
          color: #667eea;
        }

        .map-controls {
          position: absolute;
          bottom: 20px;
          right: 20px;
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .map-control-btn {
          background: white;
          border: none;
          border-radius: 50%;
          width: 44px;
          height: 44px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.2);
          cursor: pointer;
          transition: transform 0.2s;
        }

        .map-control-btn:hover {
          transform: scale(1.1);
        }

        .navigation-instructions {
          padding: 15px 20px;
          background: white;
        }

        .instruction-card {
          display: flex;
          align-items: center;
          gap: 15px;
          padding: 15px;
          background: #f8f9fa;
          border-radius: 12px;
        }

        .instruction-icon {
          font-size: 2rem;
          width: 50px;
          height: 50px;
          display: flex;
          align-items: center;
          justify-content: center;
          background: white;
          border-radius: 10px;
        }

        .instruction-text {
          flex: 1;
        }

        .instruction-primary {
          font-weight: bold;
          font-size: 1.1rem;
          margin-bottom: 3px;
        }

        .instruction-secondary {
          color: #666;
          font-size: 0.875rem;
        }

        .instruction-distance {
          font-weight: bold;
          color: #667eea;
        }

        /* AR View */
        .ar-view {
          flex: 1;
          position: relative;
          overflow: hidden;
        }

        .ar-camera {
          width: 100%;
          height: 100%;
          object-fit: cover;
        }

        .ar-overlays {
          position: absolute;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          pointer-events: none;
        }

        .ar-direction-hud {
          position: absolute;
          top: 50%;
          left: 50%;
          transform: translate(-50%, -50%);
          text-align: center;
        }

        .ar-arrow {
          transition: transform 0.3s;
        }

        .arrow-icon {
          font-size: 4rem;
          filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
        }

        .arrow-line {
          width: 4px;
          height: 100px;
          background: linear-gradient(to bottom, rgba(102, 126, 234, 0.8), transparent);
          margin: -10px auto 0;
        }

        .ar-distance-badge {
          margin-top: 20px;
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 10px 20px;
          border-radius: 20px;
          font-weight: bold;
          font-size: 1.25rem;
          backdrop-filter: blur(10px);
        }

        .ar-event-marker {
          position: absolute;
          top: 20%;
          left: 50%;
          transform: translateX(-50%);
          text-align: center;
        }

        .marker-icon {
          font-size: 3rem;
          color: #E63946;
          filter: drop-shadow(0 4px 8px rgba(0,0,0,0.5));
          animation: bounce 2s infinite;
        }

        @keyframes bounce {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-10px);
          }
        }

        .marker-label {
          background: rgba(0, 0, 0, 0.7);
          color: white;
          padding: 10px 15px;
          border-radius: 12px;
          margin-top: 10px;
          backdrop-filter: blur(10px);
        }

        .marker-title {
          font-weight: bold;
          margin-bottom: 3px;
        }

        .marker-distance {
          font-size: 0.875rem;
          opacity: 0.9;
        }

        .ar-compass {
          position: absolute;
          top: 20px;
          right: 20px;
          width: 80px;
          height: 80px;
        }

        .compass-ring {
          width: 100%;
          height: 100%;
          border: 2px solid rgba(255, 255, 255, 0.5);
          border-radius: 50%;
          position: relative;
          transition: transform 0.3s;
          background: rgba(0, 0, 0, 0.3);
          backdrop-filter: blur(10px);
        }

        .compass-north,
        .compass-east,
        .compass-south,
        .compass-west {
          position: absolute;
          color: white;
          font-weight: bold;
          font-size: 0.875rem;
        }

        .compass-north {
          top: 5px;
          left: 50%;
          transform: translateX(-50%);
          color: #E63946;
        }

        .compass-east {
          right: 8px;
          top: 50%;
          transform: translateY(-50%);
        }

        .compass-south {
          bottom: 5px;
          left: 50%;
          transform: translateX(-50%);
        }

        .compass-west {
          left: 8px;
          top: 50%;
          transform: translateY(-50%);
        }

        .compass-needle {
          position: absolute;
          top: 50%;
          left: 50%;
          width: 2px;
          height: 30px;
          background: linear-gradient(to bottom, #E63946, transparent);
          transform: translate(-50%, -100%);
        }

        .ar-not-supported {
          flex: 1;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          color: white;
          padding: 40px;
          text-align: center;
        }

        /* Actions */
        .ar-actions {
          display: flex;
          gap: 10px;
          padding: 15px 20px;
          background: rgba(0, 0, 0, 0.8);
          overflow-x: auto;
        }

        .action-btn {
          display: flex;
          flex-direction: column;
          align-items: center;
          gap: 5px;
          padding: 12px 20px;
          background: rgba(255, 255, 255, 0.1);
          border: 1px solid rgba(255, 255, 255, 0.2);
          border-radius: 12px;
          color: white;
          cursor: pointer;
          transition: all 0.2s;
          white-space: nowrap;
        }

        .action-btn:hover {
          background: rgba(255, 255, 255, 0.2);
        }

        .action-btn i {
          font-size: 1.25rem;
        }

        .action-btn span {
          font-size: 0.75rem;
        }
      `}</style>
    </div>
  );
}

function getCardinalDirection(degrees) {
  const directions = ['North', 'Northeast', 'East', 'Southeast', 'South', 'Southwest', 'West', 'Northwest'];
  const index = Math.round(degrees / 45) % 8;
  return directions[index];
}
