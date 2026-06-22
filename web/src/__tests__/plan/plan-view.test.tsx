import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { PlanView } from "@/components/plan/plan-view";
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

const plan = {
  id: "p1",
  goal: "marathon",
  weeks: 12,
  start_date: "2026-07-01",
  status: "active",
  structure: {
    goal: "marathon",
    weeks: [
      {
        week: 1,
        start_date: "2026-07-01",
        phase: "base",
        is_recovery: false,
        target_tss: 300,
        focus: "Aerobic base + easy mileage",
      },
    ],
  },
  narrative: "Build your base, then sharpen.",
  model: "stub",
};

beforeEach(() => {
  vi.clearAllMocks();
  getAccessToken.mockResolvedValue("jwt");
});

describe("PlanView (US5)", () => {
  it("generates a plan and renders the timeline", async () => {
    apiFetch
      .mockResolvedValueOnce({ plan: null })
      .mockResolvedValueOnce(plan);
    render(<PlanView />);

    expect(await screen.findByText(/build your plan/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /generate plan/i }));

    expect(await screen.findByText(/build your base, then sharpen/i)).toBeInTheDocument();
    expect(screen.getByText("Week 1")).toBeInTheDocument();
    expect(screen.getByText("Aerobic base + easy mileage")).toBeInTheDocument();
  });

  it("shows the active plan on load", async () => {
    apiFetch.mockResolvedValueOnce({ plan });
    render(<PlanView />);
    expect(await screen.findByText("Week 1")).toBeInTheDocument();
    expect(screen.getByText(/regenerate your plan/i)).toBeInTheDocument();
  });

  it("prompts to upgrade when plans are gated (402)", async () => {
    apiFetch.mockRejectedValueOnce(new ApiError(402, "premium_required"));
    render(<PlanView />);
    expect(await screen.findByText(/training plans are premium/i)).toBeInTheDocument();
  });
});
