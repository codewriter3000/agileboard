import React, { useState } from 'react';
import { updateUser } from '../lib/user';
import type { User, UserUpdatePayload } from '../lib/user';

interface UserEditModalProps {
    user: User;
    onUserUpdated: (user: User) => void;
    onCancel: () => void;
}

const UserEditModal: React.FC<UserEditModalProps> = ({ user, onUserUpdated, onCancel }) => {
    const [formData, setFormData] = useState<UserUpdatePayload>({
        full_name: user.full_name,
        role: user.role
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const updatedUser = await updateUser(user.id, formData);
            onUserUpdated(updatedUser);
        } catch (err: unknown) {
            setError((err as { response?: { data?: { detail?: string } } })?.response?.data?.detail || 'Failed to update user');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div
            style={{
                position: 'fixed',
                top: 0, left: 0, right: 0, bottom: 0,
                background: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}
        >
            <div style={{
                background: '#161616',
                padding: '24px',
                borderRadius: '8px',
                minWidth: '400px',
                maxWidth: '500px',
                width: '90%'
            }}>
                <h2 style={{ margin: '0 0 20px 0', color: '#fff' }}>Edit User</h2>

                {error && (
                    <div style={{
                        background: '#dc3545',
                        color: 'white',
                        padding: '8px 12px',
                        borderRadius: '4px',
                        marginBottom: '16px'
                    }}>
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '4px', color: '#fff' }}>
                            Email (Read-only)
                        </label>
                        <input
                            type="email"
                            value={user.email}
                            disabled
                            style={{
                                width: '100%',
                                padding: '8px',
                                borderRadius: '4px',
                                border: '1px solid #ccc',
                                fontSize: '14px',
                                background: '#f5f5f5',
                                color: '#666'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '4px', color: '#fff' }}>
                            Full Name *
                        </label>
                        <input
                            type="text"
                            name="full_name"
                            value={formData.full_name}
                            onChange={handleChange}
                            required
                            style={{
                                width: '100%',
                                padding: '8px',
                                borderRadius: '4px',
                                border: '1px solid #ccc',
                                fontSize: '14px'
                            }}
                        />
                    </div>

                    <div style={{ marginBottom: '20px' }}>
                        <label style={{ display: 'block', marginBottom: '4px', color: '#fff' }}>
                            Role *
                        </label>
                        <select
                            name="role"
                            value={formData.role}
                            onChange={handleChange}
                            style={{
                                width: '100%',
                                padding: '8px',
                                borderRadius: '4px',
                                border: '1px solid #ccc',
                                fontSize: '14px'
                            }}
                        >
                            <option value="Developer">Developer</option>
                            <option value="ScrumMaster">Scrum Master</option>
                            <option value="Admin">Admin</option>
                        </select>
                    </div>

                    <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                        <button
                            type="button"
                            onClick={onCancel}
                            style={{
                                background: '#6c757d',
                                color: 'white',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px',
                                cursor: 'pointer'
                            }}
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={loading}
                            style={{
                                background: loading ? '#6c757d' : '#28a745',
                                color: 'white',
                                border: 'none',
                                padding: '8px 16px',
                                borderRadius: '4px',
                                cursor: loading ? 'not-allowed' : 'pointer'
                            }}
                        >
                            {loading ? 'Updating...' : 'Update User'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default UserEditModal;
