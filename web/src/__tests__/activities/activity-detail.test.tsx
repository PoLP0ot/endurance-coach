import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ActivityDetail } from "@/components/activities/activity-detail";
import { ApiError } from "@/lib/api";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch };
});
vi.mock("@/lib/session", () => ({ getAccessToken }));

const detail = {
  id: "a1",
  activity_type: "running",
  name: "Long Run",
  start_time: "2026-06-20T07:00:00+00:00",
  distance_m: 20000,
  duration_s: 7200,
  avg_hr: 145,
  max_hr: 165,
  elevation_gain_m: 200,
  avg_power_w: null,
  tss: 130,
  streams: null,
};

describe("ActivityDetail (US3)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("shows metrics and generates an analysis", async () => {
    apiFetch.mockResolvedValueOnce(detail).mockResolvedValueOnce({
      activity_id: "a1",
      model: "stub",
      facts: { tss: 130 },
      narrative: "A strong aerobic builder.",
      prompt_version: "v1",
    });
    render(<ActivityDetail id="a1" />);

    expect(await screen.findByText("Long Run")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /analyze with coach/i }));
    expect(await screen.findByText(/strong aerobic builder/i)).toBeInTheDocument();
  });

  it("prompts to upgrade when analysis is premium-gated (402)", async () => {
    apiFetch
      .mockResolvedValueOnce(detail)
      .mockRejectedValueOnce(new ApiError(402, "premium_required"));
    render(<ActivityDetail id="a1" />);

    expect(await screen.findByText("Long Run")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /analyze with coach/i }));
    expect(
      await screen.findByRole("link", { name: /upgrade to premium/i }),
    ).toBeInTheDocument();
  });
});
