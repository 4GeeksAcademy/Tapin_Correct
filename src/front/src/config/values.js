/**
 * Organization and Event Values System
 * Used for matching users with organizations/events based on shared values
 */

export const VALUES = [
  {
    id: 'community',
    name: 'Community Building',
    description: 'Strengthening local communities and bringing people together',
    icon: '🤝',
    color: '#3B82F6'
  },
  {
    id: 'environment',
    name: 'Environmental Sustainability',
    description: 'Protecting the environment and promoting sustainable practices',
    icon: '🌱',
    color: '#10B981'
  },
  {
    id: 'education',
    name: 'Education & Learning',
    description: 'Promoting literacy, learning, and educational opportunities',
    icon: '📚',
    color: '#8B5CF6'
  },
  {
    id: 'health',
    name: 'Health & Wellness',
    description: 'Supporting physical and mental health for all',
    icon: '❤️',
    color: '#EC4899'
  },
  {
    id: 'equality',
    name: 'Equality & Justice',
    description: 'Fighting for human rights, equality, and social justice',
    icon: '⚖️',
    color: '#F97316'
  },
  {
    id: 'poverty',
    name: 'Poverty Alleviation',
    description: 'Fighting poverty and supporting those in need',
    icon: '🤲',
    color: '#14B8A6'
  },
  {
    id: 'youth',
    name: 'Youth Empowerment',
    description: 'Supporting and empowering young people',
    icon: '👶',
    color: '#F59E0B'
  },
  {
    id: 'seniors',
    name: 'Elder Care',
    description: 'Supporting and caring for senior citizens',
    icon: '👴',
    color: '#6366F1'
  },
  {
    id: 'animals',
    name: 'Animal Welfare',
    description: 'Protecting and caring for animals',
    icon: '🐾',
    color: '#F59E0B'
  },
  {
    id: 'arts',
    name: 'Arts & Culture',
    description: 'Promoting arts, culture, and creative expression',
    icon: '🎨',
    color: '#E91E63'
  },
  {
    id: 'innovation',
    name: 'Innovation & Technology',
    description: 'Using technology and innovation for social good',
    icon: '💡',
    color: '#06B6D4'
  },
  {
    id: 'disaster',
    name: 'Disaster Relief',
    description: 'Responding to emergencies and disasters',
    icon: '🚨',
    color: '#EF4444'
  },
  {
    id: 'hunger',
    name: 'Hunger Relief',
    description: 'Fighting hunger and food insecurity',
    icon: '🍽️',
    color: '#84CC16'
  },
  {
    id: 'women',
    name: 'Women Empowerment',
    description: 'Supporting women\'s rights and empowerment',
    icon: '♀️',
    color: '#DB2777'
  },
  {
    id: 'inclusion',
    name: 'Diversity & Inclusion',
    description: 'Promoting diversity, inclusion, and belonging',
    icon: '🌈',
    color: '#A855F7'
  }
];

/**
 * Get value by ID
 */
export function getValueById(id) {
  return VALUES.find(v => v.id === id) || VALUES[0];
}

/**
 * Get value by name (with fuzzy matching)
 */
export function getValueByName(name) {
  if (!name) return null;

  const normalized = name.trim().toLowerCase();

  return VALUES.find(v =>
    v.name.toLowerCase() === normalized ||
    v.description.toLowerCase().includes(normalized)
  );
}

/**
 * Map category to default values
 * Used when creating events from web search with categories
 */
export function getValuesFromCategory(category) {
  const categoryToValuesMap = {
    'Community': ['community'],
    'Environment': ['environment'],
    'Education': ['education'],
    'Health': ['health'],
    'Animals': ['animals'],
    'Children & Youth': ['youth'],
    'Seniors': ['seniors'],
    'Arts & Culture': ['arts'],
    'Disaster Relief': ['disaster'],
    'Human Rights': ['equality'],
    'Social Services': ['poverty'],
    'Technology': ['innovation'],
    'Women\'s Issues': ['women']
  };

  const values = categoryToValuesMap[category] || [];
  return values.map(id => getValueById(id));
}

/**
 * Calculate match score between user values and org/event values
 * Returns percentage of matching values (0-100)
 */
export function calculateValueMatch(userValues = [], itemValues = []) {
  if (!userValues.length || !itemValues.length) return 0;

  const matches = userValues.filter(uv => itemValues.includes(uv));
  return Math.round((matches.length / userValues.length) * 100);
}

/**
 * Filter items by values (match any of the selected values)
 */
export function filterByValues(items, selectedValues) {
  if (!selectedValues || selectedValues.length === 0) {
    return items;
  }

  return items.filter(item => {
    const itemValues = item.values || [];
    // Return true if any of the selected values match
    return selectedValues.some(sv => itemValues.includes(sv));
  });
}

export default VALUES;
