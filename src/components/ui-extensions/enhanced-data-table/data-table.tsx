"use client";

import {
  ColumnDef,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable,
  getFilteredRowModel,
  Row,
} from "@tanstack/react-table";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useEffect, useState } from "react";
import { EnhancedDataTableToolbar } from "./data-table-toolbar";

interface EnhancedDataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  // Default sorting configuration
  defaultSorting?: {
    id: string;
    desc: boolean;
  }[];
  // Specify which columns are searchable (empty means disable search)
  searchableColumns?: string[];
  // Placeholder text for search input
  searchPlaceholder?: string;
  // Row click handler - can trigger button clicks or custom events
  onRowClick?: (row: Row<TData>) => void;
  // Additional class for the row to indicate it's clickable
  rowClickableClassName?: string;
}

function enhancedGlobalFilterFn<T>(
  row: Row<T>,
  filterValue: string,
  searchableColumns: string[] = [],
): boolean {
  const search = filterValue.toLowerCase();

  // If searchableColumns is empty, disable search completely
  if (searchableColumns.length === 0) return true;

  const visibleValues = row
    .getAllCells()
    .filter((cell) => searchableColumns.includes(cell.column.id))
    .map((cell) => {
      const value = cell.getValue();
      if (typeof value === "string") {
        return value.toLowerCase();
      }
      if (typeof value === "number") {
        return value.toString();
      }
      return "";
    });

  return visibleValues.some((value: string) => value.includes(search));
}

export function EnhancedDataTable<TData, TValue>({
  columns,
  data,
  defaultSorting = [],
  searchableColumns = [],
  searchPlaceholder = "Search...",
}: EnhancedDataTableProps<TData, TValue>) {
  const [sorting, setSorting] = useState<SortingState>(defaultSorting);
  const [globalFilter, setGlobalFilter] = useState("");

  // Apply default sorting on initial render
  useEffect(() => {
    if (defaultSorting.length > 0) {
      setSorting(defaultSorting);
    }
  }, [defaultSorting]);

  const table = useReactTable({
    data,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: (row, _columnId, filterValue) =>
      enhancedGlobalFilterFn(row, filterValue as string, searchableColumns),
    state: {
      sorting,
      globalFilter,
    },
  });

  return (
    <div>
      <EnhancedDataTableToolbar
        table={table}
        placeholder={searchPlaceholder}
        searchableColumns={searchableColumns}
      />
      <div className="border rounded-lg">
        <Table>
          <TableHeader className="bg-gray-50">
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => (
                  <TableHead key={header.id} className="px-4 py-2">
                    {header.isPlaceholder
                      ? null
                      : flexRender(
                          header.column.columnDef.header,
                          header.getContext(),
                        )}
                  </TableHead>
                ))}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  data-state={row.getIsSelected() && "selected"}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="px-4 py-2">
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext(),
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={columns.length}
                  className="h-24 text-center"
                >
                  No results found
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
