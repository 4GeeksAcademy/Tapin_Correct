import React, { useEffect, useState } from 'react';
import Header from './components/Header';
import ListingCard from './components/ListingCard';
import EmptyState from './components/EmptyState';
import ListingDetail from './components/ListingDetail';
import Filters from './components/Filters';
import AuthForm from './components/AuthForm';
import CreateListingForm from './components/CreateListingForm';
import DashboardLanding from './pages/DashboardLanding';
import EventDiscovery from './pages/EventDiscovery';
import MapView from './components/MapView';
import LocationSelector from './components/LocationSelector';
import ResetPasswordConfirm from './components/ResetPasswordConfirm';
import EventSearch from './components/EventSearch';
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

export default function App() {
  const pathname = typeof globalThis !== 'undefined' ? globalThis.location.pathname : '/';
  const resetMatch = pathname.match(/^\/reset-password\/confirm\/([^/]+)$/);
  if (resetMatch) {
    return <ResetPasswordConfirm token={resetMatch[1]} />;
  }

  const [listings, setListings] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selected, setSelected] = useState(null);
  const [activeFilter, setActiveFilter] = useState('All');
  const [token, setToken] = useState(localStorage.getItem('access_token') || null);
  // Show the marketing-style landing page when there's no token (mobile-first)
  const [showLanding, setShowLanding] = useState(!token);
  const [user, setUser] = useState(null);
  const [viewMode, setViewMode] = useState('list'); // 'list' or 'map'
  const [userLocation, setUserLocation] = useState(null); // Store user's selected location
  const [showEventSearch, setShowEventSearch] = useState(false); // Toggle event discovery
  const [showEventDiscovery, setShowEventDiscovery] = useState(false); // Toggle cutting-edge event discovery

  // Helper: fetch listings optionally filtered by q
  async function fetchListings(filter) {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (filter && filter !== 'All') params.set('q', filter);
      const url = `${API_URL}/listings${params.toString() ? `?${params.toString()}` : ''}`;
      const res = await fetch(url);
      if (!res.ok) throw new Error(`status ${res.status}`);
      const data = await res.json();
      setListings(data);
    } catch (error_) {
      setError(error_.message);
    } finally {
      setLoading(false);
    }
  }

  // Initialize filter from URL and fetch
  useEffect(() => {
    const params = new URLSearchParams(globalThis.location.search);
    const q = params.get('q') || 'All';
    setActiveFilter(q);
    fetchListings(q);
  }, []);

  useEffect(() => {
    async function fetchMe() {
      if (!token) return setUser(null);
      try {
        const res = await fetch(`${API_URL}/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!res.ok) {
          setUser(null);
          return;
        }
        const data = await res.json();
        setUser(data.user);
      } catch {
        setUser(null);
      }
    }
    fetchMe();
  }, [token]);

  function handleSelect(item) {
    setSelected(item);
  }

  function handleFilterChange(filter) {
    setActiveFilter(filter);
    const params = new URLSearchParams(globalThis.location.search);
    if (!filter || filter === 'All') params.delete('q');
    else params.set('q', filter);
    const qs = params.toString();
    const newUrl = qs ? `?${qs}` : globalThis.location.pathname;
    globalThis.history.replaceState(null, '', newUrl);
    fetchListings(filter);
  }

  function SkeletonList({ count = 3 }) {
    return (
      <ul className="listings skeleton-list">
        {Array.from({ length: count }).map((_, i) => (
          <li key={i} className="listing-item">
            <div className="skeleton-card">
              <div className="skeleton-title" />
              <div className="skeleton-line" />
              <div className="skeleton-line" style={{ width: '80%' }} />
            </div>
          </li>
        ))}
      </ul>
    );
  }

  if (showLanding && !token) {
    return (
      <div className="app-root">
        <Header user={user} onLogout={() => { localStorage.removeItem('access_token'); setToken(null); setUser(null); }} />
        <DashboardLanding
          onEnter={() => setShowLanding(false)}
          onLogin={(_user, accessToken) => {
            if (accessToken) {
              localStorage.setItem('access_token', accessToken);
              setToken(accessToken);
            }
            setShowLanding(false);
          }}
        />
      </div>
    );
  }

  // Show EventDiscovery page when enabled
  if (showEventDiscovery) {
    return (
      <div className="app-root">
        <Header
          user={user}
          onLogout={() => {
            localStorage.removeItem('access_token');
            setToken(null);
            setUser(null);
          }}
        />

        {/* Back to Main App Button */}
        <div style={{ padding: '10px 20px', background: '#f8fafc', borderBottom: '1px solid #e2e8f0' }}>
          <button
            onClick={() => setShowEventDiscovery(false)}
            className="btn btn-outline-secondary btn-sm"
          >
            <i className="fas fa-arrow-left me-2"></i>
            Back to Listings
          </button>
        </div>

        <EventDiscovery
          token={token}
          userLocation={userLocation}
          onLocationChange={setUserLocation}
        />
      </div>
    );
  }

  return (
    <div className="app-root">
      <Header
        user={user}
        onLogout={() => {
          localStorage.removeItem('access_token');
          setToken(null);
          setUser(null);
        }}
      />

      <div className="top-section">
        {!user && (
          <div className="auth-section">
            <AuthForm
              onLogin={(d) => {
                localStorage.setItem('access_token', d.access_token);
                setToken(d.access_token);
              }}
            />
          </div>
        )}

        <Filters active={activeFilter} onChange={handleFilterChange} />
      </div>

      <main>
        {/* Event Discovery Toggles - Only show when logged in */}
        {user && (
          <div style={{ marginBottom: '20px', textAlign: 'center', display: 'flex', gap: '10px', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowEventSearch(!showEventSearch)}
              style={{
                padding: '10px 20px',
                background: showEventSearch ? '#667eea' : '#fff',
                color: showEventSearch ? '#fff' : '#667eea',
                border: '2px solid #667eea',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                transition: 'all 0.3s ease',
              }}
            >
              {showEventSearch ? 'Hide Event Discovery' : 'Discover Volunteer Events'}
            </button>

            {/* Cutting-Edge Event Discovery Button */}
            <button
              onClick={() => setShowEventDiscovery(true)}
              style={{
                padding: '10px 20px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: '#fff',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '14px',
                transition: 'all 0.3s ease',
                boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-2px)';
                e.target.style.boxShadow = '0 6px 16px rgba(102, 126, 234, 0.5)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 4px 12px rgba(102, 126, 234, 0.4)';
              }}
            >
              <i className="fas fa-sparkles me-2"></i>
              AI Event Discovery
            </button>
          </div>
        )}

        {/* Event Search Component */}
        {showEventSearch && <EventSearch onEventsLoaded={(evts) => console.log('Events loaded:', evts)} />}

        {/* View Mode Toggle */}
        {!loading && !error && listings.length > 0 && (
          <div style={{ marginBottom: '20px', textAlign: 'center' }}>
            <button
              onClick={() => setViewMode('list')}
              style={{
                padding: '8px 16px',
                background: viewMode === 'list' ? '#007bff' : '#fff',
                color: viewMode === 'list' ? '#fff' : '#333',
                border: '1px solid #007bff',
                borderRadius: '4px 0 0 4px',
                cursor: 'pointer',
                fontWeight: viewMode === 'list' ? 'bold' : 'normal',
              }}
            >
              List
            </button>
            <button
              onClick={() => setViewMode('map')}
              style={{
                padding: '8px 16px',
                background: viewMode === 'map' ? '#007bff' : '#fff',
                color: viewMode === 'map' ? '#fff' : '#333',
                border: '1px solid #007bff',
                borderLeft: 'none',
                borderRadius: '0 4px 4px 0',
                cursor: 'pointer',
                fontWeight: viewMode === 'map' ? 'bold' : 'normal',
              }}
            >
              Map
            </button>
          </div>
        )}

        {loading && <SkeletonList count={3} />}
        {error && <p className="error">Error: {error}</p>}

        {!loading && !error && (
          <section>
            {listings.length === 0 ? (
              <EmptyState />
            ) : viewMode === 'list' ? (
              <ul className="listings">
                {listings.map((l) => (
                  <li key={l.id} className="listing-item">
                    <ListingCard listing={l} onSelect={handleSelect} />
                  </li>
                ))}
              </ul>
            ) : (
              // Map view shows selector + map side-by-side so both stay in sync
              <div style={{ display: 'grid', gridTemplateColumns: '360px 1fr', gap: 20 }}>
                <div>
                  <LocationSelector
                    externalLocation={userLocation}
                    onLocationSelected={(loc) => setUserLocation(loc)}
                  />
                </div>
                <div>
                  <MapView
                    listings={listings}
                    onListingClick={handleSelect}
                    userLocation={userLocation}
                    selectedLocation={userLocation}
                    onMapLocationSelect={(loc) => setUserLocation(loc)}
                  />
                </div>
              </div>
            )}
          </section>
        )}

        {user && (
          <div style={{ marginTop: 12 }}>
            <h3>Create a listing</h3>
            <CreateListingForm
              token={token}
              userLocation={userLocation}
              onCreated={(data) => {
                setListings((s) => [data, ...s]);
              }}
            />
          </div>
        )}
      </main>

      {selected && (
        <ListingDetail
          listing={selected}
          onClose={() => setSelected(null)}
          token={token}
          user={user}
          userLocation={userLocation}
        />
      )}

      <footer>
        <small>Tapin prototype</small>
      </footer>
    </div>
  );
}
