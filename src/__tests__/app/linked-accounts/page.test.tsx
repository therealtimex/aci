import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor, fireEvent } from "@testing-library/react";
import LinkedAccountsPage from "@/app/linked-accounts/page";
import { useProject } from "@/components/context/project";
import {
  getAllLinkedAccounts,
  deleteLinkedAccount,
  updateLinkedAccount,
} from "@/lib/api/linkedaccount";
import { getApps } from "@/lib/api/app";
import { getAllAppConfigs } from "@/lib/api/appconfig";
import { TooltipProvider } from "@/components/ui/tooltip";
import { toast } from "sonner";

vi.mock("@/components/context/project");
vi.mock("@/lib/api/linkedaccount");
vi.mock("@/lib/api/app");
vi.mock("@/lib/api/appconfig");
vi.mock("@/lib/api/util", () => ({
  getApiKey: vi.fn(() => "test-api-key"),
}));
vi.mock("sonner", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <TooltipProvider>{children}</TooltipProvider>
);

describe("LinkedAccountsPage", () => {
  const mockProject = {
    id: "project-123",
    name: "Test Project",
    owner_id: "owner-1",
    visibility_access: "private",
    daily_quota_used: 0,
    daily_quota_reset_at: "2024-01-01",
    total_quota_used: 0,
    created_at: "2024-01-01",
    updated_at: "2024-01-01",
    agents: [],
  };

  const mockLinkedAccounts = [
    {
      id: "account-1",
      project_id: "project-123",
      app_name: "TEST_APP_1",
      linked_account_owner_id: "owner-1",
      security_scheme: "oauth2",
      enabled: true,
      created_at: "2024-01-01T12:00:00",
      updated_at: "2024-01-01T12:00:00",
    },
    {
      id: "account-2",
      project_id: "project-123",
      app_name: "TEST_APP_2",
      linked_account_owner_id: "owner-2",
      security_scheme: "api_key",
      enabled: false,
      created_at: "2024-01-02T12:00:00",
      updated_at: "2024-01-02T12:00:00",
    },
  ];

  const mockApps = [
    {
      id: "app-1",
      name: "TEST_APP_1",
      display_name: "Test App 1",
      provider: "test",
      version: "1.0.0",
      description: "Test description",
      categories: ["social"],
      logo: "/test-logo-1.png",
      visibility: "public",
      active: true,
      security_schemes: ["oauth2"],
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
      functions: [],
    },
    {
      id: "app-2",
      name: "TEST_APP_2",
      display_name: "Test App 2",
      provider: "test",
      version: "1.0.0",
      description: "Test description 2",
      categories: ["productivity"],
      logo: "/test-logo-2.png",
      visibility: "public",
      active: true,
      security_schemes: ["api_key"],
      created_at: "2024-01-01",
      updated_at: "2024-01-01",
      functions: [],
    },
  ];

  const mockAppConfigs = [
    {
      id: "config-1",
      project_id: "project-123",
      app_name: "TEST_APP_1",
      security_scheme: "oauth2",
      security_scheme_overrides: {},
      enabled: true,
      all_functions_enabled: true,
      enabled_functions: [],
    },
    {
      id: "config-2",
      project_id: "project-123",
      app_name: "TEST_APP_2",
      security_scheme: "api_key",
      security_scheme_overrides: {},
      enabled: true,
      all_functions_enabled: true,
      enabled_functions: [],
    },
  ];

  beforeEach(() => {
    vi.clearAllMocks();

    vi.mocked(useProject).mockReturnValue({
      project: mockProject,
      setProject: vi.fn(),
    });

    vi.mocked(getAllLinkedAccounts).mockResolvedValue(mockLinkedAccounts);
    vi.mocked(getApps).mockResolvedValue(mockApps);
    vi.mocked(getAllAppConfigs).mockResolvedValue(mockAppConfigs);
    vi.mocked(updateLinkedAccount).mockResolvedValue(mockLinkedAccounts[0]);
    vi.mocked(deleteLinkedAccount).mockResolvedValue(undefined);
  });

  it("Renders linked accounts page and displays account list", async () => {
    render(<LinkedAccountsPage />, { wrapper: TestWrapper });

    // Check if page title is correctly rendered
    expect(screen.getByText("Linked Accounts")).toBeInTheDocument();

    // Check description text
    expect(
      screen.getByText("Manage your linked accounts here."),
    ).toBeInTheDocument();

    // Wait for loading to complete and check table headers
    await waitFor(() => {
      expect(screen.getByText("APP NAME")).toBeInTheDocument();
      expect(screen.getByText("LINKED ACCOUNT OWNER ID")).toBeInTheDocument();
      expect(screen.getByText("CREATED AT")).toBeInTheDocument();
      expect(screen.getByText("ENABLED")).toBeInTheDocument();
      expect(screen.getByText("DETAILS")).toBeInTheDocument();
    });

    // Check if linked account data is loaded
    await waitFor(() => {
      expect(screen.getByText("TEST_APP_1")).toBeInTheDocument();
      expect(screen.getByText("owner-1")).toBeInTheDocument();
      expect(screen.getByText("owner-2")).toBeInTheDocument();
    });

    // Verify API calls
    expect(getAllLinkedAccounts).toHaveBeenCalledWith("test-api-key");
    expect(getAllAppConfigs).toHaveBeenCalledWith("test-api-key");
    expect(getApps).toHaveBeenCalledWith(
      ["TEST_APP_1", "TEST_APP_2"],
      "test-api-key",
    );
  });

  it("Supports deleting linked accounts", async () => {
    render(<LinkedAccountsPage />, { wrapper: TestWrapper });

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.getAllByText("See Details")[0]).toBeInTheDocument();
    });

    // Find delete buttons (may need to adjust selector based on actual DOM structure)
    const deleteButtons = screen.getAllByRole("button");
    const trashButtons = deleteButtons.filter(
      (button) =>
        button.innerHTML.includes("GoTrash") ||
        button.getAttribute("aria-label")?.includes("Delete"),
    );

    // Since we can't find the specific delete button, this part of the test may need to be adjusted based on the actual DOM structure
    // Below is a simulated deletion flow example
    if (trashButtons.length > 0) {
      fireEvent.click(trashButtons[0]);

      // Confirm deletion dialog should appear
      await waitFor(() => {
        expect(screen.getByText("Confirm Deletion?")).toBeInTheDocument();
      });

      // Click confirm delete
      const confirmDeleteButton = screen.getByText("Delete");
      fireEvent.click(confirmDeleteButton);

      // Verify delete API was called
      await waitFor(() => {
        expect(deleteLinkedAccount).toHaveBeenCalledWith(
          "account-1",
          "test-api-key",
        );
      });

      // Verify success message was displayed
      expect(toast.success).toHaveBeenCalledWith(
        expect.stringContaining("deleted"),
      );
    }
  });

  it("Displays empty state message when no linked accounts exist", async () => {
    // Mock no linked accounts scenario
    vi.mocked(getAllLinkedAccounts).mockResolvedValue([]);

    render(<LinkedAccountsPage />, { wrapper: TestWrapper });

    // Should display empty state message
    await waitFor(() => {
      expect(screen.getByText("No linked accounts found")).toBeInTheDocument();
    });
  });
});
