import type {
  ApiResponse,
  LoginCredentials,
  User,
  Mailbox,
  Domain,
  LlmAnalysis,
  LlmAnalysisRequest,
  LlmStats,
  LlmHealth,
  LlmConfig,
  LlmUserPreferences,
  DashboardStats,
  QueueItem,
  QuarantineItem,
} from '$lib/types';

/**
 * API Client Configuration
 */
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/json_api.php';
const API_KEY = import.meta.env.VITE_API_KEY || '';

/**
 * HTTP Client with automatic error handling and retries
 */
class ApiClient {
  private baseUrl: string;
  private apiKey: string;
  private sessionId: string | null = null;

  constructor(baseUrl: string = API_BASE_URL, apiKey: string = API_KEY) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;

    // Try to restore session from localStorage
    if (typeof window !== 'undefined') {
      this.sessionId = localStorage.getItem('session_id');
    }
  }

  /**
   * Set session ID for authenticated requests
   */
  setSession(sessionId: string | null) {
    this.sessionId = sessionId;
    if (typeof window !== 'undefined') {
      if (sessionId) {
        localStorage.setItem('session_id', sessionId);
      } else {
        localStorage.removeItem('session_id');
      }
    }
  }

  /**
   * Build query URL
   */
  private buildUrl(query: string): string {
    return `${this.baseUrl}?query=${encodeURIComponent(query)}`;
  }

  /**
   * Make HTTP request with retry logic
   */
  private async request<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    query: string,
    body?: any,
    retries = 3
  ): Promise<ApiResponse<T>> {
    const url = this.buildUrl(query);
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.apiKey) {
      headers['X-API-Key'] = this.apiKey;
    }

    const options: RequestInit = {
      method,
      headers,
      credentials: 'include', // Include cookies for session management
    };

    if (body && (method === 'POST' || method === 'PUT')) {
      options.body = JSON.stringify(body);
    }

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        const response = await fetch(url, options);

        if (!response.ok) {
          if (response.status === 401) {
            // Unauthorized - clear session
            this.setSession(null);
            throw new Error('Unauthorized - please login again');
          }

          if (response.status === 403) {
            throw new Error('Forbidden - insufficient permissions');
          }

          if (response.status >= 500 && attempt < retries) {
            // Server error - retry with exponential backoff
            await this.sleep(Math.pow(2, attempt) * 1000);
            continue;
          }
        }

        const data: ApiResponse<T> = await response.json();

        // Check if response indicates an error
        if (data.type === 'danger') {
          const errorMsg = Array.isArray(data.msg) ? data.msg.join(', ') : data.msg;
          throw new Error(errorMsg);
        }

        return data;
      } catch (error) {
        if (attempt === retries) {
          throw error;
        }
        // Network error - retry with exponential backoff
        await this.sleep(Math.pow(2, attempt) * 1000);
      }
    }

    throw new Error('Maximum retries exceeded');
  }

  /**
   * Sleep utility for retries
   */
  private sleep(ms: number): Promise<void> {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  // ===== Authentication API =====

  async login(credentials: LoginCredentials): Promise<User> {
    const response = await this.request<User>('POST', 'add/user/login', credentials);
    if (response.data) {
      // Extract session ID from cookies or response
      const sessionId = response.data.username; // Adjust based on actual API
      this.setSession(sessionId);
    }
    return response.data!;
  }

  async logout(): Promise<void> {
    await this.request('POST', 'add/user/logout');
    this.setSession(null);
  }

  async getAuthStatus(): Promise<User | null> {
    try {
      const response = await this.request<User>('GET', 'get/user/auth');
      return response.data || null;
    } catch {
      return null;
    }
  }

  // ===== Mailbox API =====

  async getMailboxes(): Promise<Mailbox[]> {
    const response = await this.request<Mailbox[]>('GET', 'get/mailbox/all');
    return response.data || [];
  }

  async getMailbox(mailbox: string): Promise<Mailbox> {
    const response = await this.request<Mailbox>('GET', `get/mailbox/mailbox_details/${mailbox}`);
    return response.data!;
  }

  async createMailbox(data: Partial<Mailbox>): Promise<ApiResponse> {
    return await this.request('POST', 'add/mailbox', data);
  }

  async updateMailbox(mailbox: string, data: Partial<Mailbox>): Promise<ApiResponse> {
    return await this.request('PUT', 'edit/mailbox/mailbox', { ...data, username: mailbox });
  }

  async deleteMailbox(mailbox: string): Promise<ApiResponse> {
    return await this.request('DELETE', `delete/mailbox/${mailbox}`);
  }

  // ===== Domain API =====

  async getDomains(): Promise<Domain[]> {
    const response = await this.request<Domain[]>('GET', 'get/domain/all');
    return response.data || [];
  }

  async getDomain(domain: string): Promise<Domain> {
    const response = await this.request<Domain>('GET', `get/domain/${domain}`);
    return response.data!;
  }

  async createDomain(data: Partial<Domain>): Promise<ApiResponse> {
    return await this.request('POST', 'add/domain', data);
  }

  async updateDomain(domain: string, data: Partial<Domain>): Promise<ApiResponse> {
    return await this.request('PUT', 'edit/domain', { ...data, domain });
  }

  async deleteDomain(domain: string): Promise<ApiResponse> {
    return await this.request('DELETE', `delete/domain/${domain}`);
  }

  // ===== LLM API =====

  async analyzEmail(request: LlmAnalysisRequest): Promise<LlmAnalysis> {
    const response = await this.request<LlmAnalysis>('POST', 'add/llm/analyze', request);
    return response.data!;
  }

  async getAnalysis(emailId: string, mailbox: string): Promise<LlmAnalysis | null> {
    try {
      const response = await this.request<LlmAnalysis>(
        'GET',
        `get/llm/analysis?email_id=${emailId}&mailbox=${mailbox}`
      );
      return response.data || null;
    } catch {
      return null;
    }
  }

  async getLlmStats(): Promise<LlmStats> {
    const response = await this.request<LlmStats>('GET', 'get/llm/stats');
    return response.data!;
  }

  async getLlmHealth(): Promise<LlmHealth> {
    const response = await this.request<LlmHealth>('GET', 'get/llm/health');
    return response.data!;
  }

  async getLlmConfig(): Promise<LlmConfig> {
    const response = await this.request<LlmConfig>('GET', 'get/llm/config');
    return response.data!;
  }

  async updateLlmConfig(config: Partial<LlmConfig>): Promise<ApiResponse> {
    return await this.request('POST', 'edit/llm/config', config);
  }

  async getUserPreferences(username: string): Promise<LlmUserPreferences> {
    const response = await this.request<LlmUserPreferences>(
      'GET',
      `get/llm/preferences/${username}`
    );
    return response.data!;
  }

  async updateUserPreferences(preferences: Partial<LlmUserPreferences>): Promise<ApiResponse> {
    return await this.request('POST', 'edit/llm/preferences', preferences);
  }

  // ===== Dashboard API =====

  async getDashboardStats(): Promise<DashboardStats> {
    const response = await this.request<DashboardStats>('GET', 'get/stats/dashboard');
    // Fallback implementation - construct from multiple API calls if needed
    return response.data || this.constructDashboardStats();
  }

  private async constructDashboardStats(): Promise<DashboardStats> {
    // If the backend doesn't have a dedicated dashboard endpoint,
    // we can construct it from multiple API calls
    const [mailboxes, domains, llmStats] = await Promise.all([
      this.getMailboxes(),
      this.getDomains(),
      this.getLlmStats().catch(() => null),
    ]);

    return {
      mailboxes: {
        total: mailboxes.length,
        active: mailboxes.filter((m) => m.active).length,
        quota_total: mailboxes.reduce((sum, m) => sum + m.quota, 0),
        quota_used: mailboxes.reduce((sum, m) => sum + m.quota_used, 0),
      },
      domains: {
        total: domains.length,
        active: domains.filter((d) => d.active).length,
      },
      emails_24h: {
        received: 0, // Would need to query logs
        sent: 0,
        rejected: 0,
      },
      spam_stats: {
        total: 0,
        quarantined: 0,
        rejected: 0,
      },
      system: {
        cpu: 0,
        memory: 0,
        disk: 0,
      },
      llm: llmStats || undefined,
    };
  }

  // ===== Queue API =====

  async getQueue(): Promise<QueueItem[]> {
    const response = await this.request<QueueItem[]>('GET', 'get/mailq/all');
    return response.data || [];
  }

  async flushQueue(queueId: string): Promise<ApiResponse> {
    return await this.request('POST', 'edit/mailq/flush', { qid: queueId });
  }

  async deleteQueueItem(queueId: string): Promise<ApiResponse> {
    return await this.request('DELETE', `delete/mailq/${queueId}`);
  }

  // ===== Quarantine API =====

  async getQuarantine(): Promise<QuarantineItem[]> {
    const response = await this.request<QuarantineItem[]>('GET', 'get/quarantine/all');
    return response.data || [];
  }

  async releaseQuarantineItem(id: string): Promise<ApiResponse> {
    return await this.request('POST', 'edit/quarantine/release', { id });
  }

  async deleteQuarantineItem(id: string): Promise<ApiResponse> {
    return await this.request('DELETE', `delete/quarantine/${id}`);
  }
}

// Export singleton instance
export const api = new ApiClient();

// Export class for testing or multiple instances
export { ApiClient };
