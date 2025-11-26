import React, { useState, useEffect } from 'react';

import { API_URL } from '../lib/api';

/**
 * Achievements & Gamification Panel
 *
 * Displays user level, XP, achievements, and badges
 */
export default function AchievementsPanel({ token }) {
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);
  const [userRole, setUserRole] = useState(null);
  const [organizationMetrics, setOrganizationMetrics] = useState(null);
  const [levelInfo, setLevelInfo] = useState(null);

  const achievementDefinitions = {
    weekend_warrior: {
      name: 'Weekend Warrior',
      description: 'Make a difference 5 weekends in a row',
      badge: '/src/assets/badges/weekend-warrior.svg',
      color: '#17B8A3'  // Teal - commitment & consistency
    },
    category_completionist: {
      name: 'Impact Explorer',
      description: 'Experience all 22 ways to volunteer',
      badge: '🏆',
      color: '#FF9D42'  // Orange - achievement
    },
    early_bird: {
      name: 'Early Bird',
      description: 'Plan ahead: 10 events booked 1+ week early',
      badge: '/src/assets/badges/early-bird.svg',
      color: '#10b981'  // Green - preparation
    },
    last_minute_larry: {
      name: 'Quick Responder',
      description: 'Jump in to help: 10 same-day events',
      badge: '⚡',
      color: '#17B8A3'  // Teal - responsiveness
    },
    social_butterfly: {
      name: 'Social Butterfly',
      description: 'Inspire others: bring friends to 20 events',
      badge: '/src/assets/badges/social-butterfly.svg',
      color: '#FF9D42'  // Orange - community building
    },
    local_legend: {
      name: 'Local Legend',
      description: 'Community champion: 50 events in your city',
      badge: '/src/assets/badges/local-legend.svg',
      color: '#FF9D42'  // Orange - dedication
    },
    explorer: {
      name: 'Regional Impact Maker',
      description: 'Spread kindness: volunteer in 5 cities',
      badge: '🗺️',
      color: '#17B8A3'  // Teal - exploration
    },
    night_owl: {
      name: 'Evening Champion',
      description: 'After-hours hero: 15 evening events',
      badge: '🦉',
      color: '#10b981'  // Green - flexibility
    },
    free_spirit: {
      name: 'Generous Heart',
      description: 'Give freely: 20 volunteer-only events',
      badge: '💫',
      color: '#FF9D42'  // Orange - generosity
    },
    culture_vulture: {
      name: 'Arts & Culture Advocate',
      description: 'Support the arts: 15 cultural events',
      badge: '🎭',
      color: '#17B8A3'  // Teal - cultural enrichment
    }
  };

  useEffect(() => {
    if (token) {
      loadAchievements();
    }
  }, [token]);

  async function loadAchievements() {
    try {
      const res = await fetch(`${API_URL}/api/achievements`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (res.ok) {
        const data = await res.json();
        setUserRole(data.role);

        if (data.role === 'organization') {
          // Organization metrics
          setOrganizationMetrics(data.metrics);
        } else {
          // Volunteer achievements
          setAchievements(data.achievements || []);
          setLevelInfo(data.level_info);
        }
      }
    } catch (error) {
      console.error('Error loading achievements:', error);
    } finally {
      setLoading(false);
    }
  }

  function getAchievementInfo(achievement) {
    const info = achievementDefinitions[achievement.achievement_type] || {};
    return {
      name: info.name || achievement.achievement_type,
      description: info.description || '',
      badge: info.badge || '🏅',
      color: info.color || '#17B8A3'
    };
  }

  function calculateProgress(achievement) {
    const target = {
      weekend_warrior: 5,
      category_completionist: 22,
      early_bird: 10,
      last_minute_larry: 10,
      social_butterfly: 20,
      local_legend: 50,
      explorer: 5,
      night_owl: 15,
      free_spirit: 20,
      culture_vulture: 15
    }[achievement.achievement_type] || 100;

    return Math.min((achievement.progress / target) * 100, 100);
  }

  if (loading) {
    return (
      <div className="text-center py-4">
        <div className="spinner-border spinner-border-sm"></div>
      </div>
    );
  }

  // Organization Metrics View
  if (userRole === 'organization' && organizationMetrics) {
    return (
      <div className="achievements-panel">
        <div className="achievements-header mb-4">
          <h4 className="fw-bold mb-3">
            <span className="me-2">📊</span>
            Organization Metrics
          </h4>

          <div className="card">
            <div className="card-body">
              <div className="row text-center g-3">
                <div className="col-6 col-md-4">
                  <div className="stat-value text-primary">{organizationMetrics.events_posted}</div>
                  <div className="stat-label">Events Posted</div>
                </div>
                <div className="col-6 col-md-4">
                  <div className="stat-value text-success">{organizationMetrics.unique_volunteers}</div>
                  <div className="stat-label">Volunteers Reached</div>
                </div>
                <div className="col-6 col-md-4">
                  <div className="stat-value text-info">{organizationMetrics.total_views}</div>
                  <div className="stat-label">Total Views</div>
                </div>
                <div className="col-6 col-md-4">
                  <div className="stat-value text-warning">{organizationMetrics.total_likes}</div>
                  <div className="stat-label">Total Likes</div>
                </div>
                <div className="col-6 col-md-4">
                  <div className="stat-value text-danger">{organizationMetrics.total_attendees}</div>
                  <div className="stat-label">Attendees</div>
                </div>
                <div className="col-6 col-md-4">
                  <div className="stat-value text-success">{organizationMetrics.engagement_rate}%</div>
                  <div className="stat-label">Engagement Rate</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Tips for organizations */}
        <div className="alert alert-info mt-4">
          <h6><i className="fas fa-lightbulb me-2"></i>Tips to Improve Engagement</h6>
          <ul className="mb-0 small">
            <li>Post events with compelling descriptions and images</li>
            <li>Include clear contact information for volunteers</li>
            <li>Update event details regularly</li>
            <li>Respond quickly to volunteer inquiries</li>
          </ul>
        </div>
      </div>
    );
  }

  // Volunteer Achievements View
  const unlockedCount = achievements.filter(a => a.unlocked).length;
  const totalCount = achievements.length;

  return (
    <div className="achievements-panel">
      {/* Header */}
      <div className="achievements-header mb-4">
        <h4 className="fw-bold mb-3">
          <span className="me-2">🏆</span>
          Achievements
        </h4>

        {/* Level Info with Panda */}
        {levelInfo && (
          <div className="card mb-3" style={{
            background: 'linear-gradient(135deg, #17B8A3 0%, #0E9F8E 100%)',
            color: 'white',
            border: 'none'
          }}>
            <div className="card-body">
              <div className="row text-center align-items-center">
                <div className="col-auto">
                  <div style={{ fontSize: '3rem' }}>🐼</div>
                </div>
                <div className="col">
                  <div className="stat-value">Level {levelInfo.level}</div>
                  <div className="stat-label">{levelInfo.title}</div>
                </div>
                <div className="col">
                  <div className="stat-value">{levelInfo.xp} XP</div>
                  <div className="stat-label">Next: {levelInfo.next_level_xp} XP</div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="achievement-stats card">
          <div className="card-body">
            <div className="row text-center">
              <div className="col">
                <div className="stat-value">{unlockedCount}</div>
                <div className="stat-label">Unlocked</div>
              </div>
              <div className="col">
                <div className="stat-value">{totalCount}</div>
                <div className="stat-label">Total</div>
              </div>
              <div className="col">
                <div className="stat-value">
                  {totalCount > 0 ? Math.round((unlockedCount / totalCount) * 100) : 0}%
                </div>
                <div className="stat-label">Complete</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Achievements grid */}
      <div className="achievements-grid">
        {achievements.map((achievement) => {
          const info = getAchievementInfo(achievement);
          const progress = calculateProgress(achievement);

          return (
            <div
              key={achievement.id}
              className={`achievement-card ${achievement.unlocked ? 'unlocked' : 'locked'}`}
            >
              <div className="achievement-icon" style={{
                backgroundColor: achievement.unlocked ? info.color : '#e0e0e0'
              }}>
                {achievement.unlocked ? (
                  info.badge?.startsWith('/') ? (
                    <img src={info.badge} alt={info.name} style={{ width: '40px', height: '40px' }} />
                  ) : (
                    <span>{info.badge}</span>
                  )
                ) : (
                  '🔒'
                )}
              </div>

              <div className="achievement-content">
                <h6 className="achievement-name mb-1">
                  {info.name}
                </h6>
                <p className="achievement-description small text-muted mb-2">
                  {info.description}
                </p>

                {/* Progress bar */}
                <div className="progress achievement-progress">
                  <div
                    className="progress-bar"
                    role="progressbar"
                    style={{
                      width: `${progress}%`,
                      backgroundColor: achievement.unlocked ? info.color : '#667eea'
                    }}
                  ></div>
                </div>

                <div className="achievement-meta mt-2">
                  <small className="text-muted">
                    {achievement.progress} {achievement.unlocked ? '✓' : '/ target'}
                  </small>

                  {achievement.unlocked && achievement.unlocked_at && (
                    <small className="text-success ms-2">
                      <i className="fas fa-check-circle me-1"></i>
                      {new Date(achievement.unlocked_at).toLocaleDateString()}
                    </small>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Empty state */}
      {achievements.length === 0 && (
        <div className="text-center py-5">
          <div className="display-4 mb-3">🐼</div>
          <h5>Start Your Volunteer Journey!</h5>
          <p className="text-muted">
            Make an impact in your community and unlock achievements along the way
          </p>
        </div>
      )}

      <style jsx>{`
        .achievements-panel {
          padding: 20px;
        }

        .achievement-stats {
          background: linear-gradient(135deg, #17B8A3 0%, #0E9F8E 100%);
          color: white;
          border: none;
        }

        .stat-value {
          font-size: 2rem;
          font-weight: bold;
        }

        .stat-label {
          font-size: 0.875rem;
          opacity: 0.9;
        }

        .achievements-grid {
          display: grid;
          grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
          gap: 20px;
        }

        .achievement-card {
          background: white;
          border-radius: 12px;
          padding: 20px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          transition: transform 0.2s, box-shadow 0.2s;
          display: flex;
          gap: 15px;
        }

        .achievement-card.unlocked {
          border-left: 4px solid;
        }

        .achievement-card.locked {
          opacity: 0.7;
        }

        .achievement-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }

        .achievement-icon {
          width: 60px;
          height: 60px;
          border-radius: 12px;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
          flex-shrink: 0;
        }

        .achievement-content {
          flex: 1;
        }

        .achievement-name {
          font-weight: bold;
          color: #333;
        }

        .achievement-description {
          line-height: 1.4;
        }

        .achievement-progress {
          height: 8px;
          background: #f0f0f0;
          border-radius: 4px;
        }

        .achievement-progress .progress-bar {
          border-radius: 4px;
          transition: width 0.3s ease;
        }

        .achievement-meta {
          display: flex;
          justify-content: space-between;
          align-items: center;
        }

        @media (max-width: 768px) {
          .achievements-grid {
            grid-template-columns: 1fr;
          }

          .achievement-card {
            flex-direction: column;
            text-align: center;
          }

          .achievement-icon {
            margin: 0 auto;
          }
        }
      `}</style>
    </div>
  );
}
