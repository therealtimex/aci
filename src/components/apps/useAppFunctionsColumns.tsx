"use client";

import { FunctionDetail } from "@/components/apps/function-detail";
import { type AppFunction } from "@/lib/types/appfunction";
import { useMemo, useState } from "react";
import { IdDisplay } from "@/components/apps/id-display";
import {
  createColumnHelper,
  type ColumnDef,
  type Table,
} from "@tanstack/react-table";
import { ColumnFilter } from "@/components/ui-extensions/enhanced-data-table/column-filter";

const columnHelper = createColumnHelper<AppFunction>();

export interface TagFilterComponentProps {
  tableInstance: Table<AppFunction> | null;
  functions: AppFunction[];
}

export interface AppFunctionsTableState {
  tableInstance: Table<AppFunction> | null;
  setTableInstance: (table: Table<AppFunction> | null) => void;
  tagFilterComponent: React.ReactNode;
}

export const useAppFunctionsColumns = (): ColumnDef<AppFunction>[] => {
  return useMemo(() => {
    return [
      columnHelper.accessor("name", {
        header: "FUNCTION NAME",
        cell: (info) => <IdDisplay id={info.getValue()} dim={false} />,
        enableGlobalFilter: true,
        size: 50,
      }),

      columnHelper.accessor("tags", {
        header: "TAGS",
        cell: (info) => (
          <div className="flex flex-wrap gap-2 overflow-hidden">
            {(info.getValue() || []).map((tag: string) => (
              <span
                key={tag}
                className="rounded-md bg-gray-100 px-3 py-1 text-sm font-medium text-gray-600 border border-gray-200"
              >
                {tag}
              </span>
            ))}
          </div>
        ),
        enableGlobalFilter: true,
        filterFn: "arrIncludes",
        enableColumnFilter: true,
      }),

      columnHelper.accessor("description", {
        header: "DESCRIPTION",
        cell: (info) => <div className="max-w-[500px]">{info.getValue()}</div>,
        enableGlobalFilter: true,
      }),

      columnHelper.accessor((row) => row, {
        id: "details",
        header: () => <div className="text-center">DETAILS</div>,
        cell: (info) => (
          <div className="text-center">
            <FunctionDetail func={info.getValue()} />
          </div>
        ),
        enableGlobalFilter: false,
      }),
    ] as ColumnDef<AppFunction>[];
  }, []);
};

export const useAppFunctionsTableState = (
  functions: AppFunction[],
): AppFunctionsTableState => {
  const [tableInstance, setTableInstance] = useState<Table<AppFunction> | null>(
    null,
  );

  const tagFilterComponent = useMemo(() => {
    const tags = Array.from(
      new Set(functions.flatMap((func) => func.tags || [])),
    ).filter((tag) => tag !== "" && tag !== null);

    if (tags.length === 0 || !tableInstance) return null;

    const tagsColumn = tableInstance.getColumn("tags");
    if (!tagsColumn) return null;

    return (
      <ColumnFilter
        column={tagsColumn}
        options={tags}
        placeholder="Tags"
        defaultLabel="All Tags"
        defaultOption="_all_"
        width="w-[120px]"
      />
    );
  }, [functions, tableInstance]);

  return {
    tableInstance,
    setTableInstance,
    tagFilterComponent,
  };
};
