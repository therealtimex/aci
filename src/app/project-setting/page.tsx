"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
// import { Switch } from "@/components/ui/switch";
import { AgentForm } from "@/components/project/agent-form";
import { createAgent, updateAgent } from "@/lib/api/agent";
import { useProject } from "@/components/context/project";
import { Separator } from "@/components/ui/separator";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { IdDisplay } from "@/components/apps/id-display";
// import { RiTeamLine } from "react-icons/ri";
import { MdAdd } from "react-icons/md";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { useCallback, useEffect, useState } from "react";
import { getApiKey } from "@/lib/api/util";
import { useUser } from "@/components/context/user";
import { getProjects } from "@/lib/api/project";
import ReactJson from "react-json-view";
import { App } from "@/lib/types/app";
import { getAllApps } from "@/lib/api/app";

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

  if (!project) {
    return <div>Loading...</div>;
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
            <label className="font-semibold">Project ID</label>
            <p className="text-sm text-muted-foreground">
              Change the project ID
            </p>
          </div>
          <div>
            <Input
              defaultValue={project.id}
              className="w-96 font-mono"
              readOnly
            />
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
            <label className="font-semibold">Agent</label>
            <p className="text-sm text-muted-foreground">
              Add and manage agents
            </p>
          </div>
          <div className="flex items-center justify-between w-96">
            {/* <div className="flex items-center gap-2">
              <Switch checked={hasAgents} />
              <span className="text-sm">Enable</span>
            </div> */}
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
                    values.excluded_apps,
                    values.excluded_functions,
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
              </Button>
            </AgentForm>
          </div>
        </div>

        {project.agents && project.agents.length > 0 && (
          <div className="border rounded-lg">
            <Table>
              <TableHeader className="bg-gray-50">
                <TableRow>
                  <TableHead>AGENT NAME & ID</TableHead>
                  <TableHead>DESCRIPTION</TableHead>
                  <TableHead>API KEY</TableHead>
                  <TableHead>CREATION DATE AND TIME</TableHead>
                  {/* <TableHead>ENABLED APPS</TableHead> */}
                  <TableHead>
                    <Tooltip>
                      <TooltipTrigger className="text-left">
                        INSTRUCTION FILTER
                      </TooltipTrigger>
                      <TooltipContent>
                        <p>
                          Specific instructions for each app to modulate its use
                        </p>
                      </TooltipContent>
                    </Tooltip>
                  </TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {project.agents.map((agent) => {
                  return (
                    <TableRow key={agent.id}>
                      <TableCell>
                        <div>
                          <div className="font-medium">{agent.name}</div>
                          <div className="text-sm text-muted-foreground font-mono w-24">
                            <IdDisplay id={agent.id} />
                          </div>
                        </div>
                      </TableCell>
                      <TableCell>{agent.description}</TableCell>
                      <TableCell className="font-mono">
                        <div className="w-24">
                          <IdDisplay id={agent.api_keys[0].key} />
                        </div>
                      </TableCell>
                      <TableCell>{agent.created_at}</TableCell>
                      {/* <TableCell>
                        <div className="flex flex-wrap gap-2">
                          {appConfigs.map((config) => (
                            <span
                              key={config.app_name}
                              className="rounded-md bg-gray-100 px-2 py-0.5 text-xs font-medium text-gray-600 border border-gray-200"
                            >
                              {config.app_name}
                            </span>
                          ))}
                        </div>
                      </TableCell> */}
                      <TableCell className="w-[30%]">
                        <ReactJson
                          style={{ wordBreak: "break-all" }}
                          name={false}
                          src={agent.custom_instructions}
                          displayDataTypes={false}
                          // enableClipboard={false}
                        />
                      </TableCell>
                      <TableCell>
                        <AgentForm
                          title="Edit Agent"
                          validAppNames={apps.map((app) => app.name)}
                          initialValues={{
                            name: agent.name,
                            description: agent.description,
                            excluded_apps: agent.excluded_apps,
                            excluded_functions: agent.excluded_functions,
                            custom_instructions: agent.custom_instructions,
                          }}
                          onSubmit={async (values) => {
                            if (!project) return;
                            try {
                              await updateAgent(
                                project.id,
                                agent.id,
                                user!.accessToken,
                                values.name,
                                values.description,
                                values.excluded_apps,
                                values.excluded_functions,
                                values.custom_instructions,
                              );

                              await loadProject();
                            } catch (error) {
                              console.error("Error updating agent:", error);
                            }
                          }}
                        >
                          <Button variant="outline" size="sm">
                            Edit
                          </Button>
                        </AgentForm>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </div>
        )}
      </div>
    </div>
  );
}
