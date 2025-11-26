import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import MapView from '../components/MapView';
import { API_URL } from '../lib/api';

const EventDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [event, setEvent] = useState(null);
    const [loading, setLoading] = useState(true);
    const [registering, setRegistering] = useState(false);
    const [registered, setRegistered] = useState(false);
    const [saved, setSaved] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        // Try to get event from navigation state first
        if (location.state?.event) {
            setEvent(location.state.event);
            // Cache in localStorage for page refresh
            localStorage.setItem(`event_${id}`, JSON.stringify(location.state.event));
            setLoading(false);
            return;
        }

        // Try localStorage cache
        const cached = localStorage.getItem(`event_${id}`);
        if (cached) {
            try {
                setEvent(JSON.parse(cached));
                setLoading(false);
                return;
            } catch (e) {
                console.error('Error parsing cached event:', e);
            }
        }

        // Fall back to fetching from API (for internal events)
        const fetchEvent = async () => {
            try {
                const token = localStorage.getItem('token');
                const response = await fetch(`${API_URL}/api/events/${id}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                if (response.ok) {
                    const data = await response.json();
                    setEvent(data);
                } else {
                    setError('Event not found. Please return to discovery page.');
                }
            } catch (err) {
                console.error('Error fetching event:', err);
                setError('Failed to load event. Please try again.');
            } finally {
                setLoading(false);
            }
        };

        fetchEvent();
    }, [id, location.state]);

    const handleRegister = async () => {
        if (!event) return;

        setRegistering(true);
        setError(null);

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/events/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    event_id: event.id,
                    event_title: event.title,
                    category: event.category || 'Event',
                    source: event.source || 'unknown',
                }),
            });

            if (response.ok) {
                setRegistered(true);
                alert('Successfully registered! You will receive a confirmation email shortly.');
            } else {
                const data = await response.json();
                setError(data.error || 'Failed to register. Please try again.');
            }
        } catch (err) {
            console.error('Registration error:', err);
            setError('Network error. Please check your connection and try again.');
        } finally {
            setRegistering(false);
        }
    };

    const handleSave = async () => {
        if (!event) return;

        try {
            const token = localStorage.getItem('token');
            const response = await fetch(`${API_URL}/api/events/interact`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({
                    event_id: event.id,
                    event_title: event.title,
                    category: event.category || 'Event',
                    interaction: 'save',
                    source: event.source || 'unknown',
                }),
            });

            if (response.ok) {
                setSaved(true);
                setTimeout(() => setSaved(false), 2000);
            }
        } catch (err) {
            console.error('Save error:', err);
        }
    };

    const handleShare = async () => {
        if (!event) return;

        const shareData = {
            title: event.title,
            text: `Check out this volunteer opportunity: ${event.title}`,
            url: window.location.href,
        };

        try {
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                // Fallback: copy to clipboard
                await navigator.clipboard.writeText(window.location.href);
                alert('Link copied to clipboard!');
            }
        } catch (err) {
            console.error('Share error:', err);
        }
    };

    if (loading) return <div className="text-center text-white mt-20">Loading Event...</div>;
    if (error && !event) return <div className="text-center text-red-400 mt-20">{error}</div>;

    // Normalize event data for display
    const displayEvent = {
        title: event.title || 'Untitled Event',
        organization: event.organization || 'Community Organizer',
        date: event.date || event.date_start || 'TBD',
        time: event.time || 'TBD',
        location: event.location || event.venue || event.location_name || 'Location TBD',
        lat: event.lat || event.latitude || 29.7604,
        lng: event.lng || event.longitude || -95.3698,
        description: event.description || 'Details coming soon.',
        image: event.image || event.image_url || 'https://via.placeholder.com/1200x400?text=Event',
        category: event.category || event.event_category || 'Event',
        source: event.source || 'unknown',
        spots_total: event.max_volunteers || event.spots_total || 0,
        spots_taken: event.current_volunteers || event.spots_taken || 0,
    };

    return (
        <div className="max-w-6xl mx-auto p-4 text-white pb-20">
            {/* Back Button */}
            <button
                onClick={() => navigate(-1)}
                className="mb-4 flex items-center gap-2 text-white/60 hover:text-white transition"
            >
                ← Back to Discovery
            </button>

            {/* Hero Section */}
            <div className="relative h-64 md:h-96 rounded-2xl overflow-hidden mb-8 shadow-2xl">
                <img src={displayEvent.image} alt={displayEvent.title} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-8">
                    <div>
                        <span className="px-3 py-1 bg-green-500 text-xs font-bold rounded-full uppercase tracking-wide mb-2 inline-block">
                            {displayEvent.category}
                        </span>
                        <h1 className="text-4xl md:text-5xl font-bold mb-2">{displayEvent.title}</h1>
                        <p className="text-xl text-white/80 flex items-center gap-2">
                            <span>🏢 {displayEvent.organization}</span>
                        </p>
                    </div>
                </div>
            </div>

            {error && (
                <div className="mb-4 p-4 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300">
                    {error}
                </div>
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Details */}
                <div className="lg:col-span-2 space-y-8">
                    <GlassCard className="p-8">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8 border-b border-white/10 pb-8">
                            <div>
                                <div className="text-white/50 text-sm mb-1">Date</div>
                                <div className="font-semibold">
                                    {displayEvent.date !== 'TBD' ? new Date(displayEvent.date).toLocaleDateString() : 'TBD'}
                                </div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Time</div>
                                <div className="font-semibold">{displayEvent.time}</div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Location</div>
                                <div className="font-semibold text-blue-300 truncate">{displayEvent.location}</div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Availability</div>
                                {displayEvent.spots_total > 0 ? (
                                    <div className="font-semibold text-green-400">
                                        {displayEvent.spots_total - displayEvent.spots_taken} spots left
                                    </div>
                                ) : (
                                    <div className="font-semibold text-white/60">Open</div>
                                )}
                            </div>
                        </div>

                        <h2 className="text-2xl font-bold mb-4">About This Event</h2>
                        <p className="text-white/80 leading-relaxed text-lg mb-6">{displayEvent.description}</p>

                        <div className="flex gap-3">
                            <button
                                onClick={handleShare}
                                className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg transition flex items-center gap-2"
                            >
                                🔗 Share
                            </button>
                        </div>
                    </GlassCard>

                    <GlassCard className="h-80 overflow-hidden relative">
                        <MapView
                            events={[{ ...displayEvent, lat: displayEvent.lat, lng: displayEvent.lng }]}
                            center={[displayEvent.lat, displayEvent.lng]}
                        />
                    </GlassCard>
                </div>

                {/* Right Column: Sticky Action Card */}
                <div className="relative">
                    <GlassCard className="p-6 sticky top-24">
                        <h3 className="text-xl font-bold mb-6">Ready to Tap In?</h3>

                        {displayEvent.spots_total > 0 && (
                            <div className="space-y-4 mb-6">
                                <div className="flex justify-between text-sm">
                                    <span className="text-white/60">Spots Filled</span>
                                    <span className="font-bold">{displayEvent.spots_taken} / {displayEvent.spots_total}</span>
                                </div>
                                <div className="w-full bg-white/10 rounded-full h-2">
                                    <div
                                        className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                                        style={{
                                            width: `${displayEvent.spots_total > 0
                                                ? (displayEvent.spots_taken / displayEvent.spots_total) * 100
                                                : 0
                                                }%`
                                        }}
                                    ></div>
                                </div>
                            </div>
                        )}

                        <button
                            className={`w-full py-4 rounded-xl font-bold text-lg shadow-lg transition mb-3 ${registered
                                ? 'bg-green-600 cursor-not-allowed'
                                : 'bg-gradient-to-r from-blue-600 to-purple-600 hover:scale-[1.02] active:scale-95'
                                }`}
                            onClick={handleRegister}
                            disabled={registering || registered}
                        >
                            {registering ? 'Registering...' : registered ? '✓ Registered!' : 'Register Now'}
                        </button>

                        <button
                            className="w-full py-3 bg-white/5 border border-white/10 rounded-xl font-semibold hover:bg-white/10 transition"
                            onClick={handleSave}
                        >
                            {saved ? '✓ Saved!' : 'Save for Later'}
                        </button>

                        <p className="text-center text-xs text-white/40 mt-4">
                            You'll receive a confirmation email immediately after registering.
                        </p>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
};

export default EventDetail;
