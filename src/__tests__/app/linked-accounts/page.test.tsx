import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import LinkedAccountsPage from "@/app/linked-accounts/page";

describe("LinkedAccountsPage", () => {
  it("renders the linked accounts page correctly", () => {
    render(<LinkedAccountsPage />);

    // Check if the title is rendered
    expect(screen.getByText("Linked Accounts")).toBeInTheDocument();

    // Check if the description is rendered
    expect(
      screen.getByText("Manage your linked accounts and integrations here."),
    ).toBeInTheDocument();
  });
});
