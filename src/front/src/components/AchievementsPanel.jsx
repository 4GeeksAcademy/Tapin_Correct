import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Achievements & Gamification Panel
 *
 * Displays user level, XP, achievements, and badges
 */
export default function AchievementsPanel({ token }) {
  const [achievements, setAchievements] = useState([]);
  const [loading, setLoading] = useState(true);

  const achievementDefinitions = {
    weekend_warrior: {
      name: 'Weekend Warrior',
      description: 'Attend events 5 weekends in a row',
      icon: '🎯',
      color: '#FF6B6B'
    },
    category_completionist: {
      name: 'Category Completionist',
      description: 'Try all 22 event categories',
      icon: '🏆',
      color: '#FFD93D'
    },
    early_bird: {
      name: 'Early Bird',
      description: 'Attend 10 events discovered >1 week before',
      icon: '🐦',
      color: '#6BCB77'
    },
    last_minute_larry: {
      name: 'Last Minute Larry',
      description: 'Attend 10 same-day events',
      icon: '⚡',
      color: '#4D96FF'
    },
    social_butterfly: {
      name: 'Social Butterfly',
      description: 'Bring friends to 20 events',
      icon: '🦋',
      color: '#9D4EDD'
    },
    local_legend: {
      name: 'Local Legend',
      description: 'Attend 50 events in your city',
      icon: '⭐',
      color: '#FCA311'
    },
    explorer: {
      name: 'Explorer',
      description: 'Attend events in 5 different cities',
      icon: '🗺️',
      color: '#06FFA5'
    },
    night_owl: {
      name: 'Night Owl',
      description: 'Attend 15 events starting after 8 PM',
      icon: '🦉',
      color: '#5E5EFF'
    },
    free_spirit: {
      name: 'Free Spirit',
      description: 'Attend 20 free events',
      icon: '💫',
      color: '#FF9ECD'
    },
    culture_vulture: {
      name: 'Culture Vulture',
      description: 'Attend 15 arts/theater/museum events',
      icon: '🎭',
      color: '#E63946'
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
        setAchievements(data.achievements || []);
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
      icon: info.icon || '🏅',
      color: info.color || '#667eea'
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
                {achievement.unlocked ? info.icon : '🔒'}
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
          <div className="display-4 mb-3">🎯</div>
          <h5>Start Your Journey!</h5>
          <p className="text-muted">
            Attend events to unlock achievements
          </p>
        </div>
      )}

      <style jsx>{`
        .achievements-panel {
          padding: 20px;
        }

        .achievement-stats {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
