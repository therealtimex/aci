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
import { type AppConfig } from "@/lib/types/appconfig";
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
import { Input } from "@/components/ui/input";
import { IdDisplay } from "./id-display";
import { GoTrash } from "react-icons/go";

interface AppConfigsTableProps {
  appConfigs: AppConfig[];
}

export function AppConfigsTable({ appConfigs }: AppConfigsTableProps) {
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");

  const filteredAppConfigs = appConfigs.filter((config) =>
    config.id.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div className="flex-1 flex items-center space-x-4">
          <Input
            placeholder="Search keyword, category, etc."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-sm"
          />
          <Select value={selectedCategory} onValueChange={setSelectedCategory}>
            <SelectTrigger className="w-[120px]">
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              <SelectItem value="development">Development</SelectItem>
              <SelectItem value="productivity">Productivity</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <div className="rounded-md border">
        <Table>
          <TableHeader className="bg-gray-100">
            <TableRow>
              <TableHead>APP NAME</TableHead>
              <TableHead>APP ID</TableHead>
              <TableHead>LINKED ACCOUNTS</TableHead>
              <TableHead>ENABLED</TableHead>
              <TableHead></TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredAppConfigs.map((config) => (
              <TableRow key={config.id}>
                <TableCell>{config.id}</TableCell>
                <TableCell>
                  <div className="flex-shrink-0 w-20">
                    <IdDisplay id={config.id} />
                  </div>
                </TableCell>
                <TableCell>10</TableCell>
                <TableCell>
                  <Switch checked={config.enabled} />
                </TableCell>
                <TableCell className="space-x-2 flex">
                  <Link href={`/appconfig/${config.id}`}>
                    <Button variant="outline" size="sm">
                      Open
                    </Button>
                  </Link>
                  <Button variant="ghost" size="sm" className="text-red-600">
                    <GoTrash />
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
