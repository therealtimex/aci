"use client";

import { useProject } from "@/components/context/project";
import { Skeleton } from "@/components/ui/skeleton";

export default function HomePage() {
  const { project } = useProject();

  return (
    <div className="m-4">
      <h1 className="text-2xl font-bold">Home</h1>
      {project ? (
        <p className="text-sm text-muted-foreground">
          Welcome to the home page of {project?.name} project.
        </p>
      ) : (
        <Skeleton className="h-4 w-80" />
      )}
    </div>
  );
}
