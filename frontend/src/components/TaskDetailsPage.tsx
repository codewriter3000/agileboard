import React, { useState, useEffect } from 'react';
import { useParams, Navigate, useNavigate } from 'react-router-dom';
import TaskDetails from './TaskDetails';
import { getTask, updateTask, deleteTask } from '../lib/task';
import type { TaskUpdate, Task, TaskStatus } from '../lib/task';

// Type mapping from API to component
type ComponentTask = {
    id: string;
    title: string;
    description: string;
    status?: TaskStatus;
    assignee_id?: number;
};

export const TaskDetailsPage: React.FC = () => {
    const { projectId, taskId } = useParams<{ projectId: string; taskId: string }>();
    const navigate = useNavigate();
    const [task, setTask] = useState<ComponentTask | null>(null);
    const [originalTask, setOriginalTask] = useState<Task | null>(null); // Store original API task
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);    useEffect(() => {
        const fetchTask = async () => {
            if (!taskId) return;

            try {
                setLoading(true);
                const apiTask = await getTask(parseInt(taskId));

                // Store original task for updates
                setOriginalTask(apiTask);

                // Convert API task to component format
                const componentTask: ComponentTask = {
                    id: apiTask.id.toString(),
                    title: apiTask.title,
                    description: apiTask.description || '',
                    status: apiTask.status,
                    assignee_id: apiTask.assignee_id
                };

                setTask(componentTask);
            } catch (err) {
                setError('Failed to load task');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchTask();
    }, [taskId]);

    const handleUpdate = async (updatedTask: ComponentTask) => {
        if (!originalTask) return;

        try {
            // Only send the fields that were actually changed
            const updateData: TaskUpdate = {
                title: updatedTask.title,
                description: updatedTask.description,
                // Preserve existing values from original task
                status: originalTask.status,
                assignee_id: originalTask.assignee_id,
                project_id: originalTask.project_id,
                sprint_id: originalTask.sprint_id
            };

            const updated = await updateTask(parseInt(updatedTask.id), updateData);
            setOriginalTask(updated);
            setTask(updatedTask);
        } catch (err) {
            setError('Failed to update task');
            console.error(err);
        }
    };

    const handleStatusChange = async (taskId: string, status: TaskStatus) => {
        if (!originalTask) return;

        // Frontend validation: Check if task is being moved from Backlog to In Progress without an assignee
        if (originalTask.status === 'Backlog' && status === 'In Progress' && !originalTask.assignee_id) {
            setError('Task must be assigned to someone before it can be moved to In Progress');
            return;
        }

        try {
            const updateData: TaskUpdate = {
                status: status,
                // Include assignee_id if required for the new status
                ...(status !== 'Backlog' && { assignee_id: originalTask.assignee_id })
            };

            const updated = await updateTask(parseInt(taskId), updateData);
            setOriginalTask(updated);
            setTask(prev => prev ? { ...prev, status: status } : null);
            setError(null); // Clear any previous errors
        } catch (err: unknown) {
            // Handle specific validation errors from the backend
            const error = err as { response?: { status?: number; data?: { detail?: string } } };
            if (error.response?.status === 400 || error.response?.status === 422) {
                const errorMessage = error.response?.data?.detail || 'Validation error occurred';
                setError(typeof errorMessage === 'string' ? errorMessage : 'Task validation failed');
            } else {
                setError('Failed to update task status');
            }
            console.error(err);
        }
    };

    const handleAssigneeChange = async (taskId: string, assigneeId: number | null) => {
        if (!originalTask) return;

        try {
            const updateData: TaskUpdate = {
                assignee_id: assigneeId || undefined
            };

            const updated = await updateTask(parseInt(taskId), updateData);
            setOriginalTask(updated);
            setTask(prev => prev ? { ...prev, assignee_id: assigneeId || undefined } : null);
        } catch (err) {
            setError('Failed to update task assignee');
            console.error(err);
        }
    };

    const handleDelete = async (taskId: string) => {
        try {
            await deleteTask(parseInt(taskId));
            // Navigate back to project details after successful deletion
            navigate(`/projects/${projectId}`);
        } catch (err) {
            setError('Failed to delete task');
            console.error(err);
        }
    };

    if (!projectId || !taskId) {
        return <Navigate to="/projects" replace />;
    }

    if (loading) {
        return <div>Loading task...</div>;
    }

    if (!task) {
        return (
            <div className="error">
                <h2>Task not found</h2>
                <p>The requested task could not be found.</p>
                <button onClick={() => navigate(`/projects/${projectId}`)}>
                    Back to Project
                </button>
            </div>
        );
    }

    return (
        <div style={{ padding: '20px' }}>
            <button
                onClick={() => navigate(`/projects/${projectId}`)}
                style={{ marginBottom: '20px' }}
            >
                ← Back to Project
            </button>

            {error && (
                <div style={{
                    background: '#f8d7da',
                    color: '#721c24',
                    padding: '12px',
                    borderRadius: '4px',
                    marginBottom: '20px',
                    border: '1px solid #f5c6cb'
                }}>
                    <strong>Error:</strong> {error}
                    <button
                        onClick={() => setError(null)}
                        style={{
                            float: 'right',
                            background: 'transparent',
                            border: 'none',
                            color: '#721c24',
                            cursor: 'pointer',
                            fontSize: '16px'
                        }}
                    >
                        ×
                    </button>
                </div>
            )}

            <TaskDetails
                task={task}
                onUpdate={handleUpdate}
                onDelete={handleDelete}
                onStatusChange={handleStatusChange}
                onAssigneeChange={handleAssigneeChange}
            />
        </div>
    );
};
