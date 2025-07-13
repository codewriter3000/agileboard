import api from './api';
import type { TaskCreate } from './task';

// Project interfaces
export interface Project {
  id: number;
  name: string;
  description?: string;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface ProjectCreate {
  name: string;
  description?: string;
  owner_id: number;
}

// Project API functions
export async function getProjects(): Promise<Project[]> {
  const response = await api.get('/projects/');
  return response.data;
}

export async function getProject(id: number): Promise<Project> {
  const response = await api.get(`/projects/${id}`);
  return response.data;
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const response = await api.post('/projects/', data);
  return response.data;
}

export async function updateProject(id: number, data: ProjectCreate): Promise<Project> {
  const response = await api.put(`/projects/${id}`, data);
  return response.data;
}

export async function deleteProject(id: number): Promise<void> {
  await api.delete(`/projects/${id}`);
}

// Additional project-specific endpoints
export async function getProjectTasks(projectId: number) {
  const response = await api.get(`/projects/${projectId}/tasks/`);
  return response.data;
}

export async function createProjectTask(projectId: number, data: TaskCreate) {
  const response = await api.post(`/projects/${projectId}/tasks/`, data);
  return response.data;
}
