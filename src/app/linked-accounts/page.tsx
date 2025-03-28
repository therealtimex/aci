"use client";

import { useEffect, useState, useCallback, useMemo } from "react";
import { LinkedAccount } from "@/lib/types/linkedaccount";
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
import { GoTrash } from "react-icons/go";
import { Tabs, TabsContent } from "@/components/ui/tabs";
import { useProject } from "@/components/context/project";
import { getApiKey } from "@/lib/api/util";
import {
  getAllLinkedAccounts,
  deleteLinkedAccount,
  updateLinkedAccount,
} from "@/lib/api/linkedaccount";
import { getApps } from "@/lib/api/app";
import { getAllAppConfigs } from "@/lib/api/appconfig";
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
import { Separator } from "@/components/ui/separator";
import { LinkedAccountDetails } from "@/components/linkedaccount/linked-account-details";
import { AppConfig } from "@/lib/types/appconfig";
import { AddAccountForm } from "@/components/appconfig/add-account";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { App } from "@/lib/types/app";
import { EnhancedSwitch } from "@/components/ui-extensions/enhanced-switch";

export default function LinkedAccountsPage() {
  const { project } = useProject();
  const [linkedAccounts, setLinkedAccounts] = useState<LinkedAccount[]>([]);
  const [appConfigs, setAppConfigs] = useState<AppConfig[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedCategory, setSelectedCategory] = useState<string>("all");
  const [appsMap, setAppsMap] = useState<Record<string, App>>({});

  const categories = useMemo(
    () => [
      ...new Set(Object.values(appsMap).flatMap((app) => app.categories || [])),
    ],
    [appsMap],
  );

  const filteredLinkedAccounts = useMemo(
    () =>
      linkedAccounts.filter((account) => {
        const app = appsMap[account.app_name];
        return (
          app &&
          (selectedCategory === "all" ||
            app.categories?.includes(selectedCategory))
        );
      }),
    [linkedAccounts, appsMap, selectedCategory],
  );

  const loadAppMaps = useCallback(async () => {
    if (!project || linkedAccounts.length === 0) {
      return;
    }

    try {
      const apiKey = getApiKey(project);
      const appNames = Array.from(
        new Set(linkedAccounts.map((account) => account.app_name)),
      );

      const apps = await getApps(appNames, apiKey);

      const missingApps = appNames.filter(
        (name) => !apps.some((app) => app.name === name),
      );

      if (missingApps.length > 0) {
        console.warn(`Missing apps: ${missingApps.join(", ")}`);
      }

      setAppsMap(
        apps.reduce(
          (acc, app) => {
            acc[app.name] = app;
            return acc;
          },
          {} as Record<string, App>,
        ),
      );
    } catch (error) {
      console.error("Failed to load app data:", error);
    }
  }, [project, linkedAccounts]);

  const loadAppConfigs = async () => {
    if (!project) {
      console.warn("No active project");
      return;
    }

    try {
      setIsLoading(true);
      const apiKey = getApiKey(project);
      const configs = await getAllAppConfigs(apiKey);
      setAppConfigs(configs);
    } catch (error) {
      console.error("Failed to load app configurations:", error);
      toast.error("Failed to load app configurations");
    } finally {
      setIsLoading(false);
    }
  };

  const refreshLinkedAccounts = async (silent: boolean = false) => {
    if (!project) {
      console.warn("No active project");
      return;
    }

    try {
      if (!silent) {
        setIsLoading(true);
      }

      const apiKey = getApiKey(project);
      const linkedAccounts = await getAllLinkedAccounts(apiKey);
      setLinkedAccounts(linkedAccounts);
    } catch (error) {
      console.error("Failed to load linked accounts:", error);
      toast.error("Failed to load linked accounts");
    } finally {
      if (!silent) {
        setIsLoading(false);
      }
    }
  };

  const toggleAccountStatus = async (
    accountId: string,
    newStatus: boolean,
  ): Promise<boolean> => {
    try {
      if (!project) {
        console.warn("No active project");
        return false;
      }
      const apiKey = getApiKey(project);

      await updateLinkedAccount(accountId, apiKey, newStatus);

      await refreshLinkedAccounts(true);

      return true;
    } catch (error) {
      console.error("Failed to update linked account:", error);
      toast.error("Failed to update linked account");
      return false;
    }
  };

  useEffect(() => {
    if (project) {
      const loadData = async () => {
        setIsLoading(true);
        await Promise.all([refreshLinkedAccounts(true), loadAppConfigs()]);
        setIsLoading(false);
      };

      loadData();
    }
  }, [project]);

  useEffect(() => {
    if (linkedAccounts.length > 0) {
      loadAppMaps();
    }
  }, [linkedAccounts, loadAppMaps]);

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Linked Accounts</h1>
          <p className="text-sm text-muted-foreground">
            Manage your linked accounts here.
          </p>
        </div>
        <div>
          {!isLoading && appConfigs.length > 0 && (
            <AddAccountForm
              appInfos={appConfigs.map((config) => ({
                name: config.app_name,
                securitySchemes: [config.security_scheme],
              }))}
              updateLinkedAccounts={() => refreshLinkedAccounts(true)}
            />
          )}
        </div>
      </div>
      <Separator />

      <div className="m-4">
        <Tabs defaultValue={"linked"} className="w-full">
          <TabsContent value="linked">
            <div className="flex items-center space-x-4 mb-6">
              <Select
                value={selectedCategory}
                onValueChange={setSelectedCategory}
              >
                <SelectTrigger className="w-[120px]">
                  <SelectValue placeholder="ALL" />
                </SelectTrigger>
                <SelectContent>
                  {["all", ...categories].map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {isLoading ? (
              <div className="text-center p-8">Loading...</div>
            ) : filteredLinkedAccounts.length === 0 ? (
              <div className="text-center p-8 text-muted-foreground">
                No linked accounts found
              </div>
            ) : (
              <div className="rounded-md border">
                <Table>
                  <TableHeader className="bg-gray-100">
                    <TableRow>
                      <TableHead>APP NAME</TableHead>
                      <TableHead>LINKED ACCOUNT OWNER ID</TableHead>
                      <TableHead>CREATED AT</TableHead>
                      <TableHead>ENABLED</TableHead>
                      <TableHead>DETAILS</TableHead>
                      <TableHead></TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {filteredLinkedAccounts.map((account) => (
                      <TableRow key={account.id}>
                        <TableCell>
                          <div className="font-medium">{account.app_name}</div>
                        </TableCell>
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
                            successMessage={(newState) => {
                              return `Linked account ${account.linked_account_owner_id} ${newState ? "enabled" : "disabled"}`;
                            }}
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
                                  permanently delete the linked account for
                                  owner ID &quot;
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

                                      await deleteLinkedAccount(
                                        account.id,
                                        apiKey,
                                      );

                                      refreshLinkedAccounts(true);

                                      toast.success(
                                        `Linked account ${account.linked_account_owner_id} deleted`,
                                      );
                                    } catch (error) {
                                      console.error(error);
                                      toast.error(
                                        "Failed to delete linked account",
                                      );
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
            )}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
