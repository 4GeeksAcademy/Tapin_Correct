import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';
import MapView from '../components/MapView';

const EventDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [event, setEvent] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Fetch single event (placeholder/demo data)
        const fetchEvent = async () => {
            try {
                const mockEvent = {
                    id,
                    title: "Beach Cleanup 2025",
                    organization: "Galveston Nature Council",
                    date: "Nov 30, 2025",
                    time: "9:00 AM - 12:00 PM",
                    location: "Stewart Beach Park",
                    lat: 29.3013,
                    lng: -94.7977,
                    description: "Join us for a morning of coastal conservation! We'll be removing debris and plastics from Stewart Beach. Supplies provided.",
                    image: "https://images.unsplash.com/photo-1618477461853-cf6ed80faba5?auto=format&fit=crop&w=1200&q=80",
                    spots_total: 20,
                    spots_taken: 15,
                    skills: ["No Experience Needed", "Teamwork"],
                    tags: ["Environment", "Outdoor"]
                };
                setTimeout(() => { setEvent(mockEvent); setLoading(false); }, 400);
            } catch (err) {
                console.error(err);
                setLoading(false);
            }
        };
        fetchEvent();
    }, [id]);

    if (loading) return <div className="text-center text-white mt-20">Loading Event...</div>;

    return (
        <div className="max-w-6xl mx-auto p-4 text-white pb-20">
            {/* Hero Section */}
            <div className="relative h-64 md:h-96 rounded-2xl overflow-hidden mb-8 shadow-2xl">
                <img src={event.image} alt={event.title} className="w-full h-full object-cover" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-transparent to-transparent flex items-end p-8">
                    <div>
                        <span className="px-3 py-1 bg-green-500 text-xs font-bold rounded-full uppercase tracking-wide mb-2 inline-block">
                            {event.tags[0]}
                        </span>
                        <h1 className="text-4xl md:text-5xl font-bold mb-2">{event.title}</h1>
                        <p className="text-xl text-white/80 flex items-center gap-2">
                            <span>🏢 {event.organization}</span>
                            <span className="text-blue-400 text-sm">✓ Verified</span>
                        </p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {/* Left Column: Details */}
                <div className="lg:col-span-2 space-y-8">
                    <GlassCard className="p-8">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8 border-b border-white/10 pb-8">
                            <div>
                                <div className="text-white/50 text-sm mb-1">Date</div>
                                <div className="font-semibold">{event.date}</div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Time</div>
                                <div className="font-semibold">{event.time}</div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Location</div>
                                <div className="font-semibold text-blue-300 truncate">{event.location}</div>
                            </div>
                            <div>
                                <div className="text-white/50 text-sm mb-1">Availability</div>
                                <div className="font-semibold text-green-400">{event.spots_total - event.spots_taken} spots left</div>
                            </div>
                        </div>

                        <h2 className="text-2xl font-bold mb-4">About This Event</h2>
                        <p className="text-white/80 leading-relaxed text-lg mb-6">{event.description}</p>

                        <h3 className="text-lg font-bold mb-3">Skills Required</h3>
                        <div className="flex gap-2">
                            {event.skills.map(skill => (
                                <span key={skill} className="px-3 py-1 bg-white/10 rounded-full text-sm border border-white/20">{skill}</span>
                            ))}
                        </div>
                    </GlassCard>

                    <GlassCard className="h-80 overflow-hidden relative">
                        <MapView events={[event]} center={[event.lat, event.lng]} />
                    </GlassCard>
                </div>

                {/* Right Column: Sticky Action Card */}
                <div className="relative">
                    <GlassCard className="p-6 sticky top-24">
                        <h3 className="text-xl font-bold mb-6">Ready to Tap In?</h3>

                        <div className="space-y-4 mb-6">
                            <div className="flex justify-between text-sm">
                                <span className="text-white/60">Spots Filled</span>
                                <span className="font-bold">{event.spots_taken} / {event.spots_total}</span>
                            </div>
                            <div className="w-full bg-white/10 rounded-full h-2">
                                <div
                                    className="bg-green-500 h-2 rounded-full transition-all duration-1000"
                                    style={{ width: `${(event.spots_taken / event.spots_total) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        <button
                            className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl font-bold text-lg shadow-lg hover:scale-[1.02] transition active:scale-95 mb-3"
                            onClick={() => alert('Registered! (Demo)')}
                        >
                            Register Now
                        </button>

                        <button className="w-full py-3 bg-white/5 border border-white/10 rounded-xl font-semibold hover:bg-white/10 transition">Save for Later</button>

                        <p className="text-center text-xs text-white/40 mt-4">You'll receive a confirmation email immediately after registering.</p>
                    </GlassCard>
                </div>
            </div>
        </div>
    );
};

export default EventDetail;
