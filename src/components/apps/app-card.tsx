"use client";
import Image from "next/image";
import Link from "next/link";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { type App } from "@/lib/types/app";
import { IdDisplay } from "@/components/apps/id-display";

interface AppCardProps {
  app: App;
}

export function AppCard({ app }: AppCardProps) {
  return (
    <Link href={`/apps/${app.id}`} className="block">
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardHeader className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3 min-w-0 flex-1 mr-4">
              <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-lg">
                <Image
                  src={app.logo}
                  alt={`${app.name} logo`}
                  fill
                  className="object-cover"
                />
              </div>
              <CardTitle className="truncate">
                {app.display_name}
              </CardTitle>
            </div>
            <div className="flex-shrink-0 w-20">
              <IdDisplay id={app.id} />
            </div>
          </div>
          <CardDescription>{app.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {app.categories.map((category) => (
              <span
                key={category}
                className="rounded-md bg-gray-100 px-3 py-1 text-sm font-medium text-gray-600 border border-gray-200"
              >
                {category}
              </span>
            ))}
            {/* {app.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600"
              >
                {tag}
              </span>
            ))} */}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
