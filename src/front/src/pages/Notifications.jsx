import React from 'react';
import GlassCard from '../components/GlassCard';

const Notifications = () => {
    const notifications = [
        { id: 1, type: 'achievement', title: "Badge Unlocked!", msg: "You earned the 'Eco Warrior' badge.", time: "2m ago", read: false },
        { id: 2, type: 'event', title: "Reminder", msg: "Beach Cleanup starts tomorrow at 9 AM.", time: "1h ago", read: false },
        { id: 3, type: 'org', title: "GINTC approved your request", msg: "You are confirmed for the weekend shift.", time: "1d ago", read: true },
    ];

    return (
        <div className="max-w-2xl mx-auto p-4 text-white">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">Notifications</h1>
                <button className="text-sm text-blue-300 hover:text-white">Mark all as read</button>
            </div>

            <div className="space-y-4">
                {notifications.map(note => (
                    <GlassCard
                        key={note.id}
                        className={`p-4 flex gap-4 items-start transition ${!note.read ? 'border-l-4 border-blue-500 bg-blue-500/10' : 'opacity-70'}`}
                    >
                        <div className="text-2xl">
                            {note.type === 'achievement' ? '🏆' : note.type === 'event' ? '📅' : '🏢'}
                        </div>
                        <div className="flex-1">
                            <h3 className="font-bold text-sm">{note.title}</h3>
                            <p className="text-white/70 text-sm">{note.msg}</p>
                            <span className="text-xs text-white/40 mt-1 block">{note.time}</span>
                        </div>
                        {!note.read && <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>}
                    </GlassCard>
                ))}
            </div>
        </div>
    );
};

export default Notifications;
