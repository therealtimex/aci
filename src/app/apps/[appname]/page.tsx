import React from "react";
import { AppFunctionsTable } from "@/components/apps/app-functions-table";
import { type AppFunction } from "@/lib/dummy-data";

const dummyFunctions: AppFunction[] = [
  {
    id: "1",
    name: "Function One",
    functionId: "func_001",
    description: "This is the first function.",
  },
  {
    id: "2",
    name: "Function Two",
    functionId: "func_002",
    description: "This is the second function.",
  },
];

const AppPage = () => {
  return (
    <div>
      <h1>App Functions</h1>
      <AppFunctionsTable functions={dummyFunctions} />
    </div>
  );
};

export default AppPage;
