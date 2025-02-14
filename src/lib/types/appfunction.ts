export interface AppFunction {
  id: string;
  app_name: string;
  name: string;
  description: string;
  tags: string[];
  parameters: Record<string, unknown>;
}
