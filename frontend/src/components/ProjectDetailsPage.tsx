import React, { useState, useEffect } from 'react';
import { useParams, Navigate } from 'react-router-dom';
import { ProjectDetails } from './ProjectDetails';
import { getProject, getProjectTasks } from '../lib/project';
import { getUsers } from '../lib/user';
import type { Task } from '../lib/task';
import type { User } from '../lib/user';

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
    startDate: string;
    endDate?: string;
    tasks: ComponentTask[];
};

export const ProjectDetailsPage: React.FC = () => {
    const { id } = useParams<{ id: string }>();
    const [project, setProject] = useState<ComponentProject | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);    useEffect(() => {
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
                const componentProject: ComponentProject = {
                    id: apiProject.id,
                    name: apiProject.name,
                    description: apiProject.description || '',
                    owner: `User ${apiProject.owner_id}`, // TODO: Fetch actual user name
                    startDate: new Date(apiProject.created_at).toISOString().split('T')[0],
                    endDate: undefined,
                    tasks: componentTasks
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
    }

    return <ProjectDetails project={project} />;
};
