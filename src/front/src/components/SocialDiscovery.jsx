import React, { useState, useEffect } from 'react';

import { API_URL } from '../lib/api';

/**
 * Social Discovery Layer
 *
 * "See Who's Going" - View friends' activity and coordinate attendance
 */
export default function SocialDiscovery({ token, eventId }) {
  const [attendees, setAttendees] = useState([]);
  const [friends, setFriends] = useState([]);
  const [showInvite, setShowInvite] = useState(false);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (eventId && token) {
      loadAttendees();
      loadFriends();
    }
  }, [eventId, token]);

  async function loadAttendees() {
    // Mock data for now - would fetch from API
    setAttendees([
      {
        id: 1,
        name: 'Sarah Chen',
        avatar: 'https://i.pravatar.cc/150?img=5',
        status: 'going',
        mutual_friends: 3
      },
      {
        id: 2,
        name: 'Mike Rodriguez',
        avatar: 'https://i.pravatar.cc/150?img=12',
        status: 'interested',
        mutual_friends: 5
      },
      {
        id: 3,
        name: 'Emily Taylor',
        avatar: 'https://i.pravatar.cc/150?img=9',
        status: 'going',
        mutual_friends: 2
      }
    ]);
  }

  async function loadFriends() {
    // Mock friends data
    setFriends([
      {
        id: 4,
        name: 'Alex Johnson',
        avatar: 'https://i.pravatar.cc/150?img=8',
        shared_interests: ['Music', 'Food']
      },
      {
        id: 5,
        name: 'Jessica Wu',
        avatar: 'https://i.pravatar.cc/150?img=20',
        shared_interests: ['Arts', 'Culture']
      }
    ]);
  }

  async function inviteFriend(friendId) {
    setLoading(true);
    // Would send invitation via API
    setTimeout(() => {
      alert('Invitation sent!');
      setLoading(false);
    }, 500);
  }

  async function joinEvent() {
    // Would mark user as attending via API
    alert('You\'re going to this event!');
  }

  const goingCount = attendees.filter(a => a.status === 'going').length;
  const interestedCount = attendees.filter(a => a.status === 'interested').length;

  return (
    <div className="social-discovery">
      {/* Attendee summary */}
      <div className="attendee-summary mb-4">
        <div className="d-flex align-items-center justify-content-between mb-3">
          <div>
            <h5 className="mb-1">
              <i className="fas fa-users me-2 text-primary"></i>
              Who's Going
            </h5>
            <small className="text-muted">
              {goingCount} going • {interestedCount} interested
            </small>
          </div>

          <button
            className="btn btn-primary btn-sm"
            onClick={joinEvent}
          >
            <i className="fas fa-check me-1"></i>
            I'm Going
          </button>
        </div>

        {/* Avatar stack */}
        <div className="avatar-stack mb-3">
          {attendees.slice(0, 5).map((attendee, idx) => (
            <div
              key={attendee.id}
              className="avatar-item"
              style={{ zIndex: 10 - idx }}
              title={attendee.name}
            >
              <img
                src={attendee.avatar}
                alt={attendee.name}
                className="avatar-img"
              />
              {attendee.status === 'going' && (
                <span className="avatar-badge">
                  <i className="fas fa-check"></i>
                </span>
              )}
            </div>
          ))}

          {attendees.length > 5 && (
            <div className="avatar-more">
              +{attendees.length - 5}
            </div>
          )}
        </div>

        {/* Friends attending */}
        {attendees.length > 0 && (
          <div className="friends-attending">
            {attendees.slice(0, 2).map((attendee) => (
              <div key={attendee.id} className="friend-item mb-2">
                <div className="d-flex align-items-center">
                  <img
                    src={attendee.avatar}
                    alt={attendee.name}
                    className="friend-avatar me-2"
                  />
                  <div className="flex-grow-1">
                    <div className="fw-bold small">{attendee.name}</div>
                    {attendee.mutual_friends > 0 && (
                      <small className="text-muted">
                        {attendee.mutual_friends} mutual friends
                      </small>
                    )}
                  </div>
                  <span className={`badge ${attendee.status === 'going' ? 'bg-success' : 'bg-info'}`}>
                    {attendee.status === 'going' ? 'Going' : 'Interested'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Invite friends */}
      <div className="invite-section">
        <button
          className="btn btn-outline-primary btn-sm w-100 mb-3"
          onClick={() => setShowInvite(!showInvite)}
        >
          <i className="fas fa-user-plus me-2"></i>
          Invite Friends
        </button>

        {showInvite && (
          <div className="invite-panel animate__animated animate__fadeIn">
            <h6 className="mb-3">Invite Friends</h6>

            {friends.map((friend) => (
              <div key={friend.id} className="friend-invite-item mb-2">
                <div className="d-flex align-items-center">
                  <img
                    src={friend.avatar}
                    alt={friend.name}
                    className="friend-avatar me-2"
                  />
                  <div className="flex-grow-1">
                    <div className="fw-bold small">{friend.name}</div>
                    <div className="text-muted" style={{ fontSize: '0.75rem' }}>
                      {friend.shared_interests.join(', ')}
                    </div>
                  </div>
                  <button
                    className="btn btn-sm btn-primary"
                    onClick={() => inviteFriend(friend.id)}
                    disabled={loading}
                  >
                    Invite
                  </button>
                </div>
              </div>
            ))}

            {friends.length === 0 && (
              <div className="text-center py-3 text-muted">
                <i className="fas fa-user-friends mb-2" style={{ fontSize: '2rem' }}></i>
                <p className="mb-0 small">No friends yet</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Chat/Coordination */}
      <div className="coordination-section mt-4">
        <div className="card">
          <div className="card-body">
            <h6 className="card-title">
              <i className="fas fa-comments me-2"></i>
              Event Chat
            </h6>
            <p className="card-text small text-muted">
              Coordinate arrival times, carpools, and meetup spots with other attendees
            </p>
            <button className="btn btn-sm btn-outline-primary w-100">
              <i className="fas fa-comment me-2"></i>
              Join Chat
            </button>
          </div>
        </div>
      </div>

      <style jsx>{`
        .social-discovery {
          padding: 20px;
          background: white;
          border-radius: 12px;
        }

        .avatar-stack {
          display: flex;
          align-items: center;
        }

        .avatar-item {
          position: relative;
          margin-right: -10px;
        }

        .avatar-img {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          border: 2px solid white;
          object-fit: cover;
          transition: transform 0.2s;
        }

        .avatar-item:hover .avatar-img {
          transform: scale(1.2);
          z-index: 100;
        }

        .avatar-badge {
          position: absolute;
          bottom: 0;
          right: 0;
          width: 16px;
          height: 16px;
          background: #2ecc71;
          border-radius: 50%;
          border: 2px solid white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.6rem;
          color: white;
        }

        .avatar-more {
          width: 40px;
          height: 40px;
          border-radius: 50%;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 0.75rem;
          font-weight: bold;
          border: 2px solid white;
        }

        .friend-avatar {
          width: 35px;
          height: 35px;
          border-radius: 50%;
          object-fit: cover;
        }

        .friend-item,
        .friend-invite-item {
          padding: 10px;
          background: #f8f9fa;
          border-radius: 8px;
          transition: background 0.2s;
        }

        .friend-item:hover,
        .friend-invite-item:hover {
          background: #e9ecef;
        }

        .invite-panel {
          max-height: 300px;
          overflow-y: auto;
          padding: 10px;
          background: #f8f9fa;
          border-radius: 8px;
        }

        .coordination-section .card {
          border: none;
          background: linear-gradient(135deg, #667eea10 0%, #764ba210 100%);
        }
      `}</style>
    </div>
  );
}
