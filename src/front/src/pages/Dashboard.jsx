import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import AchievementsPanel from '../components/AchievementsPanel';
import EventSwiper from '../components/EventSwiper';
import GlassCard from '../components/GlassCard';
import SurpriseMe from '../components/SurpriseMe';

/**
 * User Dashboard Component
 * Displays personalized user profile with:
 * - Taste profile analytics
 * - Achievement progress
 * - Personalized event recommendations
 * - Quick stats and activity summary
 * - Surprise Me feature integration
 */
const Dashboard = () => {
    const navigate = useNavigate();
    const [user, setUser] = useState(null);
    const [tasteProfile, setTasteProfile] = useState(null);
    const [personalizedEvents, setPersonalizedEvents] = useState([]);
    const [userStats, setUserStats] = useState({
        eventsAttended: 0,
        eventsLiked: 0,
        achievementsUnlocked: 0
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showSurpriseMe, setShowSurpriseMe] = useState(false);

    const token = localStorage.getItem('token');
    const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:5000';

    // Authentication check
    useEffect(() => {
        if (!token) {
            navigate('/login');
        }
    }, [token, navigate]);

    // Fetch user taste profile
    useEffect(() => {
        const fetchTasteProfile = async () => {
            try {
                const response = await fetch(`${BACKEND_URL}/api/profile/taste`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch taste profile: ${response.status}`);
                }

                const data = await response.json();
                setTasteProfile(data.profile);
            } catch (error) {
                console.error('Error fetching taste profile:', error);
                // Don't set error state for profile - it's optional
            }
        };

        if (token) {
            fetchTasteProfile();
        }
    }, [token, BACKEND_URL]);

    // Fetch personalized events
    useEffect(() => {
        const fetchPersonalizedEvents = async () => {
            try {
                setLoading(true);

                // Get user's saved location or default to Houston
                const savedLocation = localStorage.getItem('userLocation') || 'Houston, TX';

                const response = await fetch(`${BACKEND_URL}/api/events/personalized`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    body: JSON.stringify({
                        location: savedLocation,
                        limit: 20
                    })
                });

                if (!response.ok) {
                    throw new Error(`Failed to fetch events: ${response.status}`);
                }

                const data = await response.json();
                setPersonalizedEvents(data.events || []);
            } catch (error) {
                console.error('Error fetching personalized events:', error);
                setError(error.message);
            } finally {
                setLoading(false);
            }
        };

        if (token) {
            fetchPersonalizedEvents();
        }
    }, [token, BACKEND_URL]);

    // Fetch user achievements for stats
    useEffect(() => {
        const fetchStats = async () => {
            try {
                const response = await fetch(`${BACKEND_URL}/api/achievements`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });

                if (response.ok) {
                    const data = await response.json();
                    setUserStats(prev => ({
                        ...prev,
                        achievementsUnlocked: data.unlocked_count || 0
                    }));
                }
            } catch (error) {
                console.error('Error fetching stats:', error);
            }
        };

        if (token) {
            fetchStats();
        }
    }, [token, BACKEND_URL]);

    const handleEventSwipe = (event, direction) => {
        console.log(`Swiped ${direction} on event:`, event.title);

        // Update local stats
        if (direction === 'right') {
            setUserStats(prev => ({
                ...prev,
                eventsLiked: prev.eventsLiked + 1
            }));
        }
    };

    const handleSurpriseEvent = (event) => {
        console.log('Surprise event found:', event);
        setShowSurpriseMe(false);
        // Could navigate to event detail or show modal
    };

    const retryFetch = () => {
        setError(null);
        setLoading(true);
        window.location.reload(); // Simple retry - reload page
    };

    if (loading) {
        return (
            <div className="loading-container">
                <div className="spinner spinner-lg" />
                <p className="loading-text">Loading your dashboard...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="container" style={{ maxWidth: '600px', marginTop: 'var(--space-8)' }}>
                <div className="card card-elevated">
                    <h2 style={{ color: 'var(--error)', marginBottom: 'var(--space-4)' }}>⚠️ Something went wrong</h2>
                    <p className="text-muted mb-6">{error}</p>
                    <button onClick={retryFetch} className="btn btn-primary">
                        Try Again
                    </button>
                </div>
            </div>
        );
    }

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="container"
            style={{ minHeight: '100vh', paddingTop: 'var(--space-8)', paddingBottom: 'var(--space-8)' }}
        >
            {/* Header */}
            <div className="mb-8">
                <h1 className="hero-title" style={{ fontSize: 'var(--fs-4xl)' }}>
                    Your Dashboard
                </h1>
                <p className="text-muted" style={{ fontSize: 'var(--fs-lg)' }}>
                    Welcome back! Here's your personalized experience.
                </p>
            </div>

            {/* Quick Stats Row */}
            <div className="grid grid-3 mb-8">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                >
                    <div className="card text-center">
                        <div style={{ fontSize: 'var(--fs-5xl)', fontWeight: 'var(--fw-bold)', marginBottom: 'var(--space-2)' }}>
                            {userStats.eventsAttended}
                        </div>
                        <div className="text-muted">Events Attended</div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.2 }}
                >
                    <div className="card text-center">
                        <div style={{ fontSize: 'var(--fs-5xl)', fontWeight: 'var(--fw-bold)', marginBottom: 'var(--space-2)' }}>
                            {userStats.eventsLiked}
                        </div>
                        <div className="text-muted">Events Liked</div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.3 }}
                >
                    <div className="card text-center">
                        <div style={{ fontSize: 'var(--fs-5xl)', fontWeight: 'var(--fw-bold)', marginBottom: 'var(--space-2)' }}>
                            {userStats.achievementsUnlocked}
                        </div>
                        <div className="text-muted">Achievements</div>
                    </div>
                </motion.div>
            </div>

            {/* Main Dashboard Grid */}
            <div className="grid grid-2">

                {/* Left Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>

                    {/* Taste Profile Card */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="card">
                            <h2 style={{ fontSize: 'var(--fs-2xl)', fontWeight: 'var(--fw-semibold)', marginBottom: 'var(--space-4)' }}>
                                <span style={{ marginRight: 'var(--space-2)' }}>🎯</span> Your Taste Profile
                            </h2>

                            {tasteProfile ? (
                                <div>
                                    <h3 className="mb-4" style={{ fontSize: 'var(--fs-lg)', opacity: 0.9 }}>
                                        Favorite Categories
                                    </h3>
                                    <ul style={{ listStyle: 'none', padding: 0, marginBottom: 'var(--space-6)' }}>
                                        {Object.entries(tasteProfile.category_preferences || {})
                                            .sort(([, a], [, b]) => b - a)
                                            .slice(0, 5)
                                            .map(([category, score]) => (
                                                <li key={category} className="taste-profile-item">
                                                    <div className="progress-bar">
                                                        <div
                                                            className="progress-fill"
                                                            style={{ width: `${score * 100}%` }}
                                                        />
                                                    </div>
                                                    <span className="category-name">{category}</span>
                                                    <span className="category-score">{(score * 100).toFixed(0)}%</span>
                                                </li>
                                            ))}
                                    </ul>

                                    <div className="taste-profile-stats">
                                        <div>
                                            <div className="stat-label">Adventure Level</div>
                                            <div className="stat-value">
                                                {((tasteProfile.adventure_level || 0) * 100).toFixed(0)}%
                                            </div>
                                        </div>
                                        <div>
                                            <div className="stat-label">Price Sensitivity</div>
                                            <div className="stat-value" style={{ textTransform: 'capitalize' }}>
                                                {tasteProfile.price_sensitivity || 'Medium'}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center text-muted" style={{ padding: 'var(--space-8) 0' }}>
                                    <p>Start interacting with events to build your taste profile!</p>
                                </div>
                            )}
                        </div>
                    </motion.div>

                    {/* Achievements Panel */}
                    <motion.div
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <AchievementsPanel token={token} />
                    </motion.div>
                </div>

                {/* Right Column */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-8)' }}>

                    {/* Surprise Me Button */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.4 }}
                    >
                        <div className="card text-center">
                            <h2 style={{ fontSize: 'var(--fs-xl)', marginBottom: 'var(--space-3)' }}>
                                Feeling Adventurous? ✨
                            </h2>
                            <p className="text-muted mb-4" style={{ fontSize: 'var(--fs-base)' }}>
                                Let AI find you an unexpected event based on your mood
                            </p>
                            <button
                                onClick={() => setShowSurpriseMe(!showSurpriseMe)}
                                className="btn btn-accent btn-lg"
                            >
                                🎲 Surprise Me!
                            </button>
                        </div>
                    </motion.div>

                    {/* Surprise Me Component */}
                    {showSurpriseMe && (
                        <motion.div
                            initial={{ opacity: 0, scale: 0.95 }}
                            animate={{ opacity: 1, scale: 1 }}
                        >
                            <SurpriseMe
                                location={localStorage.getItem('userLocation') || 'Houston, TX'}
                                token={token}
                                onEventFound={handleSurpriseEvent}
                            />
                        </motion.div>
                    )}

                    {/* Personalized Events Swiper */}
                    <motion.div
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: 0.5 }}
                    >
                        <div className="card">
                            <h2 style={{ fontSize: 'var(--fs-2xl)', fontWeight: 'var(--fw-semibold)', marginBottom: 'var(--space-4)' }}>
                                <span style={{ marginRight: 'var(--space-2)' }}>💫</span> Events For You
                            </h2>

                            {personalizedEvents.length > 0 ? (
                                <div>
                                    <p className="text-muted mb-4" style={{ fontSize: 'var(--fs-base)' }}>
                                        Swipe right to like, left to skip
                                    </p>
                                    <EventSwiper
                                        events={personalizedEvents}
                                        token={token}
                                        onSwipe={handleEventSwipe}
                                    />
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-state-icon">🔍</div>
                                    <p className="empty-state-description">No personalized events available yet.</p>
                                    <p className="text-muted" style={{ fontSize: 'var(--fs-sm)', marginTop: 'var(--space-2)' }}>
                                        Start exploring events to get personalized recommendations!
                                    </p>
                                </div>
                            )}
                        </div>
                    </motion.div>
                </div>
            </div>

            {/* Bottom CTA */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.6 }}
                className="text-center mt-16"
            >
                <p className="text-muted mb-4">Want to discover more events?</p>
                <button
                    onClick={() => navigate('/events')}
                    className="btn btn-primary btn-lg"
                >
                    Browse All Events →
                </button>
            </motion.div>

            <style jsx>{`
                .taste-profile-item {
                    margin-bottom: var(--space-4);
                    display: flex;
                    align-items: center;
                    gap: var(--space-3);
                }

                .progress-bar {
                    flex: 1;
                    height: 8px;
                    background: var(--border-light);
                    border-radius: var(--radius-sm);
                    overflow: hidden;
                }

                .progress-fill {
                    height: 100%;
                    background: linear-gradient(90deg, var(--primary) 0%, var(--accent) 100%);
                    transition: width var(--transition-slow);
                }

                .category-name {
                    min-width: 150px;
                    font-size: var(--fs-base);
                }

                .category-score {
                    min-width: 50px;
                    font-weight: var(--fw-semibold);
                    opacity: 0.9;
                }

                .taste-profile-stats {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: var(--space-4);
                    padding-top: var(--space-4);
                    border-top: 1px solid var(--border-light);
                }

                .stat-label {
                    font-size: var(--fs-sm);
                    color: var(--text-muted);
                    margin-bottom: var(--space-1);
                }

                .stat-value {
                    font-size: var(--fs-2xl);
                    font-weight: var(--fw-semibold);
                }

                @media (max-width: 768px) {
                    .category-name {
                        min-width: 100px;
                    }

                    .category-score {
                        min-width: 40px;
                    }
                }
            `}</style>
        </motion.div>
    );
};

export default Dashboard;
