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
