export interface AppFunction {
    id: string;
    app_id: string;
    name: string;
    description: string;
    tags: string[];
    parameters: Record<string, unknown>;
}
