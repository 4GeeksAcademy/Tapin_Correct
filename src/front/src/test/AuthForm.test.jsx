import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AuthForm from '../components/AuthForm';

describe('AuthForm', () => {
    it('renders login and register tabs', () => {
        render(<AuthForm onLogin={() => { }} />);
        expect(screen.getByText(/Login/i)).toBeInTheDocument();
        expect(screen.getByText(/Register/i)).toBeInTheDocument();
    });

    it('shows error if passwords do not match on register', async () => {
        render(<AuthForm onLogin={() => { }} />);
        fireEvent.click(screen.getByText(/Register/i));
        fireEvent.change(screen.getByPlaceholderText(/email/i), { target: { value: 'test@example.com' } });
        fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'abc123' } });
        fireEvent.change(screen.getByPlaceholderText(/confirm password/i), { target: { value: 'xyz789' } });
        fireEvent.click(screen.getByRole('button', { name: /register/i }));
        await waitFor(() => {
            expect(screen.getByText(/Passwords do not match/i)).toBeInTheDocument();
        });
    });

    it('shows error if organization name is missing for org registration', async () => {
        render(<AuthForm onLogin={() => { }} />);
        fireEvent.click(screen.getByText(/Register/i));
        fireEvent.click(screen.getByLabelText(/Organization/i));
        fireEvent.change(screen.getByPlaceholderText(/email/i), { target: { value: 'org@example.com' } });
        fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'abc123' } });
        fireEvent.change(screen.getByPlaceholderText(/confirm password/i), { target: { value: 'abc123' } });
        fireEvent.click(screen.getByRole('button', { name: /register/i }));
        await waitFor(() => {
            expect(screen.getByText(/Organization name is required/i)).toBeInTheDocument();
        });
    });
});
