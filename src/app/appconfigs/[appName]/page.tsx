"use client";

import { useEffect, useState } from "react";
import { LinkedAccount } from "@/lib/types/linkedaccount";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { IdDisplay } from "@/components/apps/id-display";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { BsQuestionCircle } from "react-icons/bs";
import {
  Tooltip,
  TooltipTrigger,
  TooltipContent,
} from "@/components/ui/tooltip";
import { Switch } from "@/components/ui/switch";
import { GoTrash } from "react-icons/go";
import { useParams } from "next/navigation";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { App } from "@/lib/types/app";
import { useProject } from "@/components/context/project";
import { AddAccountForm } from "@/components/appconfig/add-account";
import { getApiKey } from "@/lib/api/util";
import { getApp } from "@/lib/api/app";
import {
  getLinkedAccounts,
  deleteLinkedAccount,
  updateLinkedAccount,
} from "@/lib/api/linkedaccount";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogDescription,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";
import { toast } from "sonner";

export default function AppConfigDetailPage() {
  const { appName } = useParams<{ appName: string }>();
  const { project } = useProject();
  const [app, setApp] = useState<App | null>(null);
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);

  const sortLinkedAccountsByCreateTime = (accounts: LinkedAccount[]) => {
    return [...accounts].sort((a, b) => {
      if (!a.created_at) return 1;
      if (!b.created_at) return -1;
      return (
        new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
      );
    });
  };

  useEffect(() => {
    async function loadAppAndLinkedAccounts() {
      if (!project) {
        console.warn("No active project");
        return;
      }
      const apiKey = getApiKey(project);

      const app = await getApp(appName, apiKey);
      setApp(app);

      const linkedAccounts = await getLinkedAccounts(appName, apiKey);

      setLinkedAccounts(sortLinkedAccountsByCreateTime(linkedAccounts));
    }
    loadAppAndLinkedAccounts();
  }, [project, appName]);

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg">
            {app && (
              <Image
                src={app?.logo ?? ""}
                alt={`${app?.display_name} logo`}
                fill
                className="object-contain"
              />
            )}
          </div>
          <div>
            <h1 className="text-2xl font-semibold">{app?.display_name}</h1>
            <IdDisplay id={app?.name ?? ""} />
          </div>
        </div>
        {app && (
          <AddAccountForm
            app={app}
            updateLinkedAccounts={async () => {
              if (!project) {
                console.warn("No active project");
                return;
              }
              const apiKey = getApiKey(project);

              const linkedAccounts = await getLinkedAccounts(appName, apiKey);
              setLinkedAccounts(sortLinkedAccountsByCreateTime(linkedAccounts));
            }}
          />
        )}
      </div>

      <Tabs defaultValue={"linked"} className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="linked">
            <div className="mr-2">
              <Tooltip>
                <TooltipTrigger asChild>
                  <span className="cursor-pointer">
                    <BsQuestionCircle className="h-4 w-4 text-muted-foreground" />
                  </span>
                </TooltipTrigger>
                <TooltipContent side="top">
                  <p className="text-xs">
                    {
                      "This shows a list of end-users who have connected their account in this application to your agent."
                    }
                  </p>
                </TooltipContent>
              </Tooltip>
            </div>
            Linked Accounts
          </TabsTrigger>
          {/* <TabsTrigger value="logs">Logs</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger> */}
        </TabsList>

        <TabsContent value="linked">
          <div className="rounded-md border">
            <Table>
              <TableHeader className="bg-gray-100">
                <TableRow>
                  <TableHead>LINKED ACCOUNT OWNER ID</TableHead>
                  <TableHead>CREATED AT</TableHead>
                  <TableHead>ENABLED</TableHead>
                  <TableHead></TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {linkedAccounts.map((account) => (
                  <TableRow key={account.id}>
                    <TableCell>
                      <div className="flex-shrink-0">
                        <IdDisplay id={account.linked_account_owner_id} />
                      </div>
                    </TableCell>
                    <TableCell>
                      {new Date(account.created_at)
                        .toISOString()
                        .replace(/\.\d{3}Z$/, "")
                        .replace("T", " ")}
                    </TableCell>
                    <TableCell>
                      <Switch
                        checked={account.enabled}
                        className={account.enabled ? "bg-[#1CD1AF]" : ""}
                        onCheckedChange={async (checked) => {
                          try {
                            if (!project) {
                              console.warn("No active project");
                              return;
                            }
                            const apiKey = getApiKey(project);

                            await updateLinkedAccount(
                              account.id,
                              apiKey,
                              checked,
                            );

                            // Refresh the linked accounts list after update
                            const linkedAccounts = await getLinkedAccounts(
                              appName,
                              apiKey,
                            );
                            setLinkedAccounts(
                              sortLinkedAccountsByCreateTime(linkedAccounts),
                            );
                            toast.success(
                              "Linked account updated successfully",
                            );
                          } catch (error) {
                            console.error(
                              "Failed to update linked account:",
                              error,
                            );
                          }
                        }}
                      />
                    </TableCell>
                    <TableCell>
                      <AlertDialog>
                        <AlertDialogTrigger asChild>
                          <Button
                            variant="ghost"
                            size="sm"
                            className="text-red-600"
                          >
                            <GoTrash />
                          </Button>
                        </AlertDialogTrigger>
                        <AlertDialogContent>
                          <AlertDialogHeader>
                            <AlertDialogTitle>
                              Confirm Deletion?
                            </AlertDialogTitle>
                            <AlertDialogDescription>
                              This action cannot be undone. This will
                              permanently delete the linked account for owner ID
                              &quot;
                              {account.linked_account_owner_id}&quot;.
                            </AlertDialogDescription>
                          </AlertDialogHeader>
                          <AlertDialogFooter>
                            <AlertDialogCancel>Cancel</AlertDialogCancel>
                            <AlertDialogAction
                              onClick={async () => {
                                try {
                                  if (!project) {
                                    console.warn("No active project");
                                    return;
                                  }
                                  const apiKey = getApiKey(project);

                                  await deleteLinkedAccount(account.id, apiKey);

                                  // Refresh the linked accounts list after deletion
                                  const linkedAccounts =
                                    await getLinkedAccounts(appName, apiKey);
                                  setLinkedAccounts(
                                    sortLinkedAccountsByCreateTime(
                                      linkedAccounts,
                                    ),
                                  );
                                } catch (error) {
                                  console.error(error);
                                }
                              }}
                            >
                              Delete
                            </AlertDialogAction>
                          </AlertDialogFooter>
                        </AlertDialogContent>
                      </AlertDialog>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </TabsContent>

        {/* <TabsContent value="logs">
          <div className="text-gray-500">Logs content coming soon...</div>
        </TabsContent>

        <TabsContent value="settings">
          <div className="text-gray-500">Settings content coming soon...</div>
        </TabsContent> */}
      </Tabs>
    </div>
  );
}
