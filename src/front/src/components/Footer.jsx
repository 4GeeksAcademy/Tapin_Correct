import React from 'react';
import logoIcon from '@/assets/brand/logo-icon.svg';

export default function Footer() {
    return (
        <footer className="app-footer" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '16px', borderTop: '1px solid #E6E9EE', marginTop: 24 }}>
            <img src={logoIcon} alt="Tapin logo" style={{ width: 44, height: 44, marginRight: 10 }} />
            <div style={{ color: '#64748b', fontSize: 14 }}>© {new Date().getFullYear()} TapIn • School Project</div>
        </footer>
    );
}
