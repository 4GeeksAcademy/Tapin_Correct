import React from 'react';
import { useNavigate } from 'react-router-dom';
import GlassCard from '../components/GlassCard';

const Landing = () => {
    const navigate = useNavigate();

    return (
        <div className="min-h-screen text-white">
            {/* Hero Section */}
            <div className="relative min-h-[80vh] flex items-center justify-center text-center px-4 overflow-hidden">
                {/* Animated Background Blobs */}
                <div className="absolute top-20 left-20 w-72 h-72 bg-purple-500/30 rounded-full mix-blend-multiply filter blur-xl animate-blob"></div>
                <div className="absolute top-20 right-20 w-72 h-72 bg-blue-500/30 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-2000"></div>
                <div className="absolute -bottom-8 left-1/2 w-72 h-72 bg-pink-500/30 rounded-full mix-blend-multiply filter blur-xl animate-blob animation-delay-4000"></div>

                <div className="relative z-10 max-w-4xl mx-auto">
                    <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-white to-white/70">
                        Volunteer Matching <br />
                        <span className="text-blue-400">Reimagined.</span>
                    </h1>
                    <p className="text-xl md:text-2xl text-white/70 mb-10 max-w-2xl mx-auto leading-relaxed">
                        Tapin connects you with local causes based on your skills, interests, and schedule using AI-powered matching.
                    </p>

                    <div className="flex flex-col md:flex-row gap-4 justify-center">
                        <button
                            onClick={() => navigate('/signup')}
                            className="px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-full text-lg font-bold shadow-lg hover:scale-105 transition duration-300"
                        >
                            Get Started
                        </button>
                        <button
                            onClick={() => navigate('/organizations')}
                            className="px-8 py-4 bg-white/10 border border-white/20 rounded-full text-lg font-bold backdrop-blur-sm hover:bg-white/20 transition duration-300"
                        >
                            For Organizations
                        </button>
                    </div>
                </div>
            </div>

            {/* Features Section */}
            <div className="py-20 px-4 max-w-7xl mx-auto">
                <div className="text-center mb-16">
                    <h2 className="text-3xl font-bold mb-4">Why Tapin?</h2>
                    <p className="text-white/60">We make volunteering seamless and rewarding.</p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {[
                        { icon: "🎯", title: "Smart Matching", desc: "Our ML algorithm learns your taste profile to suggest events you'll actually love." },
                        { icon: "🏆", title: "Gamified Impact", desc: "Earn badges, track your hours, and verify your impact with automated certificates." },
                        { icon: "⚡", title: "Instant Signups", desc: "No more long forms. One tap to register, check in via QR code, and get to work." }
                    ].map((feature, i) => (
                        <GlassCard key={i} className="p-8 text-center hover:-translate-y-2 transition duration-300">
                            <div className="text-5xl mb-6">{feature.icon}</div>
                            <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                            <p className="text-white/60 leading-relaxed">{feature.desc}</p>
                        </GlassCard>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Landing;
