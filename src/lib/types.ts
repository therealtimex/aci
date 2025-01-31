export interface App {
    id: string;
    name: string;
    icon: string;
    description: string;
    categories: string[];
    tags: string[];
}

export interface AppFunction {
    id: string;
    name: string;
    functionId: string;
    description: string;
    categories: string[];
    tags: string[];
}

export interface AppConfig {
    id: string;
    project_id: string;
    app_id: string;
    security_scheme: string;
    security_scheme_overrides: Record<string, unknown>;
    enabled: boolean;
    all_functions_enabled: boolean;
    enabled_functions: string[];
}

export interface APIKey {
  id: string;
  key: string;
  agent_id: string;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface Agent {
  id: string;
  project_id: string;
  name: string;
  description: string;
  excluded_apps: string[];
  excluded_functions: string[];
  created_at: string;
  updated_at: string;
  api_keys: APIKey[];
}

export interface Project {
  id: string;
  owner_id: string;
  name: string;
  visibility_access: string;
  daily_quota_used: number;
  daily_quota_reset_at: string;
  total_quota_used: number;
  created_at: string;
  updated_at: string;
  agents: Agent[];
}
