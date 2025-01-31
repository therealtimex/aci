"use client";

import React from "react";
import { useUser } from "@/components/context/user";
import { Button } from "@/components/ui/button";

const Protected = ({ children }: Readonly<{ children: React.ReactNode }>) => {
  // TODO: make this loads faster
  const { user, login } = useUser();

  return (
    <>
      {user ? (
        <div>{children}</div>
      ) : (
        <div className="w-full flex flex-col items-center justify-center h-screen">
          {/* TODO: logo */}
          <h1 className="text-2xl font-bold">Authentication required</h1>
          <p className="mb-4">Please log in to access this page</p>
          <Button onClick={login}>Log in</Button>
        </div>
      )}
    </>
  );
};

export default Protected;
