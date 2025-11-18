import React, { useState } from 'react';

/**
 * Simple location text input component
 * Accepts "City, State" format (e.g., "Dallas, TX")
 */
export default function SimpleLocationInput({ value, onChange, placeholder }) {
  const [isUsingGeolocation, setIsUsingGeolocation] = useState(false);

  const handleUseCurrentLocation = () => {
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by your browser');
      return;
    }

    setIsUsingGeolocation(true);

    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;

        // Reverse geocode to get city, state
        try {
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`
          );
          const data = await response.json();

          const city = data.address.city || data.address.town || data.address.village || '';
          const state = data.address.state || '';
          const country = data.address.country || '';

          // Only use US locations
          if (country === 'United States' && city && state) {
            // Get state abbreviation (simple lookup)
            const stateAbbr = getStateAbbreviation(state);
            onChange(`${city}, ${stateAbbr || state}`);
          } else {
            onChange(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
          }
        } catch (error) {
          console.error('Geocoding error:', error);
          onChange(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
        } finally {
          setIsUsingGeolocation(false);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        alert('Unable to get your location. Please enter it manually.');
        setIsUsingGeolocation(false);
      }
    );
  };

  return (
    <div className="input-group">
      <span className="input-group-text">
        <i className="fas fa-map-marker-alt"></i>
      </span>
      <input
        type="text"
        className="form-control"
        placeholder={placeholder || "City, State (e.g., Dallas, TX)"}
        value={value || ''}
        onChange={(e) => onChange(e.target.value)}
      />
      <button
        className="btn btn-outline-secondary"
        type="button"
        onClick={handleUseCurrentLocation}
        disabled={isUsingGeolocation}
        title="Use my current location"
      >
        {isUsingGeolocation ? (
          <span className="spinner-border spinner-border-sm" role="status"></span>
        ) : (
          <i className="fas fa-crosshairs"></i>
        )}
      </button>
    </div>
  );
}

// Simple state name to abbreviation mapping
function getStateAbbreviation(stateName) {
  const states = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR',
    'California': 'CA', 'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE',
    'Florida': 'FL', 'Georgia': 'GA', 'Hawaii': 'HI', 'Idaho': 'ID',
    'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA', 'Kansas': 'KS',
    'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV',
    'New Hampshire': 'NH', 'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY',
    'North Carolina': 'NC', 'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK',
    'Oregon': 'OR', 'Pennsylvania': 'PA', 'Rhode Island': 'RI', 'South Carolina': 'SC',
    'South Dakota': 'SD', 'Tennessee': 'TN', 'Texas': 'TX', 'Utah': 'UT',
    'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA', 'West Virginia': 'WV',
    'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC'
  };

  return states[stateName] || null;
}
