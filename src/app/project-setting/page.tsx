"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";
import { Badge } from "@/components/ui/badge";
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

export default function ProjectSettingPage() {
  const { project } = useProject();

  if (!project) {
    return <div>Loading...</div>;
  }

  const hasAgents = project.agents && project.agents.length > 0;

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
            <div className="flex items-center gap-2">
              <Switch checked={hasAgents} />
              <span className="text-sm">Enable</span>
            </div>
            <Button variant="outline">
              <MdAdd />
              Create Agent
            </Button>
          </div>
        </div>

        {hasAgents && (
          <div className="border rounded-lg">
            <Table>
              <TableHeader className="bg-gray-50">
                <TableRow>
                  <TableHead>AGENT NAME & ID</TableHead>
                  <TableHead>API KEY</TableHead>
                  <TableHead>CREATION DATE AND TIME</TableHead>
                  <TableHead>ENABLED APPS</TableHead>
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
                      <TableCell className="font-mono">
                        <div className="w-24">
                          <IdDisplay id={agent.api_keys[0].key} />
                        </div>
                      </TableCell>
                      <TableCell>{agent.created_at}</TableCell>
                      <TableCell>
                        {/* TODO: implement enabled apps list */}
                        <Badge key="Slack" variant="secondary" className="mr-1">
                          Slack
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {/* TODO: implement access level */}
                        default access
                      </TableCell>
                      <TableCell>
                        <Button variant="outline" size="sm">
                          Edit
                        </Button>
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
