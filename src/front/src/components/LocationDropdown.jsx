import React, { useState, useRef, useEffect } from 'react';
import CITIES from '../data/cities_na.json';

/**
 * Reusable location dropdown with fuzzy matching and optional proximity sorting.
 * Returns { name, lat, lon } when a city is selected.
 * @param {Object} props
 * @param {string} props.value - current input value
 * @param {Function} props.onChange - called when input changes: (val) => void
 * @param {Function} props.onSelect - called when city is selected: ({ name, lat, lon }) => void
 * @param {Array} props.userCoords - optional [lat, lon] to sort by proximity
 * @param {string} props.placeholder - input placeholder
 * @param {string} props.countryFilter - optional country code (US, CA, MX) to filter by
 * @param {Function} props.isLoading - optional loading state callback
 */
export default function LocationDropdown({ value, onChange, onSelect, userCoords, placeholder = 'Location', countryFilter, isLoading }) {
    const [isOpen, setIsOpen] = useState(false);
    const [highlightedIndex, setHighlightedIndex] = useState(-1);
    const containerRef = useRef(null);

    // Haversine distance
    const haversine = (a, b) => {
        if (!a || !b) return Infinity;
        const toRad = (v) => (v * Math.PI) / 180;
        const [lat1, lon1] = a;
        const [lat2, lon2] = b;
        const R = 6371;
        const dLat = toRad(lat2 - lat1);
        const dLon = toRad(lon2 - lon1);
        const sLat = Math.sin(dLat / 2);
        const sLon = Math.sin(dLon / 2);
        const aVal = sLat * sLat + Math.cos(toRad(lat1)) * Math.cos(toRad(lat2)) * sLon * sLon;
        const c = 2 * Math.atan2(Math.sqrt(aVal), Math.sqrt(1 - aVal));
        return R * c;
    };

    // Simple fuzzy score (prefix > word-start > substring)
    const scoreCity = (query, city) => {
        const name = (city.name || '').toLowerCase();
        const q = (query || '').toLowerCase().trim();
        let score = 0;
        if (!q) score = 0;
        else {
            if (name.startsWith(q)) score -= 100;
            else if (name.split(/\s+/).some(w => w.startsWith(q))) score -= 50;
            else if (name.includes(q)) score -= 10;
            else score += 20;
        }
        if (userCoords && city.lat != null && city.lon != null) {
            const d = haversine(userCoords, [city.lat, city.lon]);
            score += d / 100;
        }
        return score;
    };

    // Generate filtered/sorted list
    const q = (value || '').trim().toLowerCase();
    let candidates = [];
    if (!q) {
        candidates = CITIES.slice();
        // Apply country filter if provided
        if (countryFilter) {
            candidates = candidates.filter(c => c.country === countryFilter);
        }
        if (userCoords) {
            candidates.sort((a, b) => {
                const da = haversine(userCoords, [a.lat, a.lon]);
                const db = haversine(userCoords, [b.lat, b.lon]);
                return da - db;
            });
        }
    } else {
        candidates = CITIES.filter(c => {
            const name = (c.name || '').toLowerCase();
            const matchesQuery = name.includes(q) || (c.country || '').toLowerCase().includes(q);
            const matchesCountry = !countryFilter || c.country === countryFilter;
            return matchesQuery && matchesCountry;
        });
        candidates = candidates.map(c => ({ c, score: scoreCity(q, c) }))
            .sort((x, y) => x.score - y.score)
            .map(x => x.c);
    }

    const filtered = candidates.slice(0, 30);

    useEffect(() => {
        function onDocClick(e) {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setIsOpen(false);
                setHighlightedIndex(-1);
            }
        }
        document.addEventListener('mousedown', onDocClick);
        return () => document.removeEventListener('mousedown', onDocClick);
    }, []);

    const handleSelect = (city) => {
        if (!city) return;
        onChange(city.name);
        setIsOpen(false);
        setHighlightedIndex(-1);
        if (onSelect) onSelect({ name: city.name, lat: city.lat, lon: city.lon });
    };

    return (
        <div ref={containerRef} style={{ position: 'relative' }}>
            <div style={{ position: 'relative' }}>
                <input
                    value={value}
                    onChange={(e) => {
                        onChange(e.target.value);
                        setIsOpen(true);
                        setHighlightedIndex(0);
                    }}
                    onFocus={() => setIsOpen(true)}
                    onKeyDown={(e) => {
                        if (e.key === 'ArrowDown') {
                            e.preventDefault();
                            setIsOpen(true);
                            setHighlightedIndex(i => Math.min(i + 1, filtered.length - 1));
                        } else if (e.key === 'ArrowUp') {
                            e.preventDefault();
                            setHighlightedIndex(i => Math.max(i - 1, 0));
                        } else if (e.key === 'Enter') {
                            if (isOpen && highlightedIndex >= 0 && highlightedIndex < filtered.length) {
                                e.preventDefault();
                                handleSelect(filtered[highlightedIndex]);
                            }
                        } else if (e.key === 'Escape') {
                            setIsOpen(false);
                            setHighlightedIndex(-1);
                        }
                    }}
                    placeholder={placeholder}
                    style={{
                        width: '100%',
                        padding: '10px 16px',
                        fontSize: '14px',
                        background: 'white',
                        color: '#333',
                        border: '1px solid #ddd',
                        borderRadius: '6px',
                        boxSizing: 'border-box'
                    }}
                />

                {value && (
                    <button
                        onClick={() => {
                            onChange('');
                            setIsOpen(false);
                            setHighlightedIndex(-1);
                        }}
                        aria-label="clear location"
                        style={{
                            position: 'absolute',
                            right: '8px',
                            top: '50%',
                            transform: 'translateY(-50%)',
                            border: 'none',
                            background: 'transparent',
                            color: '#999',
                            cursor: 'pointer',
                            fontSize: '18px'
                        }}
                    >
                        ×
                    </button>
                )}
            </div>

            {isOpen && (
                <ul role="listbox" style={{
                    position: 'absolute',
                    left: 0,
                    right: 0,
                    maxHeight: '240px',
                    overflow: 'auto',
                    marginTop: '4px',
                    background: 'white',
                    color: '#222',
                    borderRadius: '6px',
                    border: '1px solid #ddd',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    padding: '4px',
                    listStyle: 'none',
                    zIndex: 40
                }}>
                    {filtered.length === 0 && (
                        <li style={{ padding: '8px 12px', color: '#999' }}>No matches</li>
                    )}
                    {filtered.map((city, idx) => (
                        <li
                            key={city.name}
                            role="option"
                            aria-selected={highlightedIndex === idx}
                            onMouseDown={(e) => { e.preventDefault(); handleSelect(city); }}
                            onMouseEnter={() => setHighlightedIndex(idx)}
                            style={{
                                padding: '8px 12px',
                                borderRadius: '4px',
                                background: highlightedIndex === idx ? 'rgba(102,126,234,0.08)' : 'transparent',
                                cursor: 'pointer',
                                display: 'flex',
                                justifyContent: 'space-between',
                                alignItems: 'center'
                            }}
                        >
                            <span>{city.name}</span>
                            <small style={{ color: '#999', marginLeft: 8 }}>{city.country}</small>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
}
