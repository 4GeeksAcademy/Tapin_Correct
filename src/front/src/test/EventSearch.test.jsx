import React from 'react';
import { render, screen } from '@testing-library/react';
import EventSearch from '../components/EventSearch';

const mockCategories = ['All', 'Test Category'];

test('renders EventSearch component', () => {
    render(<EventSearch categories={mockCategories} />);
    const searchButton = screen.getByRole('button', { name: /Search/i });
    expect(searchButton).toBeInTheDocument();
});
