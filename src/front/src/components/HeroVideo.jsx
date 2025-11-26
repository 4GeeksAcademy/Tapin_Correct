import React from 'react';
import heroVideo from '@/assets/brand/Animated_Hero_Video_with_Logo.mp4';

export default function HeroVideo({ maxWidth = 720, mobileMaxWidth = 360 }) {
    return (
        <div className="hero-video" style={{ display: 'flex', justifyContent: 'center', marginTop: 16 }}>
            <video
                src={heroVideo}
                autoPlay
                muted
                loop
                playsInline
                style={{ maxWidth, width: '100%', borderRadius: 10 }}
            />
            <style>{`@media (max-width: 600px) { .hero-video video { max-width: ${mobileMaxWidth}px; } }`}</style>
        </div>
    );
}
