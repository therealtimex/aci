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

export interface APIKey {
    id: string;
    key: string;
    agent_id: string;
    status: string;
    created_at: string;
    updated_at: string;
}
