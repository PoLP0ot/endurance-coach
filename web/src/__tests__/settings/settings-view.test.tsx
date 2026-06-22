import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SettingsView } from "@/components/settings/settings-view";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

const profile = {
  id: "u1",
  email: "a@b.com",
  display_name: "Sam",
  primary_goal: "marathon",
  units: "metric",
  weekly_email_opt_in: true,
  onboarding_complete: true,
  subscription_status: "free",
};

beforeEach(() => {
  vi.clearAllMocks();
  getAccessToken.mockResolvedValue("jwt");
});

describe("SettingsView (US11a)", () => {
  it("loads the profile and saves edits", async () => {
    apiFetch
      .mockResolvedValueOnce(profile)
      .mockResolvedValueOnce({ ...profile, display_name: "Sammy" });
    render(<SettingsView />);

    const name = await screen.findByLabelText(/display name/i);
    expect(name).toHaveValue("Sam");
    fireEvent.change(name, { target: { value: "Sammy" } });
    fireEvent.click(screen.getByRole("button", { name: /save changes/i }));

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/profile",
        expect.objectContaining({ method: "PATCH" }),
      ),
    );
  });

  it("links to subscription and privacy", async () => {
    apiFetch.mockResolvedValueOnce(profile);
    render(<SettingsView />);
    expect(
      await screen.findByRole("link", { name: /subscription/i }),
    ).toHaveAttribute("href", "/settings/subscription");
    expect(screen.getByRole("link", { name: /privacy/i })).toHaveAttribute(
      "href",
      "/settings/privacy",
    );
  });

  it("shows an error state on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<SettingsView />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /couldn't load your settings/i,
    );
  });
});
