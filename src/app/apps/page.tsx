"use client";

import { AppGrid } from "@/components/apps/app-grid";

import { Separator } from "@/components/ui/separator";
import { dummyApps } from "@/lib/dummyData";

export default function AppStorePage() {
  return (
    <div>
      <div className="m-4">
        <h1 className="text-2xl font-bold">App Store</h1>
        <p className="text-sm text-muted-foreground">
          Browse and connect with your favorite apps and tools.
        </p>
      </div>
      <Separator />

      {/* TODO: fetch Apps from backend */}
      <div className="m-4">
        <AppGrid apps={dummyApps} />
      </div>
    </div>
  );
}
