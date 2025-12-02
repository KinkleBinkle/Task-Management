const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

class ApiClient {
  private baseURL: string;
  private token: string | null = null;

  constructor() {
    this.baseURL = API_BASE_URL;
    this.token = localStorage.getItem('access_token');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('access_token', token);
  }

  clearToken() {
    this.token = null;
    localStorage.removeItem('access_token');
  }

  private getHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }

    return headers;
  }

  async request<T>(
    endpoint: string,
    method: 'GET' | 'POST' | 'PUT' | 'DELETE' = 'GET',
    body?: Record<string, any>
  ): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;
    const options: RequestInit = {
      method,
      headers: this.getHeaders(),
    };

    if (body) {
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);

    if (response.status === 204) {
      return null as T;
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  // Auth endpoints
  async register(username: string, name: string, password: string) {
    return this.request('/users/register', 'POST', { username, name, password });
  }

  async login(username: string, password: string) {
    return this.request('/users/login', 'POST', { username, password });
  }

  async getCurrentUser() {
    return this.request('/users/me', 'POST');
  }

  async getUser(userId: number) {
    return this.request(`/users/${userId}`);
  }

  async getAllUsers() {
    return this.request('/users/');
  }

  async updateUser(userId: number, data: Record<string, any>) {
    return this.request(`/users/${userId}`, 'PUT', data);
  }

  async deleteUser(userId: number) {
    return this.request(`/users/${userId}`, 'DELETE');
  }

  // Project endpoints
  async createProject(name: string, description?: string) {
    return this.request('/projects/', 'POST', { name, description });
  }

  async listProjects(userId?: number) {
    const endpoint = userId ? `/projects/?user_id=${userId}` : '/projects/';
    return this.request(endpoint);
  }

  async getProject(projectId: number) {
    return this.request(`/projects/${projectId}`);
  }

  async updateProject(projectId: number, data: Record<string, any>) {
    return this.request(`/projects/${projectId}`, 'PUT', data);
  }

  async deleteProject(projectId: number) {
    return this.request(`/projects/${projectId}`, 'DELETE');
  }

  async addProjectMember(projectId: number, userId: number, role: string = 'member') {
    return this.request(`/projects/${projectId}/members/`, 'POST', { user_id: userId, role });
  }

  async removeProjectMember(projectId: number, memberId: number) {
    return this.request(`/projects/${projectId}/members/${memberId}`, 'DELETE');
  }

  async updateProjectMember(projectId: number, memberId: number, role: string) {
    return this.request(`/projects/${projectId}/members/${memberId}`, 'PUT', { role });
  }

  // Task endpoints
  async createTask(projectId: number, title: string, description?: string, assigneeId?: number) {
    return this.request(`/projects/${projectId}/tasks/`, 'POST', {
      title,
      description,
      assignee_id: assigneeId,
    });
  }

  async getProjectTasks(projectId: number) {
    return this.request(`/projects/${projectId}/tasks/`);
  }

  async updateTask(projectId: number, taskId: number, data: Record<string, any>) {
    return this.request(`/projects/${projectId}/tasks/${taskId}`, 'PUT', data);
  }

  async deleteTask(projectId: number, taskId: number) {
    return this.request(`/projects/${projectId}/tasks/${taskId}`, 'DELETE');
  }
}

export default new ApiClient();
