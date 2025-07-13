import React from 'react';

type NavbarProps = {
    appTitle: string;
    username: string;
    onLogout: () => void;
};

const Navbar: React.FC<NavbarProps> = ({ appTitle, username, onLogout }) => {
    return (
        <nav style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0.5rem 1rem',
            backgroundColor: '#282c34',
            color: '#fff'
        }}>
            <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
                {appTitle}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span>{username}</span>
                <button onClick={onLogout} style={{
                    padding: '0.3rem 0.7rem',
                    background: '#61dafb',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer'
                }}>
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;