import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { BriefCard } from "@/components/dashboard/brief-card";
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

const fallback = {
  headline: "You're absorbing the load well",
  detail: "Fitness is climbing steadily.",
};

describe("BriefCard (S4)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("shows the daily brief for premium users", async () => {
    apiFetch.mockResolvedValueOnce({
      day: "2026-07-06",
      headline: "Big session day",
      body: "Yesterday's easy run set you up — today the intervals count.",
      prescription: null,
      model: "gpt-4o-mini",
    });
    render(<BriefCard fallback={fallback} />);
    expect(await screen.findByText("Big session day")).toBeInTheDocument();
    expect(screen.getByText(/today the intervals count/i)).toBeInTheDocument();
    expect(screen.getByText(/coach's brief/i)).toBeInTheDocument();
    // The weekly assessment is replaced, not duplicated.
    expect(screen.queryByText(/coach's assessment/i)).not.toBeInTheDocument();
  });

  it("falls back to the weekly assessment when the brief is gated (402)", async () => {
    apiFetch.mockRejectedValueOnce(new ApiError(402, "premium_required"));
    render(<BriefCard fallback={fallback} />);
    expect(
      await screen.findByText(/absorbing the load well/i),
    ).toBeInTheDocument();
    expect(screen.getByText(/coach's assessment/i)).toBeInTheDocument();
  });
});
