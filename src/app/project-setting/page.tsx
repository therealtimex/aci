"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// import { Switch } from "@/components/ui/switch";
import { AgentForm } from "@/components/project/agent-form";
import { createAgent, deleteAgent } from "@/lib/api/agent";
import { useProject } from "@/components/context/project";
import { Separator } from "@/components/ui/separator";
import { IdDisplay } from "@/components/apps/id-display";
// import { RiTeamLine } from "react-icons/ri";
import { MdAdd } from "react-icons/md";
import { BsQuestionCircle } from "react-icons/bs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useCallback, useEffect, useState } from "react";
import { getApiKey } from "@/lib/api/util";
import { useUser } from "@/components/context/user";
import { getProjects } from "@/lib/api/project";
import { App } from "@/lib/types/app";
import { getAllApps } from "@/lib/api/app";
import { useAgentsTableColumns } from "@/components/project/useAgentsTableColumns";
import { EnhancedDataTable } from "@/components/ui-extensions/enhanced-data-table/data-table";
import { Agent } from "@/lib/types/project";
import { toast } from "sonner";

export default function ProjectSettingPage() {
  const { user } = useUser();
  const { project, setProject } = useProject();

  // const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);
  const [apps, setApps] = useState<App[]>([]);

  const loadAppConfigs = useCallback(async () => {
    if (!project) {
      console.warn("No active project");
      return;
    }
    const apiKey = getApiKey(project);

    // const appConfigs = await getAllAppConfigs(apiKey);
    // setAppConfigs(appConfigs);
    try {
      const apps = await getAllApps(apiKey);
      setApps(apps);
    } catch (error) {
      console.error("Error fetching apps:", error);
    }
  }, [project]);

  const loadProject = useCallback(async () => {
    if (!user) {
      return;
    }

    try {
      const retrievedProjects = await getProjects(user.accessToken);

      // TODO: there will be multiple projects in a future release
      setProject(retrievedProjects[0]);
    } catch (error) {
      console.error("Error fetching projects:", error);
    }
  }, [setProject, user]);

  useEffect(() => {
    loadAppConfigs();
  }, [project, loadAppConfigs]);

  const handleDeleteAgent = useCallback(
    async (agentId: string) => {
      if (!project || !user) {
        console.warn("No active project or user");
        return;
      }

      try {
        if (project.agents.length <= 1) {
          toast.error(
            "Failed to delete agent. You must keep at least one agent in the project.",
          );
          return;
        }

        await deleteAgent(project.id, agentId, user.accessToken);
        await loadProject();
      } catch (error) {
        console.error("Error deleting agent:", error);
      }
    },
    [project, user, loadProject],
  );

  const agentTableColumns = useAgentsTableColumns(
    project?.id || "",
    handleDeleteAgent,
    loadProject,
    loadProject,
  );

  if (!project) {
    return (
      <div className="flex justify-center items-center h-screen">
        Loading...
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="flex items-center justify-between m-4">
        <h1 className="text-2xl font-semibold">Project settings</h1>
        {/* <Button
          variant="outline"
          className="text-red-500 hover:text-red-600 hover:bg-red-50"
        >
          Delete project
        </Button> */}
      </div>
      <Separator />

      <div className="px-4 py-6 space-y-6">
        {/* Project Name Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <label className="font-semibold">Project Name</label>
            <p className="text-sm text-muted-foreground">
              Change the name of the project
            </p>
          </div>
          <div>
            <Input defaultValue={project.name} className="w-96" readOnly />
          </div>
        </div>

        <Separator />

        {/* Project ID Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <div className="flex items-center gap-2">
              <label className="font-semibold">Project ID</label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-pointer">
                    <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p className="text-xs">A project can have multiple agents.</p>
                </TooltipContent>
              </Tooltip>
            </div>
          </div>
          <div className="flex items-center px-2">
            <IdDisplay id={project.id} dim={false} />
          </div>
        </div>

        <Separator />

        {/* Team Section */}
        {/* <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <label className="font-semibold">Team</label>
            <p className="text-sm text-muted-foreground">
              Easily manage your team
            </p>
          </div>
          <div>
            <Button variant="outline">
              <RiTeamLine />
              Manage Members
            </Button>
          </div>
        </div>

        <Separator /> */}

        {/* Agent Section */}
        <div className="flex flex-row">
          <div className="flex flex-col items-left w-80">
            <div className="flex items-center gap-2">
              <label className="font-semibold">Agent</label>
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-pointer">
                    <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p className="text-xs">
                    Each agent has a unique API key that can be used to access a
                    different set of tools/apps configured for the project.
                  </p>
                </TooltipContent>
              </Tooltip>
            </div>
            <p className="text-sm text-muted-foreground">
              Add and manage agents
            </p>
          </div>
          <div className="flex items-center justify-between w-96">
            {/* <div className="flex items-center gap-2">
              <Switch checked={hasAgents} />
              <span className="text-sm">Enable</span>
            </div> */}
            <div className="flex items-center gap-2">
              <AgentForm
                title="Create Agent"
                validAppNames={apps.map((app) => app.name)}
                onSubmit={async (values) => {
                  if (!project) return;
                  try {
                    await createAgent(
                      project.id,
                      user!.accessToken,
                      values.name,
                      values.description,
                      // TODO: need to create a UI for specifying allowed apps
                      values.allowed_apps,
                      values.custom_instructions,
                    );
                    await loadProject();
                  } catch (error) {
                    console.error("Error creating agent:", error);
                  }
                }}
              >
                <Button variant="outline">
                  <MdAdd />
                  Create Agent
                  <Tooltip>
                    <TooltipTrigger asChild>
                      <span className="cursor-pointer">
                        <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                      </span>
                    </TooltipTrigger>
                    <TooltipContent side="top">
                      <p className="text-xs">
                        Create a new agent API key to access applications
                        configured for this project.
                      </p>
                    </TooltipContent>
                  </Tooltip>
                </Button>
              </AgentForm>
            </div>
          </div>
        </div>

        {project.agents && project.agents.length > 0 && (
          <EnhancedDataTable
            columns={agentTableColumns}
            data={project.agents as Agent[]}
            defaultSorting={[{ id: "name", desc: true }]}
            searchPlaceholder="Search agents..."
          />
        )}
      </div>
    </div>
  );
}
