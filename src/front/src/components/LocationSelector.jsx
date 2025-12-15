import React, { useState, useRef, useEffect } from 'react';
import LocationDropdown from './LocationDropdown';

export default function LocationSelector({ onLocationSelected, externalLocation }) {
  const [selectedCity, setSelectedCity] = useState('');
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState(null);
  const [userCoords, setUserCoords] = useState(null);

  const handleCitySelect = (city) => {
    if (!city) return;
    setSelectedCity(city.name);
    onLocationSelected({ coords: [city.lat, city.lon], name: city.name, type: 'city' });
  };

  const handleUseMyLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by your browser');
      return;
    }

    setLocating(true);
    setError(null);

    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocating(false);
        const coords = [position.coords.latitude, position.coords.longitude];
        setUserCoords(coords);
        onLocationSelected({ coords, name: 'Your Location', type: 'geolocation' });
      },
      (error) => {
        setLocating(false);
        setError('Unable to retrieve your location. Please select a city instead.');
        console.error('Geolocation error:', error);
      }
    );
  };

  // If parent provides an externalLocation (e.g., map click), reflect it in the display
  useEffect(() => {
    if (externalLocation && externalLocation.coords) {
      setSelectedCity(externalLocation.name || `${externalLocation.coords[0].toFixed(4)}, ${externalLocation.coords[1].toFixed(4)}`);
    }
  }, [externalLocation]);

  return (
    <div style={{
      padding: '40px 20px',
      maxWidth: '600px',
      margin: '0 auto',
      textAlign: 'center'
    }}>
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '16px',
        padding: '48px 32px',
        color: 'white',
        boxShadow: '0 10px 40px rgba(0,0,0,0.1)'
      }}>
        <h2 style={{ margin: '0 0 12px 0', fontSize: '28px', fontWeight: '700' }}>
          📍 Choose Your Location
        </h2>
        <p style={{ margin: '0 0 32px 0', fontSize: '16px', opacity: 0.9 }}>
          Select your city or enable location to see nearby opportunities
        </p>

        <div style={{ marginBottom: '24px' }}>
          <button
            onClick={handleUseMyLocation}
            disabled={locating}
            style={{
              width: '100%',
              padding: '16px 24px',
              fontSize: '16px',
              fontWeight: '600',
              background: locating ? '#ccc' : 'white',
              color: locating ? '#666' : '#667eea',
              border: 'none',
              borderRadius: '12px',
              cursor: locating ? 'not-allowed' : 'pointer',
              transition: 'all 0.3s ease',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
            onMouseEnter={(e) => {
              if (!locating) {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 16px rgba(0,0,0,0.2)';
              }
            }}
            onMouseLeave={(e) => {
              e.target.style.transform = 'translateY(0)';
              e.target.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
            }}
          >
            {locating ? (
              <>
                <span style={{
                  width: '20px',
                  height: '20px',
                  border: '3px solid #666',
                  borderTopColor: 'transparent',
                  borderRadius: '50%',
                  animation: 'spin 1s linear infinite'
                }}></span>
                Locating...
              </>
            ) : (
              <>
                <span style={{ fontSize: '20px' }}>🎯</span>
                Use My Current Location
              </>
            )}
          </button>
        </div>

        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '16px',
          margin: '24px 0'
        }}>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.3)' }}></div>
          <span style={{ fontSize: '14px', opacity: 0.8 }}>OR</span>
          <div style={{ flex: 1, height: '1px', background: 'rgba(255,255,255,0.3)' }}></div>
        </div>

        <div style={{ position: 'relative' }}>
          <LocationDropdown
            value={selectedCity}
            onChange={(val) => setSelectedCity(val)}
            onSelect={handleCitySelect}
            userCoords={userCoords}
            placeholder="Location (e.g., San Francisco, CA)"
          />
        </div>

        {error && (
          <div style={{
            marginTop: '16px',
            padding: '12px 16px',
            background: 'rgba(255, 255, 255, 0.2)',
            borderRadius: '8px',
            fontSize: '14px',
            color: '#ffe0e0'
          }}>
            ⚠️ {error}
          </div>
        )}
      </div>

      <p style={{
        marginTop: '24px',
        fontSize: '13px',
        color: '#666',
        lineHeight: '1.6'
      }}>
        We only show opportunities within your local area to help you<br />
        connect with your community. Your privacy is important to us.
      </p>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}
