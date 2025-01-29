"use client";

import {
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableCell,
  TableHead,
} from "@/components/ui/table";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Button } from "@/components/ui/button";
import { useState } from "react";
import { useParams } from "next/navigation";
import { GoPlus } from "react-icons/go";
import { Separator } from "@/components/ui/separator";
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

export default function AppConfigPage() {
  const { appId } = useParams<{ appId: string }>();

  const [activeTab, setActiveTab] = useState("linkedAccounts");

  return (
    <div>
      <div className="m-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">GitHub</h1>
          <span>{appId}</span>
        </div>
        <Button className="bg-teal-400 text-black hover:bg-teal-500">
          <GoPlus />
          Add Account
        </Button>
      </div>
      <Separator />

      <div className="m-4">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-4">
          <TabsList>
            <TabsTrigger value="linkedAccounts">Linked Accounts</TabsTrigger>
            <TabsTrigger value="logs">Logs</TabsTrigger>
          </TabsList>
          <TabsContent value="linkedAccounts">
            <div>
              <div className="rounded-md border">
                <Table>
                  <TableHeader className="bg-gray-100">
                    <TableRow>
                      <TableHead>Linked Account Owner ID</TableHead>
                      <TableHead>Linked Account Owner Name</TableHead>
                      <TableHead>Created at</TableHead>
                      <TableHead>Delete</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow>
                      <TableCell>sdfsdf234</TableCell>
                      <TableCell>Jessie</TableCell>
                      <TableCell>2025.11.11</TableCell>
                      <TableCell>
                        <AlertDialog>
                          <AlertDialogTrigger asChild>
                            <Button className="bg-red-500 text-white hover:bg-red-600">
                              Delete
                            </Button>
                          </AlertDialogTrigger>
                          <AlertDialogContent>
                            <AlertDialogHeader>
                              <AlertDialogTitle>Are you sure?</AlertDialogTitle>
                              <AlertDialogDescription>
                                This action cannot be undone. This will
                                permanently delete the linked account.
                              </AlertDialogDescription>
                            </AlertDialogHeader>
                            <AlertDialogFooter>
                              <AlertDialogCancel>Cancel</AlertDialogCancel>
                              <AlertDialogAction
                                onClick={() =>
                                  console.log("TODO: delete linked account")
                                }
                              >
                                Delete
                              </AlertDialogAction>
                            </AlertDialogFooter>
                          </AlertDialogContent>
                        </AlertDialog>
                      </TableCell>
                    </TableRow>
                  </TableBody>
                </Table>
              </div>
            </div>
          </TabsContent>
          <TabsContent value="logs">
            <h2 className="text-xl font-bold">Logs</h2>
            {/* TODO: Logs content goes here */}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
