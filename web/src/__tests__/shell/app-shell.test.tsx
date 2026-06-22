import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { AppShell } from "@/components/shell/app-shell";

const { push, usePathname, signOut } = vi.hoisted(() => ({
  push: vi.fn(),
  usePathname: vi.fn(),
  signOut: vi.fn(),
}));

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push }),
  usePathname: () => usePathname(),
}));
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { signOut } }),
}));

describe("AppShell (US10)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    usePathname.mockReturnValue("/dashboard");
    signOut.mockResolvedValue({ error: null });
  });

  it("renders the four primary nav destinations", () => {
    render(<AppShell>content</AppShell>);
    for (const label of ["Progress", "Coach", "Plan", "Settings"]) {
      const links = screen.getAllByRole("link", {
        name: new RegExp(`^${label}$`, "i"),
      });
      expect(links.length).toBeGreaterThan(0);
      expect(links[0]).toHaveAttribute(
        "href",
        label === "Progress" ? "/dashboard" : `/${label.toLowerCase()}`,
      );
    }
  });

  it("renders its children", () => {
    render(<AppShell>page body</AppShell>);
    expect(screen.getByText("page body")).toBeInTheDocument();
  });

  it("marks the active route with aria-current", () => {
    usePathname.mockReturnValue("/coach");
    render(<AppShell>content</AppShell>);
    const active = screen
      .getAllByRole("link", { name: /coach/i })
      .filter((el) => el.getAttribute("aria-current") === "page");
    expect(active.length).toBeGreaterThan(0);
  });

  it("signs out and redirects to login", async () => {
    render(<AppShell>content</AppShell>);
    fireEvent.click(screen.getAllByRole("button", { name: /sign out/i })[0]);
    await waitFor(() => expect(signOut).toHaveBeenCalled());
    await waitFor(() => expect(push).toHaveBeenCalledWith("/login"));
  });
});
