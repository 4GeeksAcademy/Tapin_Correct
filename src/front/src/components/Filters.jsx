import React from 'react';
import { CATEGORIES } from '../config/categories';

export default function Filters({ active, onChange }) {
  return (
    <div className="filters">
      <div className="chips">
        {CATEGORIES.map((category) => (
          <button
            key={category.id}
            className={`chip ${active === category.name ? 'active' : ''}`}
            onClick={() => onChange && onChange(category.name)}
            style={{
              borderColor: active === category.name ? category.color : undefined,
              backgroundColor: active === category.name ? category.color : undefined,
            }}
          >
            {category.icon} {category.name}
          </button>
        ))}
      </div>
    </div>
  );
}
