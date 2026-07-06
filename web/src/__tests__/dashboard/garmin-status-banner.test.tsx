import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { GarminStatusBanner } from "@/components/dashboard/garmin-status-banner";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

describe("GarminStatusBanner (S6)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("prompts to reconnect when the Garmin token expired", async () => {
    apiFetch.mockResolvedValueOnce({ status: "auth_expired", last_sync_at: null });
    render(<GarminStatusBanner />);
    expect(
      await screen.findByText(/garmin connection has expired/i),
    ).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /reconnect garmin/i }),
    ).toHaveAttribute("href", "/onboarding");
  });

  it("renders nothing while connected", async () => {
    apiFetch.mockResolvedValueOnce({
      status: "connected",
      last_sync_at: "2026-07-05T07:00:00Z",
    });
    const { container } = render(<GarminStatusBanner />);
    await vi.waitFor(() => expect(apiFetch).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });

  it("renders nothing when the status call fails", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    const { container } = render(<GarminStatusBanner />);
    await vi.waitFor(() => expect(apiFetch).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });
});
