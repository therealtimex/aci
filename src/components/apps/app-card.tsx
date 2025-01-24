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
import { type App } from "@/lib/dummy-data";

interface AppCardProps {
  app: App;
  projectName: string;
}

export function AppCard({ app, projectName }: AppCardProps) {
  return (
    <Link href={`/${projectName}/apps/${app.id}`} className="block">
      <Card className="h-full transition-shadow hover:shadow-lg">
        <CardHeader className="space-y-4">
          <div className="flex items-center gap-4">
            <div className="relative h-12 w-12 overflow-hidden rounded-lg">
              <Image
                src={app.icon}
                alt={`${app.name} icon`}
                fill
                className="object-cover"
              />
            </div>
            <CardTitle>{app.name}</CardTitle>
          </div>
          <CardDescription>{app.description}</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-2">
            {app.categories.map((category) => (
              <span
                key={category}
                className="rounded-full bg-gray-100 px-2.5 py-0.5 text-xs font-medium text-gray-600"
              >
                {category}
              </span>
            ))}
            {app.tags.map((tag) => (
              <span
                key={tag}
                className="rounded-full bg-blue-50 px-2.5 py-0.5 text-xs font-medium text-blue-600"
              >
                {tag}
              </span>
            ))}
          </div>
        </CardContent>
      </Card>
    </Link>
  );
}
