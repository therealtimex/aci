import { Project } from "@/lib/types/project";

export function getApiKey(project: Project): string {
  if (
    !project ||
    !project.agents ||
    project.agents.length === 0 ||
    !project.agents[0].api_keys ||
    project.agents[0].api_keys.length === 0
  ) {
    throw new Error(
      `No API key available in project: ${project.id} ${project.name}`,
    );
  }
  return project.agents[0].api_keys[0].key;
}
