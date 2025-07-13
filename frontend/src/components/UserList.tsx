import React, { useState, useEffect } from 'react';
import { getUsers, deleteUser } from '../lib/user';
import type { User } from '../lib/user';
import UserCreateModal from './UserCreateModal';
import UserEditModal from './UserEditModal';

export const UserList: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [editingUser, setEditingUser] = useState<User | null>(null);
    const [searchTerm, setSearchTerm] = useState('');
    const [deleteConfirmUser, setDeleteConfirmUser] = useState<User | null>(null);

    useEffect(() => {
        loadUsers();
    }, []);

    const loadUsers = async () => {
        try {
            setLoading(true);
            const data = await getUsers();
            setUsers(data);
        } catch (err) {
            setError('Failed to load users');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleUserCreated = (newUser: User) => {
        setUsers([...users, newUser]);
        setShowCreateModal(false);
    };

    const handleUserUpdated = (updatedUser: User) => {
        setUsers(users.map(user =>
            user.id === updatedUser.id ? updatedUser : user
        ));
        setEditingUser(null);
    };

    const handleDeleteUser = async (user: User) => {
        try {
            await deleteUser(user.id);
            setUsers(users.filter(u => u.id !== user.id));
            setDeleteConfirmUser(null);
        } catch (err) {
            setError('Failed to delete user');
            console.error(err);
        }
    };

    const filteredUsers = users.filter(user =>
        user.full_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
        user.role.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const getRoleColor = (role: string) => {
        switch (role) {
            case 'Admin': return '#dc3545';
            case 'ScrumMaster': return '#007bff';
            case 'Developer': return '#28a745';
            default: return '#6c757d';
        }
    };

    if (loading) return <div>Loading users...</div>;
    if (error) return <div className="error">Error: {error}</div>;

    return (
        <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                <h1>User Management</h1>
                <button
                    onClick={() => setShowCreateModal(true)}
                    style={{
                        background: '#007bff',
                        color: 'white',
                        border: 'none',
                        padding: '8px 16px',
                        borderRadius: '4px',
                        cursor: 'pointer'
                    }}
                >
                    Add User
                </button>
            </div>

            <div style={{ marginBottom: '20px' }}>
                <input
                    type="text"
                    placeholder="Search users by name, email, or role..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                        width: '300px',
                        padding: '8px',
                        borderRadius: '4px',
                        border: '1px solid #ccc'
                    }}
                />
            </div>

            <div style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(400px, 1fr))',
                gap: '20px'
            }}>
                {filteredUsers.map(user => (
                    <div
                        key={user.id}
                        style={{
                            border: '1px solid #e0e0e0',
                            borderRadius: '8px',
                            padding: '20px',
                            background: '#2c2c2c',
                            boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                        }}
                    >
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                            <div>
                                <h3 style={{ margin: '0 0 8px 0', color: '#fff' }}>{user.full_name}</h3>
                                <p style={{ margin: '0 0 8px 0', color: '#ccc' }}>{user.email}</p>
                                <span
                                    style={{
                                        background: getRoleColor(user.role),
                                        color: 'white',
                                        padding: '2px 8px',
                                        borderRadius: '12px',
                                        fontSize: '12px',
                                        fontWeight: 'bold'
                                    }}
                                >
                                    {user.role}
                                </span>
                            </div>
                            <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                    onClick={() => setEditingUser(user)}
                                    style={{
                                        background: '#28a745',
                                        color: 'white',
                                        border: 'none',
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        fontSize: '12px'
                                    }}
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => setDeleteConfirmUser(user)}
                                    style={{
                                        background: '#dc3545',
                                        color: 'white',
                                        border: 'none',
                                        padding: '4px 8px',
                                        borderRadius: '4px',
                                        cursor: 'pointer',
                                        fontSize: '12px'
                                    }}
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {filteredUsers.length === 0 && (
                <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
                    {searchTerm ? 'No users found matching your search.' : 'No users found.'}
                </div>
            )}

            {showCreateModal && (
                <UserCreateModal
                    onUserCreated={handleUserCreated}
                    onCancel={() => setShowCreateModal(false)}
                />
            )}

            {editingUser && (
                <UserEditModal
                    user={editingUser}
                    onUserUpdated={handleUserUpdated}
                    onCancel={() => setEditingUser(null)}
                />
            )}

            {deleteConfirmUser && (
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
                        textAlign: 'center'
                    }}>
                        <h3>Confirm Delete</h3>
                        <p>Are you sure you want to delete user "{deleteConfirmUser.full_name}"?</p>
                        <p style={{ color: '#666', fontSize: '14px' }}>This action cannot be undone.</p>
                        <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', marginTop: '20px' }}>
                            <button
                                onClick={() => handleDeleteUser(deleteConfirmUser)}
                                style={{
                                    background: '#dc3545',
                                    color: 'white',
                                    border: 'none',
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    cursor: 'pointer'
                                }}
                            >
                                Delete
                            </button>
                            <button
                                onClick={() => setDeleteConfirmUser(null)}
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
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default UserList;
