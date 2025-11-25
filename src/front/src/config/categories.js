/**
 * Unified Category System for Tapin
 * Used across Listings, Events, and Web Search results
 */

export const CATEGORIES = [
  {
    id: 'all',
    name: 'All',
    color: '#607D8B',
    icon: '🌟'
  },
  {
    id: 'community',
    name: 'Community',
    color: '#3B82F6',
    icon: '🤝',
    aliases: ['Community Development']
  },
  {
    id: 'environment',
    name: 'Environment',
    color: '#10B981',
    icon: '🌱',
    aliases: ['Environment', 'Conservation']
  },
  {
    id: 'education',
    name: 'Education',
    color: '#8B5CF6',
    icon: '📚',
    aliases: ['Education & Literacy', 'Education']
  },
  {
    id: 'health',
    name: 'Health',
    color: '#EC4899',
    icon: '❤️',
    aliases: ['Health & Medicine', 'Health']
  },
  {
    id: 'animals',
    name: 'Animals',
    color: '#F59E0B',
    icon: '🐾',
    aliases: ['Animal Welfare', 'Animals']
  },
  {
    id: 'children',
    name: 'Children & Youth',
    color: '#F97316',
    icon: '👶',
    aliases: ['Children & Youth', 'Youth']
  },
  {
    id: 'seniors',
    name: 'Seniors',
    color: '#6366F1',
    icon: '👴',
    aliases: ['Seniors', 'Elder Care']
  },
  {
    id: 'arts',
    name: 'Arts & Culture',
    color: '#E91E63',
    icon: '🎨',
    aliases: ['Arts & Culture', 'Arts']
  },
  {
    id: 'disaster',
    name: 'Disaster Relief',
    color: '#EF4444',
    icon: '🚨',
    aliases: ['Disaster Relief', 'Emergency']
  },
  {
    id: 'rights',
    name: 'Human Rights',
    color: '#F97316',
    icon: '⚖️',
    aliases: ['Human Rights', 'Justice']
  },
  {
    id: 'social',
    name: 'Social Services',
    color: '#14B8A6',
    icon: '🤲',
    aliases: ['Social Services', 'Welfare']
  },
  {
    id: 'sports',
    name: 'Sports & Recreation',
    color: '#84CC16',
    icon: '⚽',
    aliases: ['Sports & Recreation', 'Fitness']
  },
  {
    id: 'technology',
    name: 'Technology',
    color: '#06B6D4',
    icon: '💻',
    aliases: ['Technology', 'Tech']
  },
  {
    id: 'women',
    name: "Women's Issues",
    color: '#DB2777',
    icon: '♀️',
    aliases: ["Women's Issues"]
  }
];

/**
 * Get category by name (handles aliases)
 */
export function getCategoryByName(name) {
  if (!name) return CATEGORIES[0]; // Return 'All' as default

  const normalized = name.trim();

  return CATEGORIES.find(cat =>
    cat.name.toLowerCase() === normalized.toLowerCase() ||
    (cat.aliases && cat.aliases.some(alias =>
      alias.toLowerCase() === normalized.toLowerCase()
    ))
  ) || CATEGORIES.find(cat => cat.id === 'all');
}

/**
 * Get category color by name
 */
export function getCategoryColor(name) {
  const category = getCategoryByName(name);
  return category.color;
}

/**
 * Get all category names for display
 */
export function getCategoryNames() {
  return CATEGORIES.map(cat => cat.name);
}

/**
 * Filter items by category
 */
export function filterByCategory(items, categoryName) {
  if (!categoryName || categoryName === 'All') {
    return items;
  }

  const category = getCategoryByName(categoryName);
  if (!category || category.id === 'all') {
    return items;
  }

  return items.filter(item => {
    const itemCategory = item.category || '';
    const itemCat = getCategoryByName(itemCategory);
    return itemCat.id === category.id;
  });
}

export default CATEGORIES;
