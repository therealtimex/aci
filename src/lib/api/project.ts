import { Project } from "@/lib/types/project";

export async function getProjects(accessToken: string): Promise<Project[]> {
  const response = await fetch(
    `${process.env.NEXT_PUBLIC_API_URL}/v1/projects/`,
    {
      method: "GET",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      credentials: "include",
    },
  );

  if (!response.ok) {
    console.log(response);
    throw new Error(
      `Failed to fetch projects: ${response.status} ${response.statusText}`,
    );
  }
  const retrievedProjects: Project[] = await response.json();
  return retrievedProjects;
}
