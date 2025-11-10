// API Response Types
export interface ApiResponse<T = any> {
  type: 'success' | 'danger' | 'warning' | 'info';
  msg: string | string[];
  log?: [string, string];
  data?: T;
}

// Authentication Types
export interface User {
  username: string;
  role: 'admin' | 'domainadmin' | 'user';
  email?: string;
  created?: string;
  modified?: string;
  active?: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  sessionId?: string;
}

// Mailbox Types
export interface Mailbox {
  username: string;
  domain: string;
  name: string;
  quota: number;
  quota_used: number;
  active: boolean;
  created: string;
  modified: string;
  spam_enabled: boolean;
  imap_enabled: boolean;
  pop3_enabled: boolean;
  smtp_enabled: boolean;
}

export interface MailboxStats {
  total: number;
  active: number;
  quota_total: number;
  quota_used: number;
}

// Domain Types
export interface Domain {
  domain: string;
  description: string;
  aliases: number;
  mailboxes: number;
  maxquota: number;
  quota: number;
  active: boolean;
  created: string;
  modified: string;
}

// LLM Analysis Types
export interface LlmAnalysis {
  id: number;
  mailbox: string;
  email_id: string;
  summary: string | null;
  categories: string[];
  priority_score: number;
  is_phishing: boolean;
  phishing_score: number;
  sensitive_data: boolean;
  auto_reply_suggestion: string | null;
  processing_time: number;
  analyzed_at: string;
  created: string;
  modified: string;
}

export interface LlmAnalysisRequest {
  email_id: string;
  mailbox: string;
  force?: boolean;
}

export interface LlmStats {
  total_analyzed: number;
  phishing_detected: number;
  avg_processing_time: number;
  recent_analyses: LlmAnalysis[];
  analyses_by_category: Record<string, number>;
  analyses_by_priority: Record<string, number>;
}

export interface LlmHealth {
  status: 'healthy' | 'degraded' | 'error';
  ollama: 'ok' | 'error';
  mysql: 'ok' | 'error';
  redis: 'ok' | 'error';
  model: string;
  uptime?: number;
  version?: string;
}

export interface LlmConfig {
  enabled: boolean;
  model: string;
  host: string;
  timeout: number;
  interval: number;
  batch_size: number;
  max_retries: number;
  auto_analysis: boolean;
  auto_categorize: boolean;
  phishing_detection: boolean;
  sensitive_data_detection: boolean;
  auto_reply_suggestions: boolean;
  max_email_size: number;
  cache_ttl: number;
  concurrent_jobs: number;
  phishing_threshold: number;
  notify_admins: boolean;
  quarantine_high_risk: boolean;
}

export interface LlmUserPreferences {
  username: string;
  auto_analysis: boolean;
  auto_categorize: boolean;
  phishing_alerts: boolean;
  summary_enabled: boolean;
}

// Email Types
export interface Email {
  id: string;
  mailbox: string;
  subject: string;
  from: string;
  to: string[];
  cc?: string[];
  date: string;
  size: number;
  flags: string[];
  attachments?: number;
  has_attachments: boolean;
  folder: string;
  // LLM enriched data
  llm_analysis?: LlmAnalysis;
}

// Queue Types
export interface QueueItem {
  queue_id: string;
  arrival_time: string;
  message_size: number;
  sender: string;
  recipients: string[];
  queue_name: string;
  reason?: string;
}

// Quarantine Types
export interface QuarantineItem {
  id: string;
  qid: string;
  subject: string;
  sender: string;
  rcpt: string;
  score: number;
  created: string;
  action?: 'spam' | 'virus' | 'banned';
  symbols?: string[];
}

// Dashboard Stats Types
export interface DashboardStats {
  mailboxes: MailboxStats;
  domains: {
    total: number;
    active: number;
  };
  emails_24h: {
    received: number;
    sent: number;
    rejected: number;
  };
  spam_stats: {
    total: number;
    quarantined: number;
    rejected: number;
  };
  system: {
    cpu: number;
    memory: number;
    disk: number;
  };
  llm?: LlmStats;
}

// Chart Data Types
export interface ChartDataPoint {
  label: string;
  value: number;
  color?: string;
}

export interface TimeSeriesData {
  timestamp: string;
  value: number;
  label?: string;
}

// Notification Types
export type NotificationType = 'success' | 'error' | 'warning' | 'info';

export interface Notification {
  id: string;
  type: NotificationType;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  action?: {
    label: string;
    href: string;
  };
}

// Filter and Pagination Types
export interface PaginationParams {
  page: number;
  limit: number;
  sort?: string;
  order?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  data: T[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

// Form Types
export interface FormErrors {
  [key: string]: string | undefined;
}

// Theme Types
export type Theme = 'light' | 'dark' | 'system';

// WebSocket Message Types
export interface WebSocketMessage {
  type: 'email' | 'notification' | 'llm_analysis' | 'system';
  action: 'new' | 'update' | 'delete';
  data: any;
  timestamp: string;
}
