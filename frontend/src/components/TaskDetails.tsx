import React, { useState, useEffect } from 'react';
import { getUsers } from '../lib/user';
import type { User } from '../lib/user';
import type { TaskStatus } from '../lib/task';

interface Task {
    id: string;
    title: string;
    description: string;
    status?: TaskStatus;
    assignee_id?: number;
}

interface TaskDetailsProps {
    task: Task;
    onUpdate: (updatedTask: Task) => void;
    onDelete: (taskId: string) => void;
    onStatusChange?: (taskId: string, status: TaskStatus) => void;
    onAssigneeChange?: (taskId: string, assigneeId: number | null) => void;
}

const statusOrder: TaskStatus[] = ['Backlog', 'In Progress', 'Review', 'Done'];

const TaskDetails: React.FC<TaskDetailsProps> = ({
    task,
    onUpdate,
    onDelete,
    onStatusChange,
    onAssigneeChange
}) => {
    const [isEditing, setIsEditing] = useState(false);
    const [editedTask, setEditedTask] = useState<Task>(task);
    const [showDeleteModal, setShowDeleteModal] = useState(false);
    const [users, setUsers] = useState<User[]>([]);
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

    const handleEditChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
        const { name, value } = e.target;
        setEditedTask(prev => ({ ...prev, [name]: value }));
    };

    const handleSave = () => {
        onUpdate(editedTask);
        setIsEditing(false);
    };

    const handleDelete = () => {
        setShowDeleteModal(true);
    };

    const confirmDelete = () => {
        onDelete(task.id);
        setShowDeleteModal(false);
    };

    const cancelDelete = () => {
        setShowDeleteModal(false);
    };

    const getNextStatus = (currentStatus: TaskStatus): TaskStatus | null => {
        const currentIndex = statusOrder.indexOf(currentStatus);
        if (currentIndex < statusOrder.length - 1) {
            return statusOrder[currentIndex + 1];
        }
        return null;
    };

    const getPreviousStatus = (currentStatus: TaskStatus): TaskStatus | null => {
        const currentIndex = statusOrder.indexOf(currentStatus);
        if (currentIndex > 0) {
            return statusOrder[currentIndex - 1];
        }
        return null;
    };

    const handleStatusAdvance = () => {
        if (task.status && onStatusChange) {
            const nextStatus = getNextStatus(task.status);
            if (nextStatus) {
                // Validate that task is assigned before advancing from Backlog
                if (task.status === 'Backlog' && nextStatus === 'In Progress' && !task.assignee_id) {
                    alert('Task must be assigned to someone before it can be moved to In Progress');
                    return;
                }
                onStatusChange(task.id, nextStatus);
            }
        }
    };

    const handleStatusRevert = () => {
        if (task.status && onStatusChange) {
            const previousStatus = getPreviousStatus(task.status);
            if (previousStatus) {
                onStatusChange(task.id, previousStatus);
            }
        }
    };

    const handleAssigneeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
        const assigneeId = e.target.value ? parseInt(e.target.value) : null;
        if (onAssigneeChange) {
            onAssigneeChange(task.id, assigneeId);
        }
    };

    const getAssignedUser = () => {
        return users.find(user => user.id === task.assignee_id);
    };

    const nextStatus = task.status ? getNextStatus(task.status) : null;
    const previousStatus = task.status ? getPreviousStatus(task.status) : null;
    const assignedUser = getAssignedUser();

    return (
        <div style={{ border: '1px solid #ccc', padding: 16, borderRadius: 8, maxWidth: 600 }}>
            {isEditing ? (
                <div>
                    <input
                        type="text"
                        name="title"
                        value={editedTask.title}
                        onChange={handleEditChange}
                        style={{ width: '100%', marginBottom: 8 }}
                    />
                    <textarea
                        name="description"
                        value={editedTask.description}
                        onChange={handleEditChange}
                        style={{ width: '100%', marginBottom: 8, minHeight: '80px' }}
                    />
                    <button onClick={handleSave} style={{ marginRight: 8 }}>Save</button>
                    <button onClick={() => setIsEditing(false)}>Cancel</button>
                </div>
            ) : (
                <div>
                    <h2>{task.title}</h2>
                    <p>{task.description}</p>

                    {/* Status Section */}
                    {task.status && (
                        <div style={{ marginBottom: 16 }}>
                            <h4>Status: {task.status}</h4>
                            <div style={{ display: 'flex', gap: '8px', marginTop: 8 }}>
                                {previousStatus && (
                                    <button
                                        onClick={handleStatusRevert}
                                        style={{
                                            background: '#6c757d',
                                            color: 'white',
                                            border: 'none',
                                            padding: '6px 12px',
                                            borderRadius: 4
                                        }}
                                    >
                                        ← {previousStatus}
                                    </button>
                                )}
                                {nextStatus && (
                                    <button
                                        onClick={handleStatusAdvance}
                                        style={{
                                            background: '#28a745',
                                            color: 'white',
                                            border: 'none',
                                            padding: '6px 12px',
                                            borderRadius: 4
                                        }}
                                    >
                                        {nextStatus} →
                                    </button>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Assignee Section */}
                    <div style={{ marginBottom: 16 }}>
                        <h4>Assignee</h4>
                        {assignedUser ? (
                            <div style={{ marginBottom: 8 }}>
                                <span style={{
                                    background: '#090c0f',
                                    padding: '4px 8px',
                                    borderRadius: 4,
                                    marginRight: 8
                                }}>
                                    {assignedUser.full_name} ({assignedUser.role})
                                </span>
                            </div>
                        ) : (
                            <p style={{ color: '#6c757d', fontStyle: 'italic' }}>Unassigned</p>
                        )}

                        <select
                            value={task.assignee_id || ''}
                            onChange={handleAssigneeChange}
                            style={{ padding: '4px 8px', borderRadius: 4, border: '1px solid #ccc' }}
                        >
                            <option value="">Unassigned</option>
                            {users.map(user => (
                                <option key={user.id} value={user.id}>
                                    {user.full_name} ({user.role})
                                </option>
                            ))}
                        </select>
                    </div>

                    <div style={{ borderTop: '1px solid #eee', paddingTop: 16 }}>
                        <button onClick={() => setIsEditing(true)} style={{ marginRight: 8 }}>Edit</button>
                        <button onClick={handleDelete} style={{ color: 'red' }}>Delete</button>
                    </div>
                </div>
            )}

            {showDeleteModal && (
                <div
                    style={{
                        position: 'fixed',
                        top: 0, left: 0, right: 0, bottom: 0,
                        background: 'rgba(0,0,0,0.3)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center'
                    }}
                >
                    <div style={{ background: '#161616', padding: 24, borderRadius: 8, minWidth: 300 }}>
                        <h3>Confirm Deletion</h3>
                        <p>Are you sure you want to delete this task?</p>
                        <button onClick={confirmDelete} style={{ color: 'red', marginRight: 8 }}>Delete</button>
                        <button onClick={cancelDelete}>Cancel</button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default TaskDetails;