"use client";

import { useEffect, useState, useCallback } from "react";
import { LinkedAccount } from "@/lib/types/linkedaccount";
import Image from "next/image";
import { Button } from "@/components/ui/button";
import { IdDisplay } from "@/components/apps/id-display";
import { LinkedAccountDetails } from "@/components/linkedaccount/linked-account-details";
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
import { GoTrash } from "react-icons/go";
import { useParams } from "next/navigation";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { App } from "@/lib/types/app";
import { useProject } from "@/components/context/project";
import { AddAccountForm } from "@/components/appconfig/add-account";
import { getApiKey } from "@/lib/api/util";
import { getApp } from "@/lib/api/app";
import {
  getAppLinkedAccounts,
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
import Link from "next/link";
import { EnhancedSwitch } from "@/components/ui-extensions/enhanced-switch";

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

  const refreshLinkedAccounts = useCallback(async () => {
    if (!project) {
      console.warn("No active project");
      return;
    }
    const apiKey = getApiKey(project);
    const linkedAccounts = await getAppLinkedAccounts(appName, apiKey);
    setLinkedAccounts(sortLinkedAccountsByCreateTime(linkedAccounts));
  }, [project, appName]);

  const toggleAccountStatus = useCallback(
    async (accountId: string, newStatus: boolean) => {
      try {
        if (!project) {
          console.warn("No active project");
          return false;
        }
        const apiKey = getApiKey(project);

        await updateLinkedAccount(accountId, apiKey, newStatus);

        // Refresh the linked accounts list after update
        await refreshLinkedAccounts();

        return true;
      } catch (error) {
        console.error("Failed to update linked account:", error);
        return false;
      }
    },
    [project, refreshLinkedAccounts],
  );

  useEffect(() => {
    async function loadAppAndLinkedAccounts() {
      if (!project) {
        console.warn("No active project");
        return;
      }
      const apiKey = getApiKey(project);

      const app = await getApp(appName, apiKey);
      setApp(app);
      await refreshLinkedAccounts();
    }
    loadAppAndLinkedAccounts();
  }, [project, appName, refreshLinkedAccounts]);

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
            <Link href={`/apps/${app?.name}`}>
              <h1 className="text-2xl font-semibold">{app?.display_name}</h1>
            </Link>
            <IdDisplay id={app?.name ?? ""} />
          </div>
        </div>
        {app && (
          <AddAccountForm
            appInfos={[
              {
                name: app.name,
                securitySchemes: app.security_schemes,
              },
            ]}
            updateLinkedAccounts={refreshLinkedAccounts}
          />
        )}
      </div>

      <Tabs defaultValue={"linked"} className="w-full">
        <TabsList className="mb-6">
          <TabsTrigger value="linked">
            Linked Accounts
            <div className="ml-2">
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
                  <TableHead>DETAILS</TableHead>
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
                      <EnhancedSwitch
                        checked={account.enabled}
                        onAsyncChange={(checked) =>
                          toggleAccountStatus(account.id, checked)
                        }
                        successMessage={`Linked account ${account.linked_account_owner_id} ${account.enabled ? "disabled" : "enabled"}`}
                        errorMessage="Failed to update linked account"
                      />
                    </TableCell>
                    <TableCell>
                      <LinkedAccountDetails
                        account={account}
                        toggleAccountStatus={toggleAccountStatus}
                      >
                        <Button variant="outline" size="sm">
                          See Details
                        </Button>
                      </LinkedAccountDetails>
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
                                    await getAppLinkedAccounts(appName, apiKey);
                                  setLinkedAccounts(
                                    sortLinkedAccountsByCreateTime(
                                      linkedAccounts,
                                    ),
                                  );

                                  toast.success(
                                    `Linked account ${account.linked_account_owner_id} deleted`,
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
