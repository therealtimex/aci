import { AppGrid } from "@/components/apps/app-grid";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";
import { dummyApps } from "@/lib/dummy-data";

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

      <div className="m-4 flex items-center gap-2">
        <Select>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            <SelectItem value="productivity">Productivity</SelectItem>
            <SelectItem value="communication">Communication</SelectItem>
            <SelectItem value="development">Development</SelectItem>
          </SelectContent>
        </Select>

        <Select>
          <SelectTrigger className="w-[80px]">
            <SelectValue placeholder="Tags" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tags</SelectItem>
            <SelectItem value="ai">AI</SelectItem>
            <SelectItem value="automation">Automation</SelectItem>
            <SelectItem value="integration">Integration</SelectItem>
          </SelectContent>
        </Select>
      </div>

      <Separator />

      <div className="m-4">
        <AppGrid apps={dummyApps} />
      </div>
    </div>
  );
}
