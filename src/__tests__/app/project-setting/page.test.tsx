import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen } from "@testing-library/react";
import ProjectSettingPage from "@/app/project-setting/page";
import { useProject } from "@/components/context/project";
import { useUser } from "@/components/context/user";
import { getAllApps } from "@/lib/api/app";
import { TooltipProvider } from "@/components/ui/tooltip";

// Mock the modules
vi.mock("@/components/context/project", () => ({
  useProject: vi.fn(),
}));
vi.mock("@/components/context/user", () => ({
  useUser: vi.fn(),
}));
vi.mock("@/lib/api/app");
vi.mock("@/lib/api/util", () => ({
  getApiKey: vi.fn(() => "test-api-key"),
}));

vi.mock("@/components/project/app-edit-form", () => ({
  AppEditForm: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="app-edit-form">{children}</div>
  ),
}));

vi.mock("@/components/project/agent-instruction-filter-form", () => ({
  AgentInstructionFilterForm: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="agent-instruction-form">{children}</div>
  ),
}));

const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <TooltipProvider>{children}</TooltipProvider>
);

describe("ProjectSettingPage", () => {
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
    agents: [
      {
        id: "agent-1",
        name: "Test Agent",
        description: "Test Description",
        project_id: "project-123",
        allowed_apps: [],
        api_keys: [
          {
            id: "key-1",
            key: "test-key-1",
            agent_id: "agent-1",
            status: "active",
            created_at: "2024-01-01",
            updated_at: "2024-01-01",
          },
        ],
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
        custom_instructions: {},
        excluded_apps: [],
        excluded_functions: [],
      },
    ],
  };

  beforeEach(() => {
    vi.clearAllMocks();

    // Mock user context
    const userMock = {
      user: { accessToken: "test-token", userId: "user-1" },
      setUser: vi.fn(),
      signup: vi.fn(),
      login: vi.fn(),
      logout: vi.fn(),
    };
    vi.mocked(useUser).mockReturnValue(userMock);

    // Mock project context
    vi.mocked(useProject).mockReturnValue({
      project: mockProject,
      setProject: vi.fn(),
    });

    // Mock getAllApps
    vi.mocked(getAllApps).mockResolvedValue([
      {
        id: "app-1",
        name: "TEST_APP_1",
        display_name: "Test App 1",
        provider: "test",
        version: "1.0.0",
        description: "Test description",
        categories: ["test"],
        logo: "/test-logo.png",
        visibility: "public",
        active: true,
        security_schemes: [],
        created_at: "2024-01-01",
        updated_at: "2024-01-01",
        functions: [],
      },
    ]);
  });

  it("renders project settings when project is available", () => {
    render(<ProjectSettingPage />, { wrapper: TestWrapper });

    // Check if main title is rendered
    expect(screen.getByText("Project settings")).toBeInTheDocument();

    // Check if project name is displayed
    expect(screen.getByDisplayValue("Test Project")).toBeInTheDocument();

    // Check if project ID is displayed
    expect(screen.getByText("project-123")).toBeInTheDocument();
  });

  it("displays agent information correctly", async () => {
    render(<ProjectSettingPage />, { wrapper: TestWrapper });

    // Check if agent section is rendered
    const agentLabels = screen.getAllByText("Agent");
    expect(agentLabels[0]).toBeInTheDocument();

    const manageAgentsLabels = screen.getAllByText("Add and manage agents");
    expect(manageAgentsLabels[0]).toBeInTheDocument();

    // Check if agent table is rendered with correct data
    const agentNameLabels = screen.getAllByText("Test Agent");
    expect(agentNameLabels[0]).toBeInTheDocument();

    const descriptionLabels = screen.getAllByText("Test Description");
    expect(descriptionLabels[0]).toBeInTheDocument();
  });

  it("loads apps on component mount", () => {
    render(<ProjectSettingPage />, { wrapper: TestWrapper });
    expect(getAllApps).toHaveBeenCalledWith("test-api-key");
  });
});
