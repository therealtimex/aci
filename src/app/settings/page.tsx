"use client";

import { Button } from "@/components/ui/button";
import { useUser } from "@/components/context/user";

export default function SettingsPage() {
  const { logout } = useUser();
  return (
    <div className="container mx-auto p-6 space-y-4">
      <h1 className="text-2xl font-bold">Account Settings</h1>
      <p className="text-muted-foreground">
        Manage your account settings and preferences here.
      </p>
      <Button variant="destructive" onClick={logout}>
        Log Out
      </Button>
    </div>
  );
}
