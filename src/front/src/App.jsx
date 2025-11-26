import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';

// Components
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import DashboardLanding from './pages/DashboardLanding';
import EventDiscovery from './pages/EventDiscovery';
import Dashboard from './pages/Dashboard';
import ResetPasswordConfirm from './components/ResetPasswordConfirm';

// API
import { API_URL } from './lib/api';

export default function App() {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('access_token') || null);
  const [loading, setLoading] = useState(true);
  const [userLocation, setUserLocation] = useState(null);

  // Fetch current user on mount
  useEffect(() => {
    async function fetchMe() {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const res = await fetch(`${API_URL}/me`, {
          headers: { Authorization: `Bearer ${token}` },
        });

        if (!res.ok) {
          localStorage.removeItem('access_token');
          setToken(null);
          setUser(null);
          setLoading(false);
          return;
        }

        const data = await res.json();
        setUser(data.user);
      } catch (error) {
        console.error('Error fetching user:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    }

    fetchMe();
  }, [token]);

  // Get user's geolocation
  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setUserLocation({
            coords: [position.coords.latitude, position.coords.longitude],
            type: 'coordinates',
          });
        },
        (error) => {
          console.log('Geolocation error:', error);
          // Default to a major city if geolocation fails
          setUserLocation({
            name: 'New York, NY',
            type: 'city',
          });
        }
      );
    } else {
      setUserLocation({
        name: 'New York, NY',
        type: 'city',
      });
    }
  }, []);

  const handleLogin = (userData, accessToken) => {
    if (accessToken) {
      localStorage.setItem('access_token', accessToken);
      setToken(accessToken);
    }
    if (userData) {
      setUser(userData);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  };

  if (loading) {
    return (
      <div className="app-root" style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
          style={{ textAlign: 'center' }}
        >
          <div className="spinner" style={{ margin: '0 auto var(--space-4)' }} />
          <p style={{ color: 'var(--text-muted)', fontSize: 'var(--fs-lg)' }}>
            Loading TapIn...
          </p>
        </motion.div>
      </div>
    );
  }

  return (
    <Router>
      <div className="app-root">
        <Navigation user={user} onLogout={handleLogout} />

        <AnimatePresence mode="wait">
          <Routes>
            {/* Landing Page / Home */}
            <Route
              path="/"
              element={
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <DashboardLanding
                    user={user}
                    onLogin={handleLogin}
                  />
                </motion.div>
              }
            />

            {/* Event Discovery */}
            <Route
              path="/discover"
              element={
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.3 }}
                >
                  <EventDiscovery
                    token={token}
                    user={user}
                    userLocation={userLocation}
                    onLocationChange={setUserLocation}
                  />
                </motion.div>
              }
            />

            {/* User Dashboard - Protected Route */}
            <Route
              path="/dashboard"
              element={
                user ? (
                  <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -20 }}
                    transition={{ duration: 0.3 }}
                  >
                    <Dashboard />
                  </motion.div>
                ) : (
                  <Navigate to="/?auth=true" replace />
                )
              }
            />

            {/* Password Reset Confirmation */}
            <Route
              path="/reset-password/confirm/:token"
              element={
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <ResetPasswordConfirm />
                </motion.div>
              }
            />

            {/* 404 Not Found */}
            <Route
              path="*"
              element={
                <div className="container" style={{ paddingTop: 'var(--space-20)', paddingBottom: 'var(--space-20)' }}>
                  <div className="empty-state">
                    <div className="empty-state-icon">404</div>
                    <h2 className="empty-state-title">Page Not Found</h2>
                    <p className="empty-state-description">
                      The page you're looking for doesn't exist or has been moved.
                    </p>
                    <a href="/" className="btn btn-primary btn-lg" style={{ marginTop: 'var(--space-6)' }}>
                      Back to Home
                    </a>
                  </div>
                </div>
              }
            />
          </Routes>
        </AnimatePresence>

        <Footer />
      </div>
    </Router>
  );
}
