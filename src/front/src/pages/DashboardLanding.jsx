import React, { useState } from 'react';
import { motion } from 'framer-motion';
import pandaWaving from '../assets/mascot/panda-waving.svg';
import volunteerIcon from '../assets/icons/volunteer.svg';
import organizationIcon from '../assets/icons/organization.svg';
import locationIcon from '../assets/icons/location.svg';
import AuthForm from '../components/AuthForm';

export default function DashboardLanding({ onLogin, onEnter, user }) {
  const [showAuth, setShowAuth] = useState(false);

  const fadeInUp = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0 }
  };

  const staggerContainer = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2
      }
    }
  };

  if (showAuth) {
    return (
      <div className="app-root">
        <div className="container" style={{ maxWidth: '500px', paddingTop: 'var(--space-16)' }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="text-center mb-8">
              <img
                src={pandaWaving}
                alt="Tapin panda mascot waving"
                style={{ width: '220px', height: '220px', margin: '0 auto' }}
              />
            </div>

            <div className="card card-elevated">
              <AuthForm
                onLogin={(data) => {
                  try {
                    if (data?.access_token) {
                      localStorage.setItem('access_token', data.access_token);
                    }
                  } catch { }
                  if (typeof onLogin === 'function') {
                    const user = data?.user || null;
                    const token = data?.access_token || null;
                    onLogin(user, token);
                  }
                  setShowAuth(false);
                  if (typeof onEnter === 'function') onEnter();
                }}
              />

              <button
                onClick={() => setShowAuth(false)}
                className="btn btn-ghost w-100 mt-4"
              >
                ← Back to home
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  return (
    <div className="app-root">
      <section className="hero">
        <div className="container">
          <motion.div
            initial="hidden"
            animate="visible"
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="text-center"
          >
            <img
              src={pandaWaving}
              alt="Tapin panda mascot"
              style={{ width: '180px', height: '180px', margin: '0 auto var(--space-8)' }}
            />

            <h1 className="hero-title">
              TapIn
            </h1>

            <p className="hero-subtitle">
              Connect your community through volunteer opportunities and local services
            </p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              style={{ display: 'flex', gap: 'var(--space-4)', justifyContent: 'center', flexWrap: 'wrap' }}
            >
              <button
                className="btn btn-primary btn-lg"
                onClick={() => setShowAuth(true)}
                data-testid="get-started-btn"
                aria-label="Get started with registration"
              >
                Get Started
              </button>
              <button
                className="btn btn-secondary btn-lg"
                onClick={() => setShowAuth(true)}
                data-testid="login-btn"
                aria-label="Log in to your account"
              >
                Log In
              </button>
            </motion.div>
          </motion.div>

          {/* Feature Cards */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="grid grid-3 mt-16"
            style={{ maxWidth: '1200px', margin: '0 auto', marginTop: 'var(--space-16)' }}
          >
            <motion.div variants={fadeInUp} className="card">
              <div style={{ textAlign: 'center' }}>
                <img
                  src={volunteerIcon}
                  alt=""
                  style={{ width: '64px', height: '64px', margin: '0 auto var(--space-4)' }}
                />
                <h3 style={{ fontSize: 'var(--fs-2xl)', marginBottom: 'var(--space-3)' }}>
                  Volunteer Opportunities
                </h3>
                <p className="text-muted">
                  Find meaningful ways to give back to your community. Browse local volunteer opportunities and make a difference.
                </p>
              </div>
            </motion.div>

            <motion.div variants={fadeInUp} className="card">
              <div style={{ textAlign: 'center' }}>
                <img
                  src={organizationIcon}
                  alt=""
                  style={{ width: '64px', height: '64px', margin: '0 auto var(--space-4)' }}
                />
                <h3 style={{ fontSize: 'var(--fs-2xl)', marginBottom: 'var(--space-3)' }}>
                  Local Services
                </h3>
                <p className="text-muted">
                  Discover small businesses and professionals in your area. Support your local economy and find quality services.
                </p>
              </div>
            </motion.div>

            <motion.div variants={fadeInUp} className="card">
              <div style={{ textAlign: 'center' }}>
                <img
                  src={locationIcon}
                  alt=""
                  style={{ width: '64px', height: '64px', margin: '0 auto var(--space-4)' }}
                />
                <h3 style={{ fontSize: 'var(--fs-2xl)', marginBottom: 'var(--space-3)' }}>
                  Map View
                </h3>
                <p className="text-muted">
                  Browse opportunities by location. Easily find events and services near you with our interactive map.
                </p>
              </div>
            </motion.div>
          </motion.div>

          {/* Footer Note */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2, duration: 0.5 }}
            className="text-center text-muted mt-16"
            style={{ paddingBottom: 'var(--space-12)' }}
          >
            © {new Date().getFullYear()} TapIn
          </motion.div>
        </div>
      </section>
    </div>
  );
}
