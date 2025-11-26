import React, { useState } from 'react';
import GlassCard from '../components/GlassCard';

const VolunteerManagement = () => {
    const [volunteers, setVolunteers] = useState([
        { id: 1, name: "Travone Butler", event: "Beach Cleanup", status: "Confirmed", checkIn: false },
        { id: 2, name: "Sarah Jones", event: "Beach Cleanup", status: "Waitlist", checkIn: false },
        { id: 3, name: "Mike Chen", event: "Tree Planting", status: "Attended", checkIn: true },
    ]);

    const handleCheckIn = (id) => {
        setVolunteers(volunteers.map(v => v.id === id ? { ...v, checkIn: !v.checkIn, status: !v.checkIn ? 'Attended' : 'Confirmed' } : v));
    };

    return (
        <div className="max-w-6xl mx-auto p-6 text-white">
            <div className="flex justify-between items-center mb-8">
                <h1 className="text-3xl font-bold">Volunteer Management</h1>
                <div className="flex gap-2">
                    <button className="px-4 py-2 bg-white/10 border border-white/20 rounded hover:bg-white/20">Export CSV</button>
                    <button className="px-4 py-2 bg-blue-600 rounded hover:bg-blue-700">Message All</button>
                </div>
            </div>

            <GlassCard className="overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead className="bg-white/10 text-white/70 uppercase text-sm">
                            <tr>
                                <th className="p-4">Volunteer Name</th>
                                <th className="p-4">Event</th>
                                <th className="p-4">Status</th>
                                <th className="p-4">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-white/5">
                            {volunteers.map(vol => (
                                <tr key={vol.id} className="hover:bg-white/5 transition">
                                    <td className="p-4 font-bold">{vol.name}</td>
                                    <td className="p-4">{vol.event}</td>
                                    <td className="p-4">
                                        <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${vol.status === 'Attended' ? 'bg-green-500/20 text-green-400' :
                                                vol.status === 'Waitlist' ? 'bg-yellow-500/20 text-yellow-400' :
                                                    'bg-blue-500/20 text-blue-400'
                                            }`}>
                                            {vol.status}
                                        </span>
                                    </td>
                                    <td className="p-4 flex gap-2">
                                        <button
                                            onClick={() => handleCheckIn(vol.id)}
                                            className={`px-3 py-1 rounded text-sm font-semibold transition ${vol.checkIn ? 'bg-green-600 text-white' : 'bg-white/10 hover:bg-white/20'
                                                }`}
                                        >
                                            {vol.checkIn ? 'Checked In' : 'Check In'}
                                        </button>
                                        <button className="p-2 bg-white/5 hover:bg-white/10 rounded">✉️</button>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </GlassCard>
        </div>
    );
};

export default VolunteerManagement;
