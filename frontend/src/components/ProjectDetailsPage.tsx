import React, { useState, useEffect } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { ProjectDetails } from './ProjectDetails';
import { getProject, getProjectTasks } from '../lib/project';
import { getUsers } from '../lib/user';
import TaskCreateModal from './TaskCreateModal';
import ProjectEditModal from './ProjectEditModal';
import type { Task } from '../lib/task';
import type { User } from '../lib/user';
import type { Project } from '../lib/project';

// Type mapping from API to component
type ComponentTask = {
    id: number;
    title: string;
    description: string;
    status: 'Backlog' | 'In Progress' | 'Review' | 'Done';
    assignee_id?: number;
    assignee_name?: string;
};

type ComponentProject = {
    id: number;
    name: string;
    description: string;
    owner: string;
    owner_id: number;
    status: 'Active' | 'Archived';
    startDate: string;
    endDate?: string;
    tasks: ComponentTask[];
    originalProject: Project; // Keep reference to original API data
};

export const ProjectDetailsPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [project, setProject] = useState<ComponentProject | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showCreateTaskModal, setShowCreateTaskModal] = useState(false);
    const [showEditProjectModal, setShowEditProjectModal] = useState(false);
    const [users, setUsers] = useState<User[]>([]);    useEffect(() => {
        const fetchProject = async () => {
            if (!id) return;

            try {
                setLoading(true);
                const [apiProject, projectTasks, users] = await Promise.all([
                    getProject(parseInt(id)),
                    getProjectTasks(parseInt(id)),
                    getUsers()
                ]);

                // Create a user lookup map
                const userMap = new Map<number, User>();
                users.forEach(user => userMap.set(user.id, user));
                setUsers(users); // Store users for later use

                // Convert API tasks to component format
                const componentTasks: ComponentTask[] = projectTasks.map((task: Task) => ({
                    id: task.id,
                    title: task.title,
                    description: task.description || '',
                    status: task.status,
                    assignee_id: task.assignee_id,
                    assignee_name: task.assignee_id ? userMap.get(task.assignee_id)?.full_name : undefined
                }));

                // Convert API project to component format
                const ownerUser = userMap.get(apiProject.owner_id);
                const componentProject: ComponentProject = {
                    id: apiProject.id,
                    name: apiProject.name,
                    description: apiProject.description || '',
                    owner: ownerUser ? `${ownerUser.full_name} (${ownerUser.role})` : `User ${apiProject.owner_id}`,
                    owner_id: apiProject.owner_id,
                    status: apiProject.status || 'Active',
                    startDate: new Date(apiProject.created_at).toISOString().split('T')[0],
                    endDate: undefined,
                    tasks: componentTasks,
                    originalProject: apiProject
                };

                setProject(componentProject);
            } catch (err) {
                setError('Failed to load project');
                console.error(err);
            } finally {
                setLoading(false);
            }
        };

        fetchProject();
    }, [id]);

    const handleCreateTask = () => {
        setShowCreateTaskModal(true);
    };

    const handleCloseTaskModal = () => {
        setShowCreateTaskModal(false);
    };

    const handleEditProject = () => {
        setShowEditProjectModal(true);
    };

    const handleCloseEditModal = () => {
        setShowEditProjectModal(false);
    };

    const handleProjectUpdated = (updatedProject: Project) => {
        if (project) {
            // Update the component project with new data
            const ownerUser = users.find(u => u.id === updatedProject.owner_id);
            const updatedComponentProject: ComponentProject = {
                ...project,
                name: updatedProject.name,
                description: updatedProject.description || '',
                owner: ownerUser ? `${ownerUser.full_name} (${ownerUser.role})` : `User ${updatedProject.owner_id}`,
                owner_id: updatedProject.owner_id,
                status: updatedProject.status || 'Active',
                originalProject: updatedProject
            };
            setProject(updatedComponentProject);
        }
        setShowEditProjectModal(false);
    };

    const handleProjectDeleted = () => {
        // Navigate back to projects list after deletion
        window.history.back();
    };

    const handleTaskCreated = (newTask: Task) => {
        if (project) {
            // Add the new task to the project's task list
            const componentTask: ComponentTask = {
                id: newTask.id,
                title: newTask.title,
                description: newTask.description || '',
                status: newTask.status,
                assignee_id: newTask.assignee_id,
                assignee_name: undefined // Will be resolved when project is refreshed
            };

            setProject(prev => prev ? {
                ...prev,
                tasks: [...prev.tasks, componentTask]
            } : null);
        }
        setShowCreateTaskModal(false);
    };

    if (!id) {
        return <Navigate to="/projects" replace />;
    }

    if (loading) {
        return <div>Loading project...</div>;
    }

    if (error || !project) {
        return (
            <div className="error">
                <h2>Project not found</h2>
                <p>{error || 'The requested project could not be found.'}</p>
                <button onClick={() => window.history.back()}>Go Back</button>
            </div>
        );
    }    return (
        <>
            <ProjectDetails
                project={project}
                onCreateTask={handleCreateTask}
                onEditProject={handleEditProject}
            />

            {showCreateTaskModal && id && (
                <TaskCreateModal
                    projectId={parseInt(id)}
                    isOpen={showCreateTaskModal}
                    onClose={handleCloseTaskModal}
                    onTaskCreated={handleTaskCreated}
                />
            )}

            {showEditProjectModal && project && (
                <ProjectEditModal
                    project={project.originalProject}
                    isOpen={showEditProjectModal}
                    onClose={handleCloseEditModal}
                    onUpdate={handleProjectUpdated}
                    onDelete={handleProjectDeleted}
                />
            )}
        </>
    );
};
