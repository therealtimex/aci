export interface AppFunction {
  id: string;
  app_name: string;
  name: string;
  description: string;
  tags: string[];
  parameters: object;
}

export interface FunctionExecute {
  function_input: object;
  linked_account_owner_id: string;
}

export interface FunctionExecutionResult {
  success: boolean;
  data: object;
  error?: string;
}
