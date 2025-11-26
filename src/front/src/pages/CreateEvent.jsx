import React, { useState } from 'react';
import GlassCard from '../components/GlassCard';
import { useNavigate } from 'react-router-dom';

const CreateEvent = () => {
    const navigate = useNavigate();
    const [step, setStep] = useState(1);
    const [formData, setFormData] = useState({
        title: '', category: 'Environment', date: '', location: '', description: ''
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        // Logic to POST to /api/events
        alert("Event Created! Redirecting...");
        navigate('/org/dashboard');
    };

    return (
        <div className="max-w-3xl mx-auto p-6 text-white min-h-screen flex items-center">
            <GlassCard className="w-full p-8">
                <div className="flex justify-between items-center mb-8">
                    <h1 className="text-2xl font-bold">Create New Event</h1>
                    <span className="text-sm text-white/50">Step {step} of 3</span>
                </div>

                {/* Progress Bar */}
                <div className="w-full bg-white/10 h-1 rounded-full mb-8">
                    <div
                        className="bg-blue-500 h-1 rounded-full transition-all duration-500"
                        style={{ width: `${(step / 3) * 100}%` }}
                    />
                </div>

                <form onSubmit={handleSubmit}>
                    {step === 1 && (
                        <div className="space-y-6 animate-fadeIn">
                            <div>
                                <label className="block text-sm text-white/70 mb-2">Event Title</label>
                                <input
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 focus:outline-none focus:border-blue-500 transition"
                                    placeholder="e.g., Annual Charity Gala"
                                    value={formData.title}
                                    onChange={e => setFormData({ ...formData, title: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-white/70 mb-2">Category</label>
                                <select
                                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 focus:outline-none focus:border-blue-500 [&>option]:text-black"
                                    value={formData.category}
                                    onChange={e => setFormData({ ...formData, category: e.target.value })}
                                >
                                    <option>Environment</option>
                                    <option>Education</option>
                                    <option>Health</option>
                                    <option>Animals</option>
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm text-white/70 mb-2">Description</label>
                                <textarea
                                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 h-32 focus:outline-none focus:border-blue-500"
                                    placeholder="Tell volunteers what they'll be doing..."
                                    value={formData.description}
                                    onChange={e => setFormData({ ...formData, description: e.target.value })}
                                />
                            </div>
                        </div>
                    )}

                    {step === 2 && (
                        <div className="space-y-6 animate-fadeIn">
                            <div>
                                <label className="block text-sm text-white/70 mb-2">Date & Time</label>
                                <input
                                    type="datetime-local"
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 focus:outline-none focus:border-blue-500 text-white"
                                    value={formData.date}
                                    onChange={e => setFormData({ ...formData, date: e.target.value })}
                                />
                            </div>
                            <div>
                                <label className="block text-sm text-white/70 mb-2">Location</label>
                                <input
                                    required
                                    className="w-full bg-white/5 border border-white/10 rounded-lg p-3 focus:outline-none focus:border-blue-500"
                                    placeholder="Street Address or Venue Name"
                                    value={formData.location}
                                    onChange={e => setFormData({ ...formData, location: e.target.value })}
                                />
                            </div>
                        </div>
                    )}

                    {step === 3 && (
                        <div className="space-y-6 animate-fadeIn text-center">
                            <div className="w-20 h-20 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-4">
                                <span className="text-3xl">🎉</span>
                            </div>
                            <h2 className="text-xl font-bold">Ready to Publish?</h2>
                            <p className="text-white/60">Your event "{formData.title}" will be visible to all volunteers immediately.</p>

                            <div className="bg-white/5 p-4 rounded-lg text-left text-sm space-y-2 max-w-sm mx-auto">
                                <div className="flex justify-between"><span>Category:</span> <span className="font-bold">{formData.category}</span></div>
                                <div className="flex justify-between"><span>Location:</span> <span className="font-bold">{formData.location}</span></div>
                            </div>
                        </div>
                    )}

                    <div className="flex justify-between mt-8 pt-6 border-t border-white/10">
                        {step > 1 ? (
                            <button type="button" onClick={() => setStep(s => s - 1)} className="text-white/60 hover:text-white">Back</button>
                        ) : (
                            <button type="button" onClick={() => navigate('/org/dashboard')} className="text-white/60 hover:text-white">Cancel</button>
                        )}

                        {step < 3 ? (
                            <button
                                type="button"
                                onClick={() => setStep(s => s + 1)}
                                className="px-6 py-2 bg-blue-600 rounded-lg font-semibold hover:bg-blue-700 transition"
                            >
                                Next Step
                            </button>
                        ) : (
                            <button
                                type="submit"
                                className="px-6 py-2 bg-green-600 rounded-lg font-semibold hover:bg-green-700 transition shadow-lg shadow-green-500/20"
                            >
                                Publish Event
                            </button>
                        )}
                    </div>
                </form>
            </GlassCard>
        </div>
    );
};

export default CreateEvent;
