/**
 * API Service
 * ===========
 * Centralized API client with authentication handling.
 */

import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import type {
  User,
  LoginCredentials,
  RegisterData,
  TokenResponse,
  DesignGenerateRequest,
  DesignGenerateResponse,
  PlotValidationResponse,
  SoilAnalysisResponse,
  Project,
  ProjectCreate,
  Point,
  SoilType,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

/**
 * API Client class with authentication handling.
 */
class ApiClient {
  private client: AxiosInstance;
  private refreshTokenPromise: Promise<string> | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getAccessToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle token refresh
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest = error.config as AxiosRequestConfig & { _retry?: boolean };

        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshAccessToken();
            originalRequest.headers = {
              ...originalRequest.headers,
              Authorization: `Bearer ${newToken}`,
            };
            return this.client(originalRequest);
          } catch (refreshError) {
            this.logout();
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // ==========================================
  // Token Management
  // ==========================================

  private getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  private getRefreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  private setTokens(tokens: TokenResponse): void {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
  }

  private async refreshAccessToken(): Promise<string> {
    if (this.refreshTokenPromise) {
      return this.refreshTokenPromise;
    }

    this.refreshTokenPromise = (async () => {
      const refreshToken = this.getRefreshToken();
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await axios.post<TokenResponse>(
        `${API_BASE_URL}/auth/refresh`,
        { refresh_token: refreshToken }
      );

      this.setTokens(response.data);
      return response.data.access_token;
    })();

    try {
      const token = await this.refreshTokenPromise;
      return token;
    } finally {
      this.refreshTokenPromise = null;
    }
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    window.location.href = '/login';
  }

  // ==========================================
  // Authentication API
  // ==========================================

  async login(credentials: LoginCredentials): Promise<{ user: User; tokens: TokenResponse }> {
    const response = await this.client.post<TokenResponse>('/auth/login', credentials);
    this.setTokens(response.data);

    // Get user info
    const userResponse = await this.client.get<User>('/auth/me');
    localStorage.setItem('user', JSON.stringify(userResponse.data));

    return { user: userResponse.data, tokens: response.data };
  }

  async register(data: RegisterData): Promise<User> {
    const response = await this.client.post<User>('/auth/register', data);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  // ==========================================
  // Design API
  // ==========================================

  async validatePlot(coordinates: Point[]): Promise<PlotValidationResponse> {
    const response = await this.client.post<PlotValidationResponse>(
      '/design/validate-plot',
      { coordinates }
    );
    return response.data;
  }

  async analyzeSoil(
    soilType: SoilType,
    totalLoad: number,
    foundationArea: number,
    buildingHeight: number,
    numStories: number
  ): Promise<SoilAnalysisResponse> {
    const response = await this.client.post<SoilAnalysisResponse>(
      '/design/analyze-soil',
      {
        soil_type: soilType,
        total_load: totalLoad,
        foundation_area: foundationArea,
        building_height: buildingHeight,
        num_stories: numStories,
      }
    );
    return response.data;
  }

  async generateDesign(request: DesignGenerateRequest): Promise<DesignGenerateResponse> {
    const response = await this.client.post<DesignGenerateResponse>(
      '/design/generate',
      request
    );
    return response.data;
  }

  // ==========================================
  // Project API
  // ==========================================

  async createProject(data: ProjectCreate): Promise<Project> {
    const response = await this.client.post<Project>('/design/projects', data);
    return response.data;
  }

  async getProjects(): Promise<Project[]> {
    const response = await this.client.get<Project[]>('/design/projects');
    return response.data;
  }

  async getProject(id: string): Promise<Project> {
    const response = await this.client.get<Project>(`/design/projects/${id}`);
    return response.data;
  }

  // ==========================================
  // Export API
  // ==========================================

  async exportDesign(
    designId: string,
    format: 'svg' | 'gltf' | 'pdf' | 'json'
  ): Promise<{ download_url: string }> {
    const response = await this.client.post<{ download_url: string }>(
      '/design/export',
      { design_id: designId, format }
    );
    return response.data;
  }
}

// Export singleton instance
export const api = new ApiClient();

// Export class for testing
export { ApiClient };