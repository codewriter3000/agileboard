import api from './api';

// Task interfaces
export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  project_id: number;
  assignee_id?: number;
  sprint_id?: number;
  created_at: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status: TaskStatus;
  project_id: number;
  assignee_id?: number;
  sprint_id?: number;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  assignee_id?: number;
  project_id?: number;
  sprint_id?: number;
}

export type TaskStatus = 'Backlog' | 'In Progress' | 'Review' | 'Done';

// Task API functions
export async function getTasks(): Promise<Task[]> {
  const response = await api.get('/tasks/');
  return response.data;
}

export async function getTask(id: number): Promise<Task> {
  const response = await api.get(`/tasks/${id}`);
  return response.data;
}

export async function createTask(data: TaskCreate): Promise<Task> {
  const response = await api.post('/tasks/', data);
  return response.data;
}

export async function updateTask(id: number, data: TaskUpdate): Promise<Task> {
  const response = await api.put(`/tasks/${id}`, data);
  return response.data;
}

export async function deleteTask(id: number): Promise<void> {
  await api.delete(`/tasks/${id}`);
}

// Task-specific utility functions
export async function assignTask(taskId: number, assigneeId: number): Promise<Task> {
  const response = await api.patch(`/tasks/${taskId}/assign`, { assignee_id: assigneeId });
  return response.data;
}

export async function updateTaskStatus(taskId: number, status: TaskStatus): Promise<Task> {
  const response = await api.patch(`/tasks/${taskId}/status`, { status });
  return response.data;
}
