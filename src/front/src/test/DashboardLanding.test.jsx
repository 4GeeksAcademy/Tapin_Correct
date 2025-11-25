import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import DashboardLanding from '../pages/DashboardLanding';

describe('DashboardLanding', () => {
    it('renders landing page and CTA buttons', () => {
        render(<DashboardLanding />);
        expect(screen.getByText(/TapIn/i)).toBeInTheDocument();
        expect(screen.getByText(/Get Started/i)).toBeInTheDocument();
        expect(screen.getByText(/Log In/i)).toBeInTheDocument();
    });

    it('shows AuthForm when Get Started is clicked', () => {
        render(<DashboardLanding />);
        fireEvent.click(screen.getByText(/Get Started/i));
        expect(screen.getByText(/Login/i)).toBeInTheDocument();
        expect(screen.getByText(/Register/i)).toBeInTheDocument();
    });

    it('shows AuthForm when Log In is clicked', () => {
        render(<DashboardLanding />);
        fireEvent.click(screen.getByText(/Log In/i));
        expect(screen.getByText(/Login/i)).toBeInTheDocument();
        expect(screen.getByText(/Register/i)).toBeInTheDocument();
    });
});
