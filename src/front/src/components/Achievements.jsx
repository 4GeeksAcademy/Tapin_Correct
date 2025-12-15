import React, { useState, useEffect } from 'react';

export default function Achievements({ userId }) {
    const [achievements, setAchievements] = useState([]);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (!userId) return;

        const fetchAchievements = async () => {
            const token = localStorage.getItem('access_token');
            try {
                const response = await fetch(`/api/user/${userId}/achievements`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                });
                if (!response.ok) {
                    throw new Error('Failed to fetch achievements');
                }
                const data = await response.json();
                setAchievements(data);
            } catch (err) {
                setError(err.message);
            }
        };

        fetchAchievements();
    }, [userId]);

    if (error) {
        return <p className="error-message">Error: {error}</p>;
    }

    if (achievements.length === 0) {
        return <p>No achievements yet. Keep volunteering!</p>;
    }

    return (
        <div className="achievements-container">
            <h3>Your Achievements</h3>
            <div className="achievements-list">
                {achievements.map(ach => (
                    <div key={ach.id} className="achievement-item" title={`${ach.name}: ${ach.description}`}>
                        <i className={`fas ${ach.icon}`}></i>
                        <span>{ach.name}</span>
                    </div>
                ))}
            </div>
        </div>
    );
}
