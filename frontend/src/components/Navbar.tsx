import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

type NavbarProps = {
    appTitle: string;
    username: string;
    onLogout: () => void;
};

const Navbar: React.FC<NavbarProps> = ({ appTitle, username, onLogout }) => {
    const navigate = useNavigate();
    const location = useLocation();

    const navItems = [
        { path: '/projects', label: 'Projects' },
        { path: '/users', label: 'Users' }
    ];

    return (
        <nav style={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            padding: '0.5rem 1rem',
            backgroundColor: '#282c34',
            color: '#fff'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
                <div style={{ fontWeight: 'bold', fontSize: '1.2rem' }}>
                    {appTitle}
                </div>
                <div style={{ display: 'flex', gap: '1rem' }}>
                    {navItems.map(item => (
                        <button
                            key={item.path}
                            onClick={() => navigate(item.path)}
                            style={{
                                background: location.pathname === item.path ? '#61dafb' : 'transparent',
                                border: '1px solid #61dafb',
                                color: location.pathname === item.path ? '#000' : '#61dafb',
                                padding: '0.3rem 0.7rem',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '0.9rem'
                            }}
                        >
                            {item.label}
                        </button>
                    ))}
                </div>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span>{username}</span>
                <button onClick={onLogout} style={{
                    padding: '0.3rem 0.7rem',
                    background: '#dc3545',
                    border: 'none',
                    borderRadius: '4px',
                    cursor: 'pointer',
                    color: '#fff'
                }}>
                    Logout
                </button>
            </div>
        </nav>
    );
};

export default Navbar;