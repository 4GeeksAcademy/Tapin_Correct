import React, { useRef, useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
// FIX: Use bundled marker icons so Vite doesn't break image paths
import iconUrl from 'leaflet/dist/images/marker-icon.png';
import iconRetinaUrl from 'leaflet/dist/images/marker-icon-2x.png';
import shadowUrl from 'leaflet/dist/images/marker-shadow.png';

const DefaultIcon = L.icon({
  iconUrl,
  iconRetinaUrl,
  shadowUrl,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  tooltipAnchor: [16, -28]
});
L.Marker.prototype.options.icon = DefaultIcon;

export default function MapView({
  listings,
  events,
  onListingClick,
  userLocation,
  selectedLocation,
  onMapLocationSelect,
  center: propCenter,
}) {
  const mapRef = useRef();
  const [isGeocoding, setIsGeocoding] = useState(false);

  // Normalize data: support both listings and events props
  const items = events || listings || [];

  // Use provided center or user's selected location or default to Houston
  const LOCAL_CITY_CENTER = propCenter || userLocation?.coords || [29.7604, -95.3698];
  const MAX_DISTANCE_KM = 50; // Only show items within 50km of center

  // Helper function to calculate distance between two coordinates (Haversine formula)
  const getDistanceKm = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Earth's radius in km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };

  // Normalize item coordinates (support both lat/latitude and lng/longitude)
  const normalizeItem = (item) => ({
    ...item,
    lat: item.lat || item.latitude,
    lng: item.lng || item.longitude,
  });

  // Filter items that have coordinates AND are within local area (if center provided, skip distance check)
  const mappableItems = items
    .map(normalizeItem)
    .filter((item) => {
      if (item.lat == null || item.lng == null) return false;
      // If a specific center is provided (like in EventDetail), skip distance filtering
      if (propCenter) return true;
      const distance = getDistanceKm(
        LOCAL_CITY_CENTER[0],
        LOCAL_CITY_CENTER[1],
        item.lat,
        item.lng
      );
      return distance <= MAX_DISTANCE_KM;
    });

  // Fixed center on local city
  const mapCenter = LOCAL_CITY_CENTER;

  // Fixed zoom level for city view
  const zoom = propCenter ? 14 : 11; // Closer zoom for single event view

  useEffect(() => {
    // Keep map centered appropriately
    if (mapRef.current) {
      mapRef.current.setView(LOCAL_CITY_CENTER, zoom);
    }
  }, [mappableItems]);

  // Component to handle map clicks and react to external selectedLocation
  function MapController({ selectedLocation }) {
    const map = useMap();

    // Smoothly pan to selectedLocation when it changes
    useEffect(() => {
      if (selectedLocation && selectedLocation.coords && map) {
        const [lat, lon] = selectedLocation.coords;
        // use flyTo for a smooth animated pan
        try {
          map.flyTo([lat, lon], Math.max(12, zoom), { duration: 1.0 });
        } catch (e) {
          map.setView([lat, lon], Math.max(12, zoom));
        }
      }
    }, [selectedLocation, map]);

    // Register click handler to pick a location from the map
    useMapEvents({
      click(e) {
        const { lat, lng } = e.latlng;
        // Attempt reverse-geocoding (Mapbox if token provided, else Nominatim)
        (async () => {
          setIsGeocoding(true);
          let displayName = `${lat.toFixed(4)}, ${lng.toFixed(4)}`;
          try {
            const token = import.meta.env.VITE_MAPBOX_TOKEN;
            if (token) {
              const url = `https://api.mapbox.com/geocoding/v5/mapbox.places/${lng},${lat}.json?types=place,locality,neighborhood,address&limit=1&access_token=${token}`;
              const res = await fetch(url);
              if (res.ok) {
                const data = await res.json();
                if (data && data.features && data.features.length) {
                  displayName = data.features[0].place_name;
                }
              }
            } else {
              // Fallback to Nominatim (OpenStreetMap)
              const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
              const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
              if (res.ok) {
                const data = await res.json();
                if (data && data.display_name) displayName = data.display_name;
              }
            }
          } catch (err) {
            // ignore; we'll use lat/lon as name
            console.error('Reverse geocode error', err);
          } finally {
            setIsGeocoding(false);
          }

          if (onMapLocationSelect) {
            onMapLocationSelect({ coords: [lat, lng], name: displayName, type: 'map' });
          }
        })();
      }
    });

    return null;
  }

  if (mappableItems.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '500px',
          background: 'rgba(255, 255, 255, 0.05)',
          borderRadius: '8px',
          color: '#999',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '18px', marginBottom: '8px' }}>📍 No events with location data</p>
          <p style={{ fontSize: '14px' }}>
            {propCenter ? 'Location data unavailable for this event.' : `No items within ${MAX_DISTANCE_KM}km have location data.`}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={{ position: 'relative' }}>
      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        .geocoding-spinner {
          animation: spin 1s linear infinite;
        }
      `}</style>

      <MapContainer
        center={mapCenter}
        zoom={zoom}
        ref={mapRef}
        style={{ height: '600px', width: '100%', borderRadius: '8px', zIndex: 0, position: 'relative' }}
        scrollWheelZoom={true}
        minZoom={propCenter ? 10 : 10}
        maxZoom={18}
        maxBounds={propCenter ? undefined : [
          [LOCAL_CITY_CENTER[0] - 0.5, LOCAL_CITY_CENTER[1] - 0.5],
          [LOCAL_CITY_CENTER[0] + 0.5, LOCAL_CITY_CENTER[1] + 0.5]
        ]}
      >
        {/* controller to handle clicks and panning to external selected location */}
        <MapController selectedLocation={selectedLocation} />
        <TileLayer
          attribution='&copy; OpenStreetMap contributors &copy; CARTO'
          url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
        />

        {mappableItems.map((item) => (
          <Marker key={item.id} position={[item.lat, item.lng]}>
            <Popup>
              <div style={{ minWidth: '200px', background: '#1a1a1a', padding: '8px', borderRadius: '8px' }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px', color: '#fff' }}>{item.title}</h3>
                {(item.location || item.venue || item.location_name) && (
                  <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#aaa' }}>
                    📍 {item.location || item.venue || item.location_name}
                  </p>
                )}
                {item.date && (
                  <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#aaa' }}>
                    📅 {typeof item.date === 'string' ? new Date(item.date).toLocaleDateString() : item.date}
                  </p>
                )}
                {item.description && (
                  <p
                    style={{
                      margin: '8px 0',
                      fontSize: '14px',
                      maxHeight: '60px',
                      overflow: 'hidden',
                      color: '#ccc',
                    }}
                  >
                    {item.description.substring(0, 100)}
                    {item.description.length > 100 ? '...' : ''}
                  </p>
                )}
                {onListingClick && (
                  <button
                    onClick={() => onListingClick(item)}
                    style={{
                      marginTop: '8px',
                      padding: '6px 12px',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: 'white',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      width: '100%',
                      fontWeight: 'bold',
                    }}
                  >
                    View Details
                  </button>
                )}
              </div>
            </Popup>
          </Marker>
        ))}

        {/* Marker for the externally-selected location (from LocationSelector or map click) */}
        {selectedLocation && selectedLocation.coords && (
          <Marker position={[selectedLocation.coords[0], selectedLocation.coords[1]]}>
            <Popup>
              <div style={{ minWidth: '180px' }}>
                <strong style={{ color: 'white' }}>{selectedLocation.name || 'Selected location'}</strong>
                <div style={{ marginTop: 6, fontSize: 12, color: 'var(--text-muted)' }}>{selectedLocation.type}</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {/* Loading spinner overlay during reverse-geocoding */}
      {isGeocoding && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: 'rgba(255, 255, 255, 0.7)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            borderRadius: '8px',
            zIndex: 1000,
          }}
        >
          <div style={{ textAlign: 'center' }}>
            <div
              className="geocoding-spinner"
              style={{
                fontSize: '32px',
                marginBottom: '12px',
              }}
            >
              🔄
            </div>
            <p style={{ margin: 0, color: '#666', fontSize: '14px' }}>Locating address...</p>
          </div>
        </div>
      )}
    </div>
  );
}
