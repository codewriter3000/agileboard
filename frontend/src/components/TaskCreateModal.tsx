import React, { useState, useEffect } from 'react';
import { createTask } from '../lib/task';
import { getUsers } from '../lib/user';
import type { TaskCreate, Task } from '../lib/task';
import type { User } from '../lib/user';

interface TaskCreateModalProps {
    projectId: number;
    isOpen: boolean;
    onClose: () => void;
    onTaskCreated: (newTask: Task) => void;
}

const TaskCreateModal: React.FC<TaskCreateModalProps> = ({
    projectId,
    isOpen,
    onClose,
    onTaskCreated
}) => {
    const [newTask, setNewTask] = useState<TaskCreate>({
        title: '',
        description: '',
        status: 'Backlog',
        project_id: projectId,
        assignee_id: undefined,
        sprint_id: undefined
    });
    const [users, setUsers] = useState<User[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
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
            setNewTask({
                title: '',
                description: '',
                status: 'Backlog',
                project_id: projectId,
                assignee_id: undefined,
                sprint_id: undefined
            });
            setError(null);
        }
    }, [isOpen, projectId]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
        const { name, value } = e.target;
        setNewTask(prev => ({
            ...prev,
            [name]: name === 'assignee_id' ? (value ? parseInt(value) : undefined) : value
        }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!newTask.title.trim()) {
            setError('Task title is required');
            return;
        }

        // Validate assignee requirement for active statuses
        if (newTask.status !== 'Backlog' && !newTask.assignee_id) {
            setError('Assignee is required when task status is not Backlog');
            return;
        }

        try {
            setLoading(true);
            setError(null);
            const createdTask = await createTask(newTask);
            onTaskCreated(createdTask);
            onClose();
        } catch (err: unknown) {
            const error = err as { response?: { data?: { detail?: string } } };
            setError(error.response?.data?.detail || 'Failed to create task');
            console.error(err);
        } finally {
            setLoading(false);
        }
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
                    color: 'white',
                    maxHeight: '80vh',
                    overflowY: 'auto'
                }}
            >
                <h2 style={{ marginBottom: '20px' }}>Create New Task</h2>

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

                <form onSubmit={handleSubmit}>
                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '4px' }}>
                            Task Title *
                        </label>
                        <input
                            type="text"
                            name="title"
                            value={newTask.title}
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
                            value={newTask.description || ''}
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
                            value={newTask.status}
                            onChange={handleInputChange}
                            style={{
                                width: '100%',
                                padding: '8px',
                                borderRadius: '4px',
                                border: '1px solid #ccc',
                                fontSize: '14px'
                            }}
                        >
                            <option value="Backlog">Backlog</option>
                            <option value="In Progress">In Progress</option>
                            <option value="Review">Review</option>
                            <option value="Done">Done</option>
                        </select>
                    </div>

                    <div style={{ marginBottom: '16px' }}>
                        <label style={{ display: 'block', marginBottom: '4px' }}>
                            Assignee
                        </label>
                        {loadingUsers ? (
                            <div style={{ color: '#999' }}>Loading users...</div>
                        ) : (
                            <select
                                name="assignee_id"
                                value={newTask.assignee_id || ''}
                                onChange={handleInputChange}
                                style={{
                                    width: '100%',
                                    padding: '8px',
                                    borderRadius: '4px',
                                    border: '1px solid #ccc',
                                    fontSize: '14px'
                                }}
                            >
                                <option value="">Unassigned</option>
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
                            {loading ? 'Creating...' : 'Create Task'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default TaskCreateModal;
