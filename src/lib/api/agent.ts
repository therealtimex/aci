import { Agent } from "@/lib/types/project";

export async function createAgent(
  projectId: string,
  accessToken: string,
  name: string,
  description: string,
  excluded_apps: string[] = [],
  excluded_functions: string[] = [],
  custom_instructions: Record<string, string> = {},
): Promise<Agent> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/v1/projects/${projectId}/agents`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify({
        name,
        description,
        excluded_apps,
        excluded_functions,
        custom_instructions,
      }),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to create agent. Status: ${response.status}`);
  }
  return response.json();
}

export async function updateAgent(
  projectId: string,
  agentId: string,
  accessToken: string,
  name?: string,
  description?: string,
  excluded_apps?: string[],
  excluded_functions?: string[],
  custom_instructions?: Record<string, string>,
): Promise<Agent> {
  const body = Object.fromEntries(
    Object.entries({
      name,
      description,
      excluded_apps,
      excluded_functions,
      custom_instructions,
    })
      // eslint-disable-next-line @typescript-eslint/no-unused-vars
      .filter(([_, value]) => value !== undefined),
  );

  // TODO: custom_instructions bug

  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/v1/projects/${projectId}/agents/${agentId}`,
    {
      method: "PATCH",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${accessToken}`,
      },
      body: JSON.stringify(body),
    },
  );

  if (!response.ok) {
    throw new Error(`Failed to update agent. Status: ${response.status}`);
  }
  return response.json();
}
