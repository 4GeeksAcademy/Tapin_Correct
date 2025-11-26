import React, { useState } from 'react';
import GlassCard from '../components/GlassCard';

const Messages = () => {
    const [activeChat, setActiveChat] = useState(1);

    const chats = [
        { id: 1, name: "GINTC Organizer", lastMsg: "See you tomorrow!", time: "10:30 AM", unread: 1 },
        { id: 2, name: "Sarah (Volunteer)", lastMsg: "Do you need a ride?", time: "Yesterday", unread: 0 },
    ];

    return (
        <div className="max-w-6xl mx-auto p-4 text-white h-[calc(100vh-100px)] flex gap-6">
            {/* Chat List */}
            <div className="w-1/3 hidden md:block">
                <GlassCard className="h-full overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-white/10 font-bold">Messages</div>
                    <div className="flex-1 overflow-y-auto">
                        {chats.map(chat => (
                            <div
                                key={chat.id}
                                onClick={() => setActiveChat(chat.id)}
                                className={`p-4 cursor-pointer hover:bg-white/5 transition border-b border-white/5 ${activeChat === chat.id ? 'bg-white/10' : ''}`}
                            >
                                <div className="flex justify-between mb-1">
                                    <span className="font-bold">{chat.name}</span>
                                    <span className="text-xs text-white/40">{chat.time}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span className="text-sm text-white/60 truncate">{chat.lastMsg}</span>
                                    {chat.unread > 0 && <span className="bg-blue-500 text-xs px-2 rounded-full">{chat.unread}</span>}
                                </div>
                            </div>
                        ))}
                    </div>
                </GlassCard>
            </div>

            {/* Chat Window */}
            <div className="flex-1 flex flex-col">
                <GlassCard className="flex-1 flex flex-col overflow-hidden">
                    <div className="p-4 border-b border-white/10 font-bold flex justify-between items-center">
                        <span>GINTC Organizer</span>
                        <button className="text-xs bg-white/10 px-3 py-1 rounded">View Profile</button>
                    </div>

                    <div className="flex-1 p-4 overflow-y-auto space-y-4">
                        <div className="flex justify-start">
                            <div className="bg-white/10 p-3 rounded-2xl rounded-tl-none max-w-[80%]">
                                Hi! Just checking if you received the parking info?
                            </div>
                        </div>
                        <div className="flex justify-end">
                            <div className="bg-blue-600 p-3 rounded-2xl rounded-tr-none max-w-[80%]">
                                Yes, got it. Thanks! See you tomorrow.
                            </div>
                        </div>
                    </div>

                    <div className="p-4 border-t border-white/10 flex gap-2">
                        <input
                            className="flex-1 bg-white/5 border border-white/10 rounded-full px-4 py-2 focus:outline-none focus:border-blue-500"
                            placeholder="Type a message..."
                        />
                        <button className="bg-blue-600 p-2 rounded-full w-10 h-10 flex items-center justify-center hover:bg-blue-700 transition">
                            ➤
                        </button>
                    </div>
                </GlassCard>
            </div>
        </div>
    );
};

export default Messages;
