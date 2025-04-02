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
  FilterFn,
  FilterFnOption,
} from "@tanstack/react-table";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { useEffect, useState, useMemo } from "react";
import { EnhancedDataTableToolbar } from "./data-table-toolbar";
import { rankItem } from "@tanstack/match-sorter-utils";

const fuzzyFilter: FilterFn<unknown> = (row, columnId, value, addMeta) => {
  if (!value || value === "") return true;
  const itemRank = rankItem(row.getValue(columnId), value);
  addMeta({
    itemRank,
  });
  return itemRank.passed;
};

interface EnhancedDataTableProps<TData, TValue> {
  columns: ColumnDef<TData, TValue>[];
  data: TData[];
  // Default sorting configuration
  defaultSorting?: {
    id: string;
    desc: boolean;
  }[];
  // Placeholder text for search input
  searchPlaceholder?: string;
  // Row click handler - can trigger button clicks or custom events
  onRowClick?: (row: Row<TData>) => void;
  // Additional class for the row to indicate it's clickable
  rowClickableClassName?: string;
}

export function EnhancedDataTable<TData, TValue>({
  columns,
  data,
  defaultSorting = [],
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

  const hasFilterableColumns = useMemo(() => {
    return columns.some((column) => column.enableGlobalFilter === true);
  }, [columns]);

  const table = useReactTable({
    data,
    columns,
    filterFns: {
      fuzzy: fuzzyFilter,
    },
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onSortingChange: setSorting,
    onGlobalFilterChange: setGlobalFilter,
    globalFilterFn: "fuzzy" as FilterFnOption<TData>,
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
        showSearchInput={hasFilterableColumns}
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
