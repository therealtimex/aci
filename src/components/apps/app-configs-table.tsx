"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Button } from "@/components/ui/button";
import { type AppConfig } from "@/lib/types";
import { useState } from "react";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import Link from "next/link";

interface AppConfigsTableProps {
  appConfigs: AppConfig[];
}

export function AppConfigsTable({ appConfigs }: AppConfigsTableProps) {
  const [selectedCategory, setSelectedCategory] = useState("all"); // eslint-disable-line
  const [selectedTag, setSelectedTag] = useState("all"); // eslint-disable-line

  const categories: string[] = [];
  const tags: string[] = [];

  return (
    <div>
      <div className="flex items-center gap-3 mb-4">
        <Select onValueChange={setSelectedCategory}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            {["all", ...categories].map((category) => (
              <SelectItem key={category} value={category}>
                {category}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select onValueChange={setSelectedTag}>
          <SelectTrigger className="w-[80px]">
            <SelectValue placeholder="Tags" />
          </SelectTrigger>
          <SelectContent>
            {["all", ...tags].map((tag) => (
              <SelectItem key={tag} value={tag}>
                {tag}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead>APP NAME</TableHead>
              <TableHead>APP ID</TableHead>
              <TableHead>LINKED ACCOUNTS</TableHead>
              <TableHead>ENABLED</TableHead>
              <TableHead>DETAILS</TableHead>
              <TableHead>DELETE</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {appConfigs.map((config) => (
              <TableRow key={config.id}>
                <TableCell className="font-medium">app name</TableCell>
                <TableCell className="max-w-[500px]">{config.app_id}</TableCell>
                <TableCell>12</TableCell>
                <TableCell>
                  <Switch />
                </TableCell>
                <TableCell>
                  <Link href={`/appconfig/${config.app_id}`}>
                    <Button variant="outline" size="sm">
                      Open
                    </Button>
                  </Link>
                </TableCell>
                <TableCell>
                  <Button variant="destructive" size="sm">
                    Delete
                  </Button>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
