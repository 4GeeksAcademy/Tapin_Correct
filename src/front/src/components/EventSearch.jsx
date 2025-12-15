import React, { useState } from 'react';
import { CATEGORIES } from '../categories';

export default function EventSearch() {
    const [query, setQuery] = useState('');
    const [category, setCategory] = useState('All');
    const [results, setResults] = useState([]);
    const [error, setError] = useState(null);

    const handleSearch = async (e) => {
        e.preventDefault();
        setError(null);

        if (!query) {
            return;
        }

        try {
            const response = await fetch(`/api/search/events?q=${query}&category=${category}`);
            const data = await response.json();

            if (data.error) {
                setError(data.error);
                setResults([]);
            } else {
                setResults(data);
            }
        } catch (err) {
            setError('An unexpected error occurred. Please try again.');
            setResults([]);
        }
    };

    return (
        <div className="event-search-container">
            <h2>Search for External Volunteer Opportunities</h2>
            <form onSubmit={handleSearch}>
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="e.g., 'animal shelter in Los Angeles'"
                    className="search-input"
                />
                <select value={category} onChange={(e) => setCategory(e.target.value)}>
                    {CATEGORIES.map(cat => (
                        <option key={cat} value={cat}>{cat}</option>
                    ))}
                </select>
                <button type="submit" className="search-button">Search</button>
            </form>

            {error && <p className="error-message">{error}</p>}

            <div className="results-container">
                {results.map((item, index) => (
                    <div key={index} className="result-item">
                        <h3><a href={item.link} target="_blank" rel="noopener noreferrer">{item.title}</a></h3>
                        <p>{item.snippet}</p>
                        <a href={item.link} target="_blank" rel="noopener noreferrer" className="result-link">View Opportunity</a>
                    </div>
                ))}
            </div>
        </div>
    );
}
