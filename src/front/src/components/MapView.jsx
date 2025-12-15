import React, { useRef, useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMapEvents, useMap } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';


delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

export default function MapView({ listings, onListingClick, userLocation, selectedLocation, onMapLocationSelect }) {
  const mapRef = useRef();
  const [isGeocoding, setIsGeocoding] = useState(false);


  const LOCAL_CITY_CENTER = userLocation?.coords || [29.7604, -95.3698];
  const MAX_DISTANCE_KM = 50;


  const getDistanceKm = (lat1, lon1, lat2, lon2) => {
    const R = 6371;
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  };


  const mappableListings = listings.filter(
    (listing) => {
      if (listing.latitude == null || listing.longitude == null) return false;
      const distance = getDistanceKm(
        LOCAL_CITY_CENTER[0],
        LOCAL_CITY_CENTER[1],
        listing.latitude,
        listing.longitude
      );
      return distance <= MAX_DISTANCE_KM;
    }
  );


  const center = LOCAL_CITY_CENTER;


  const zoom = 11;

  useEffect(() => {


    if (mapRef.current) {
      mapRef.current.setView(LOCAL_CITY_CENTER, zoom);
    }

  }, [mappableListings]);


  function MapController({ selectedLocation }) {
    const map = useMap();


    useEffect(() => {
      if (selectedLocation && selectedLocation.coords && map) {
        const [lat, lon] = selectedLocation.coords;

        try {
          map.flyTo([lat, lon], Math.max(12, zoom), { duration: 1.0 });
        } catch (e) {
          map.setView([lat, lon], Math.max(12, zoom));
        }
      }
    }, [selectedLocation, map]);


    useMapEvents({
      click(e) {
        const { lat, lng } = e.latlng;

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

              const url = `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${lat}&lon=${lng}`;
              const res = await fetch(url, { headers: { 'Accept': 'application/json' } });
              if (res.ok) {
                const data = await res.json();
                if (data && data.display_name) displayName = data.display_name;
              }
            }
          } catch (err) {

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

  if (mappableListings.length === 0) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          height: '500px',
          background: '#f5f5f5',
          borderRadius: '8px',
          color: '#666',
        }}
      >
        <div style={{ textAlign: 'center' }}>
          <p style={{ fontSize: '18px', marginBottom: '8px' }}>📍 No local listings found</p>
          <p style={{ fontSize: '14px' }}>
            No listings within {MAX_DISTANCE_KM}km of your area have location data.
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
        center={center}
        zoom={zoom}
        ref={mapRef}
        style={{ height: '600px', width: '100%', borderRadius: '8px' }}
        scrollWheelZoom={true}
        minZoom={10}
        maxZoom={15}
        maxBounds={[
          [LOCAL_CITY_CENTER[0] - 0.5, LOCAL_CITY_CENTER[1] - 0.5],
          [LOCAL_CITY_CENTER[0] + 0.5, LOCAL_CITY_CENTER[1] + 0.5]
        ]}
      >
        {}
        <MapController selectedLocation={selectedLocation} />
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {mappableListings.map((listing) => (
          <Marker key={listing.id} position={[listing.latitude, listing.longitude]}>
            <Popup>
              <div style={{ minWidth: '200px' }}>
                <h3 style={{ margin: '0 0 8px 0', fontSize: '16px' }}>{listing.title}</h3>
                {listing.location && (
                  <p style={{ margin: '0 0 4px 0', fontSize: '12px', color: '#666' }}>
                    📍 {listing.location}
                  </p>
                )}
                {listing.description && (
                  <p
                    style={{
                      margin: '8px 0',
                      fontSize: '14px',
                      maxHeight: '60px',
                      overflow: 'hidden',
                    }}
                  >
                    {listing.description.substring(0, 100)}
                    {listing.description.length > 100 ? '...' : ''}
                  </p>
                )}
                <button
                  onClick={() => onListingClick && onListingClick(listing)}
                  style={{
                    marginTop: '8px',
                    padding: '6px 12px',
                    background: '#007bff',
                    color: 'white',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    width: '100%',
                  }}
                >
                  View Details
                </button>
              </div>
            </Popup>
          </Marker>
        ))}

        {}
        {selectedLocation && selectedLocation.coords && (
          <Marker position={[selectedLocation.coords[0], selectedLocation.coords[1]]}>
            <Popup>
              <div style={{ minWidth: '180px' }}>
                <strong>{selectedLocation.name || 'Selected location'}</strong>
                <div style={{ marginTop: 6, fontSize: 12, color: '#666' }}>{selectedLocation.type}</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>

      {}
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
