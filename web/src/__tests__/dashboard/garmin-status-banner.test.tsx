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
      last_sync_at: new Date().toISOString(),
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

describe("GarminStatusBanner stale sync nudge", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("nudges to sync when the last sync is days old", async () => {
    const old = new Date(Date.now() - 5 * 86400000).toISOString();
    apiFetch.mockResolvedValueOnce({ status: "connected", last_sync_at: old });
    render(<GarminStatusBanner />);
    expect(await screen.findByText(/last sync was 5 days ago/i)).toBeInTheDocument();
  });

  it("starts a sync from the nudge", async () => {
    const old = new Date(Date.now() - 4 * 86400000).toISOString();
    apiFetch
      .mockResolvedValueOnce({ status: "connected", last_sync_at: old })
      .mockResolvedValueOnce({ job_id: "j1" });
    render(<GarminStatusBanner />);
    const { fireEvent } = await import("@testing-library/react");
    fireEvent.click(await screen.findByRole("button", { name: /sync now/i }));
    expect(await screen.findByText(/sync started/i)).toBeInTheDocument();
    expect(apiFetch).toHaveBeenLastCalledWith(
      "/garmin/sync",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
