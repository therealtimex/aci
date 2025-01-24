"use client"

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Button } from "@/components/ui/button"
import { type AppFunction } from "@/lib/dummy-data"

interface AppFunctionsTableProps {
  functions: AppFunction[]
}

export function AppFunctionsTable({ functions }: AppFunctionsTableProps) {
  return (
    <div className="rounded-md border">
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Function Name</TableHead>
            <TableHead>Function ID</TableHead>
            <TableHead className="max-w-[500px]">Description</TableHead>
            <TableHead className="text-right">Actions</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {functions.map((func) => (
            <TableRow key={func.id}>
              <TableCell className="font-medium">{func.name}</TableCell>
              <TableCell>{func.functionId}</TableCell>
              <TableCell className="max-w-[500px]">{func.description}</TableCell>
              <TableCell className="text-right">
                <Button variant="outline" size="sm">
                  See Details
                </Button>
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  )
}
