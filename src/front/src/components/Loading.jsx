import React from 'react';

const Loading = ({ message = 'Loading...' }) => {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            width: '100%',
            height: '100%',
            minHeight: '50vh',
            gap: '1.5rem'
        }}>
            <div className="spinner" style={{
                border: '4px solid rgba(255, 255, 255, 0.08)',
                borderTop: '4px solid #fff',
                borderRadius: '50%',
                width: '48px',
                height: '48px',
                animation: 'spin 1s linear infinite'
            }} />
            <p>{message}</p>
            <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
        </div>
    );
};

export default Loading;
