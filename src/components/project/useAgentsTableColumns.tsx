"use client";

import { ColumnDef } from "@tanstack/react-table";
import { IdDisplay } from "@/components/apps/id-display";
import { Button } from "@/components/ui/button";
import { GoTrash } from "react-icons/go";
import { BsQuestionCircle } from "react-icons/bs";
import {
  Tooltip,
  TooltipContent,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { AppEditForm } from "@/components/project/app-edit-form";
import { AgentInstructionFilterForm } from "@/components/project/agent-instruction-filter-form";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { ArrowUpDown } from "lucide-react";
import { Agent } from "@/lib/types/project";
import { useMemo } from "react";

export const useAgentsTableColumns = (
  projectId: string,
  onDeleteAgent: (agentId: string) => Promise<void>,
  reload: () => Promise<void>,
  onInstructionsSave: () => Promise<void>,
): ColumnDef<Agent>[] => {
  return useMemo(() => {
    return [
      {
        accessorKey: "name",
        header: ({ column }) => (
          <div className="text-left">
            <Button
              variant="ghost"
              onClick={() =>
                column.toggleSorting(column.getIsSorted() === "asc")
              }
              className="w-full justify-start px-0"
            >
              AGENT NAME
              <ArrowUpDown className="h-4 w-4" />
            </Button>
          </div>
        ),
        filterFn: "includesString",
      },
      {
        accessorKey: "description",
        header: "DESCRIPTION",
        filterFn: "includesString",
      },
      {
        accessorKey: "api_keys",
        header: "API KEY",
        cell: ({ row }) => {
          const agent = row.original;
          return (
            <div className="font-mono w-24">
              <IdDisplay id={agent.api_keys[0].key} />
            </div>
          );
        },
      },
      {
        accessorKey: "created_at",
        header: ({ column }) => (
          <div className="text-left">
            <Button
              variant="ghost"
              onClick={() =>
                column.toggleSorting(column.getIsSorted() === "asc")
              }
              className="w-full justify-start px-0"
            >
              CREATION TIME
              <ArrowUpDown className="h-4 w-4" />
            </Button>
          </div>
        ),
        cell: ({ row }) => {
          return (
            <div>
              {new Date(row.getValue("created_at"))
                .toISOString()
                .replace(/\.\d{3}Z$/, "")
                .replace("T", " ")}
            </div>
          );
        },
        sortingFn: "datetime",
      },
      {
        accessorKey: "allowed_apps",
        header: "ALLOWED APPS",
        cell: ({ row }) => {
          const agent = row.original;
          return (
            <div className="text-center">
              <AppEditForm
                reload={reload}
                projectId={projectId}
                agentId={agent.id}
                allowedApps={agent.allowed_apps || []}
              >
                <Button variant="outline" size="sm" data-action="edit-apps">
                  Edit
                </Button>
              </AppEditForm>
            </div>
          );
        },
      },
      {
        accessorKey: "custom_instructions",
        header: () => (
          <div className="text-left w-40">
            <Tooltip>
              <TooltipTrigger className="flex items-center whitespace-nowrap gap-2">
                <span className="text-sm">CUSTOM INSTRUCTIONS</span>
                <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
              </TooltipTrigger>
              <TooltipContent>
                <p>
                  Outline in natural language when an API execution request from
                  agents should be blocked.
                </p>
              </TooltipContent>
            </Tooltip>
          </div>
        ),
        cell: ({ row }) => {
          const agent = row.original;
          return (
            <div className="text-center">
              <AgentInstructionFilterForm
                projectId={projectId}
                agentId={agent.id}
                initialInstructions={agent.custom_instructions}
                allowedApps={agent.allowed_apps || []}
                onSaveSuccess={onInstructionsSave}
              >
                <Button variant="outline" size="sm">
                  Edit
                </Button>
              </AgentInstructionFilterForm>
            </div>
          );
        },
      },
      {
        id: "delete",
        header: () => <div className="text-center">DELETE</div>,
        cell: ({ row }) => {
          const agent = row.original;
          return (
            <div className="text-center">
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    <GoTrash />
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle>Delete Agent?</AlertDialogTitle>
                    <AlertDialogDescription>
                      This action cannot be undone. This will permanently delete
                      the agent &quot;
                      {agent.name}
                      &quot; and remove all its associated data.
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction onClick={() => onDeleteAgent(agent.id)}>
                      Delete
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          );
        },
      },
    ];
  }, [projectId, onDeleteAgent, reload, onInstructionsSave]);
};
