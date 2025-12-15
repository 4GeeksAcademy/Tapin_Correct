import React, { useState, useEffect } from 'react';

const predefinedValues = [
    "Animal Welfare",
    "Arts & Culture",
    "Children & Youth",
    "Community Development",
    "Disaster Relief",
    "Education & Literacy",
    "Environment",
    "Health & Medicine",
    "Human Rights",
    "Seniors",
    "Social Services",
    "Sports & Recreation",
    "Technology",
    "Women's Issues",
];

export default function ValuesSelector({ user, onSave }) {
    const [selectedValues, setSelectedValues] = useState([]);

    useEffect(() => {

        const fetchUserValues = async () => {
            const token = localStorage.getItem('access_token');
            const response = await fetch('/user/values', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            const data = await response.json();
            setSelectedValues(data.values);
        };
        fetchUserValues();
    }, [user]);

    const handleValueChange = (value) => {
        const newSelectedValues = selectedValues.includes(value)
            ? selectedValues.filter(v => v !== value)
            : [...selectedValues, value];
        setSelectedValues(newSelectedValues);
    };

    const handleSave = async () => {
        const token = localStorage.getItem('access_token');

        for (const value of selectedValues) {
            await fetch('/user/values', {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ value })
            });
        }

        for (const value of selectedValues) {
            await fetch('/user/values', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ value })
            });
        }
        if (onSave) {
            onSave(selectedValues);
        }
    };

    return (
        <div>
            <h2>Select Your Values</h2>
            <div>
                {predefinedValues.map(value => (
                    <label key={value}>
                        <input
                            type="checkbox"
                            checked={selectedValues.includes(value)}
                            onChange={() => handleValueChange(value)}
                        />
                        {value}
                    </label>
                ))}
            </div>
            <button onClick={handleSave}>Save</button>
        </div>
    );
}
