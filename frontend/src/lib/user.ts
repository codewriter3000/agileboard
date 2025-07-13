import api from './api';

export interface CreateUserPayload {
    full_name: string;
    email: string;
    password: string;
    role?: UserRole;
}

export interface User {
    id: number;
    full_name: string;
    email: string;
    role: UserRole;
}

export type UserRole = 'Admin' | 'ScrumMaster' | 'Developer';

// User API functions
export async function getUsers(): Promise<User[]> {
    const response = await api.get('/users/');
    return response.data;
}

export async function getUser(id: number): Promise<User> {
    const response = await api.get(`/users/${id}`);
    return response.data;
}

export async function createUser(payload: CreateUserPayload): Promise<User> {
    const response = await api.post('/users/', payload);
    return response.data;
}

export async function updateUser(id: number, payload: Partial<CreateUserPayload>): Promise<User> {
    const response = await api.put(`/users/${id}`, payload);
    return response.data;
}

export async function deleteUser(id: number): Promise<void> {
    await api.delete(`/users/${id}`);
}

// Authentication functions (placeholder for future implementation)
export async function login(email: string, password: string): Promise<{ token: string; user: User }> {
    const response = await api.post('/auth/login', { email, password });
    return response.data;
}

export async function logout(): Promise<void> {
    await api.post('/auth/logout');
    localStorage.removeItem('token');
}