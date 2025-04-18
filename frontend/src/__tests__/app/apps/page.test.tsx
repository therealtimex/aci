import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import AppStorePage from "@/app/apps/page";
import { getAllApps } from "@/lib/api/app";
import { useMetaInfo } from "@/components/context/metainfo";
import { OrgMemberInfoClass } from "@propelauth/react";
import { Project } from "@/lib/types/project";

// Mock the modules
vi.mock("@/components/context/metainfo", () => ({
  useMetaInfo: vi.fn(),
}));
vi.mock("@/lib/api/app");
vi.mock("@/lib/api/util", () => ({
  getApiKey: vi.fn(() => "test-api-key"),
}));

describe("AppStorePage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("loads and displays apps when project is available", async () => {
    // Mock the MetaInfo context - Changed
    vi.mocked(useMetaInfo).mockReturnValue({
      activeProject: {
        id: "123",
        name: "Test Project",
        owner_id: "owner-1",
        visibility_access: "private",
        daily_quota_used: 0,
        daily_quota_reset_at: "2024-01-01",
        total_quota_used: 0,
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
        agents: [],
      },
      accessToken: "test-token",
      // Add other required fields from MetaInfoContextType with dummy values
      reloadActiveProject: vi.fn(),
      setActiveProject: vi.fn(),
      orgs: [],
      activeOrg: {
        orgId: "org-123",
        orgName: "Test Org",
      } as OrgMemberInfoClass,
      setActiveOrg: vi.fn(),
      projects: [
        {
          id: "123",
          name: "Test Project",
          owner_id: "owner-1",
          visibility_access: "private",
          daily_quota_used: 0,
          daily_quota_reset_at: "2024-01-01",
          total_quota_used: 0,
          created_at: "2024-01-01",
          updated_at: "2024-01-01",
          agents: [],
        } as Project,
      ],
    });

    // Mock the getAllApps response with complete app properties
    const mockApps = [
      {
        id: "1",
        name: "TEST_APP_1",
        display_name: "Test App 1",
        provider: "test",
        version: "1.0.0",
        description: "Test description",
        categories: ["test"],
        logo: "/test.png",
        visibility: "public",
        active: true,
        security_schemes: [],
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
        functions: [],
      },
    ];
    vi.mocked(getAllApps).mockResolvedValue(mockApps);

    render(<AppStorePage />);

    expect(screen.getByText("App Store")).toBeInTheDocument();

    expect(
      screen.getByText("Browse and connect with your favorite apps and tools."),
    ).toBeInTheDocument();

    // Wait for and verify that the test app is displayed
    await waitFor(() => {
      expect(screen.getByText("TEST_APP_1")).toBeInTheDocument();
    });

    // Verify that getAllApps was called
    expect(getAllApps).toHaveBeenCalledWith("test-api-key");
  });
});
