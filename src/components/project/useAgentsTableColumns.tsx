"use client";

import { createColumnHelper, ColumnDef } from "@tanstack/react-table";
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

const columnHelper = createColumnHelper<Agent>();

export const useAgentsTableColumns = (
  projectId: string,
  onDeleteAgent: (agentId: string) => Promise<void>,
  reload: () => Promise<void>,
  onInstructionsSave: () => Promise<void>,
): ColumnDef<Agent>[] => {
  return useMemo(() => {
    return [
      columnHelper.accessor("name", {
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
        enableGlobalFilter: true,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("description", {
        header: "DESCRIPTION",
        enableGlobalFilter: true,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("api_keys", {
        header: "API KEY",
        cell: (ctx) => (
          <div className="font-mono w-24">
            <IdDisplay id={ctx.getValue()[0].key} />
          </div>
        ),
        enableGlobalFilter: false,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("created_at", {
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
        cell: (ctx) => (
          <div>
            {new Date(ctx.getValue())
              .toISOString()
              .replace(/\.\d{3}Z$/, "")
              .replace("T", " ")}
          </div>
        ),
        enableGlobalFilter: false,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("allowed_apps", {
        header: "ALLOWED APPS",
        cell: (ctx) => (
          <div className="text-center">
            <AppEditForm
              reload={reload}
              projectId={projectId}
              agentId={ctx.row.original.id}
              allowedApps={ctx.row.original.allowed_apps || []}
            >
              <Button variant="outline" size="sm" data-action="edit-apps">
                Edit
              </Button>
            </AppEditForm>
          </div>
        ),
        enableGlobalFilter: false,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("custom_instructions", {
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
        cell: (ctx) => (
          <div className="text-center">
            <AgentInstructionFilterForm
              projectId={projectId}
              agentId={ctx.row.original.id}
              initialInstructions={ctx.row.original.custom_instructions}
              allowedApps={ctx.row.original.allowed_apps || []}
              onSaveSuccess={onInstructionsSave}
            >
              <Button variant="outline" size="sm">
                Edit
              </Button>
            </AgentInstructionFilterForm>
          </div>
        ),
        enableGlobalFilter: false,
      }) as ColumnDef<Agent>,
      columnHelper.accessor("id", {
        header: () => <div className="text-center">DELETE</div>,
        cell: (ctx) => (
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
                    {ctx.row.original.name}
                    &quot; and remove all its associated data.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction
                    onClick={() => onDeleteAgent(ctx.row.original.id)}
                  >
                    Delete
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        ),
        enableGlobalFilter: false,
      }) as ColumnDef<Agent>,
    ];
  }, [projectId, onDeleteAgent, reload, onInstructionsSave]);
};
