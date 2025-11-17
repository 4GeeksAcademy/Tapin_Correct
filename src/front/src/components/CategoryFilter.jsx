import React, { useState, useEffect } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

/**
 * Category filter component with icons and colors
 * Fetches categories from the unified backend system
 */
export default function CategoryFilter({ selectedCategory, onCategoryChange }) {
  const [categories, setCategories] = useState({});
  const [grouped, setGrouped] = useState({});
  const [loading, setLoading] = useState(true);
  const [showAll, setShowAll] = useState(false);

  useEffect(() => {
    fetchCategories();
  }, []);

  async function fetchCategories() {
    try {
      const res = await fetch(`${API_URL}/api/categories`);
      if (res.ok) {
        const data = await res.json();
        setCategories(data.categories);
        setGrouped(data.grouped);
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="text-center py-3">
        <div className="spinner-border spinner-border-sm" role="status">
          <span className="visually-hidden">Loading...</span>
        </div>
      </div>
    );
  }

  const allCategories = Object.keys(categories);
  const displayCategories = showAll ? allCategories : allCategories.slice(0, 12);

  return (
    <div className="category-filter">
      <div className="d-flex flex-wrap gap-2 mb-3">
        <button
          className={`btn ${selectedCategory === 'All' ? 'btn-primary' : 'btn-outline-primary'} btn-sm`}
          onClick={() => onCategoryChange('All')}
        >
          <span className="me-1">📅</span>
          All Events
        </button>

        {displayCategories.map((categoryName) => {
          const category = categories[categoryName];
          const isSelected = selectedCategory === categoryName;

          return (
            <button
              key={categoryName}
              className={`btn ${isSelected ? 'btn-primary' : 'btn-outline-secondary'} btn-sm`}
              style={isSelected ? { backgroundColor: category.color, borderColor: category.color } : {}}
              onClick={() => onCategoryChange(categoryName)}
              title={category.description}
            >
              <span className="me-1">{category.icon}</span>
              {categoryName}
            </button>
          );
        })}
      </div>

      {allCategories.length > 12 && (
        <button
          className="btn btn-link btn-sm text-decoration-none"
          onClick={() => setShowAll(!showAll)}
        >
          {showAll ? '▲ Show Less' : '▼ Show More Categories'}
        </button>
      )}

      {/* Category groups dropdown for mobile */}
      <div className="dropdown d-md-none mt-2">
        <button
          className="btn btn-outline-secondary btn-sm dropdown-toggle w-100"
          type="button"
          data-bs-toggle="dropdown"
        >
          <i className="fas fa-filter me-2"></i>
          Filter by Category
        </button>
        <ul className="dropdown-menu w-100">
          <li>
            <a
              className={`dropdown-item ${selectedCategory === 'All' ? 'active' : ''}`}
              href="#"
              onClick={(e) => {
                e.preventDefault();
                onCategoryChange('All');
              }}
            >
              All Events
            </a>
          </li>
          <li><hr className="dropdown-divider" /></li>
          {Object.entries(grouped).map(([groupName, groupCategories]) => (
            <React.Fragment key={groupName}>
              <li><h6 className="dropdown-header">{groupName}</h6></li>
              {groupCategories.map((cat) => (
                <li key={cat}>
                  <a
                    className={`dropdown-item ${selectedCategory === cat ? 'active' : ''}`}
                    href="#"
                    onClick={(e) => {
                      e.preventDefault();
                      onCategoryChange(cat);
                    }}
                  >
                    <span className="me-2">{categories[cat]?.icon}</span>
                    {cat}
                  </a>
                </li>
              ))}
            </React.Fragment>
          ))}
        </ul>
      </div>
    </div>
  );
}
