import React, { useState, useEffect } from 'react';
import { updateProject, deleteProject } from '../lib/project';
import { getUsers } from '../lib/user';
import type { Project, ProjectUpdate, ProjectStatus } from '../lib/project';
import type { User } from '../lib/user';

interface ProjectEditModalProps {
    project: Project;
    isOpen: boolean;
    onClose: () => void;
    onUpdate: (updatedProject: Project) => void;
    onDelete: (projectId: number) => void;
}

const ProjectEditModal: React.FC<ProjectEditModalProps> = ({
    project,
    isOpen,
    onClose,
    onUpdate,
    onDelete
}) => {
    const [editedProject, setEditedProject] = useState<ProjectUpdate>({
        name: project.name,
        description: project.description || '',
        owner_id: project.owner_id,
        status: project.status || 'Active'
    });
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
    const [loadingUsers, setLoadingUsers] = useState(true);

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const userList = await getUsers();
                setUsers(userList);
            } catch (error) {
                console.error('Failed to fetch users:', error);
            } finally {
                setLoadingUsers(false);
            }
        };
        fetchUsers();
    }, []);

    useEffect(() => {
        if (isOpen) {
            setEditedProject({
                name: project.name,
                description: project.description || '',
                owner_id: project.owner_id,
                status: project.status || 'Active'
            });
            setError(null);
            setShowDeleteConfirm(false);
        }
    }, [isOpen, project]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setEditedProject(prev => ({
            ...prev,
            [name]: name === 'owner_id' ? parseInt(value) : value
        }));
    };

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!editedProject.name?.trim()) {
            setError('Project name is required');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const updatedProject = await updateProject(project.id, editedProject);
            onUpdate(updatedProject);
            onClose();
        } catch (err) {
            setError('Failed to update project');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async () => {
        try {
            setLoading(true);
            setError(null);
            await deleteProject(project.id);
            onDelete(project.id);
            onClose();
        } catch (err) {
            setError('Failed to delete project');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleDeleteConfirm = () => {
        setShowDeleteConfirm(true);
    };

    const handleDeleteCancel = () => {
        setShowDeleteConfirm(false);
    };

    if (!isOpen) return null;

    return (
        <div
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                right: 0,
                bottom: 0,
                background: 'rgba(0,0,0,0.5)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                zIndex: 1000
            }}
        >
            <div
                style={{
                    background: '#1a1a1a',
                    padding: '24px',
                    borderRadius: '8px',
                    minWidth: '500px',
                    maxWidth: '600px',
                    width: '90%',
                    color: 'white'
                }}
            >
                <h2 style={{ marginBottom: '20px' }}>Edit Project</h2>

                {error && (
                    <div style={{
                        background: '#f8d7da',
                        color: '#721c24',
                        padding: '12px',
                        borderRadius: '4px',
                        marginBottom: '20px',
                        border: '1px solid #f5c6cb'
                    }}>
                        {error}
                    </div>
                )}

                {!showDeleteConfirm ? (
                    <form onSubmit={handleSave}>
                        <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', marginBottom: '4px' }}>
                                Project Name *
                            </label>
                            <input
                                type="text"
                                name="name"
                                value={editedProject.name || ''}
                                onChange={handleInputChange}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: '4px',
                                    border: '1px solid #ccc',
                                    fontSize: '14px'
                                }}
                                required
                            />
                        </div>

                        <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', marginBottom: '4px' }}>
                                Description
                            </label>
                            <textarea
                                name="description"
                                value={editedProject.description || ''}
                                onChange={handleInputChange}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: '4px',
                                    border: '1px solid #ccc',
                                    fontSize: '14px',
                                    minHeight: '80px',
                                    resize: 'vertical'
                                }}
                            />
                        </div>

                        <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', marginBottom: '4px' }}>
                                Status
                            </label>
                            <select
                                name="status"
                                value={editedProject.status || 'Active'}
                                onChange={handleInputChange}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: '4px',
                                    border: '1px solid #ccc',
                                    fontSize: '14px'
                                }}
                            >
                                <option value="Active">Active</option>
                                <option value="Archived">Archived</option>
                            </select>
                        </div>

                        <div style={{ marginBottom: '16px' }}>
                            <label style={{ display: 'block', marginBottom: '4px' }}>
                                Owner
                            </label>
                            {loadingUsers ? (
                                <div style={{ color: '#999' }}>Loading users...</div>
                            ) : (
                                <select
                                    name="owner_id"
                                    value={editedProject.owner_id || ''}
                                    onChange={handleInputChange}
                                    style={{
                                        width: '100%',
                                        padding: '8px',
                                        borderRadius: '4px',
                                        border: '1px solid #ccc',
                                        fontSize: '14px'
                                    }}
                                    required
                                >
                                    <option value="">Select Owner</option>
                                    {users.map(user => (
                                        <option key={user.id} value={user.id}>
                                            {user.full_name} ({user.role})
                                        </option>
                                    ))}
                                </select>
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                            <button
                                type="button"
                                onClick={handleDeleteConfirm}
                                disabled={loading}
                                style={{
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    border: '1px solid #dc3545',
                                    background: 'transparent',
                                    color: '#dc3545',
                                    cursor: loading ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Delete
                            </button>
                            <button
                                type="button"
                                onClick={onClose}
                                disabled={loading}
                                style={{
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    border: '1px solid #6c757d',
                                    background: 'transparent',
                                    color: '#6c757d',
                                    cursor: loading ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                type="submit"
                                disabled={loading}
                                style={{
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    border: 'none',
                                    background: '#28a745',
                                    color: 'white',
                                    cursor: loading ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {loading ? 'Saving...' : 'Save'}
                            </button>
                        </div>
                    </form>
                ) : (
                    <div>
                        <h3 style={{ marginBottom: '16px' }}>Confirm Deletion</h3>
                        <p style={{ marginBottom: '20px' }}>
                            Are you sure you want to delete the project "{project.name}"?
                            This action cannot be undone and will also delete all associated tasks.
                        </p>
                        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                            <button
                                type="button"
                                onClick={handleDeleteCancel}
                                disabled={loading}
                                style={{
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    border: '1px solid #6c757d',
                                    background: 'transparent',
                                    color: '#6c757d',
                                    cursor: loading ? 'not-allowed' : 'pointer'
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                type="button"
                                onClick={handleDelete}
                                disabled={loading}
                                style={{
                                    padding: '8px 16px',
                                    borderRadius: '4px',
                                    border: 'none',
                                    background: '#dc3545',
                                    color: 'white',
                                    cursor: loading ? 'not-allowed' : 'pointer'
                                }}
                            >
                                {loading ? 'Deleting...' : 'Delete Project'}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default ProjectEditModal;
