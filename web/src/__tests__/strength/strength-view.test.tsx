import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { StrengthView } from "@/components/strength/strength-view";
import { ApiError } from "@/lib/api";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/lib/api")>();
  return { ...mod, apiFetch };
});
vi.mock("@/lib/session", () => ({ getAccessToken }));

const item = {
  slot: "push",
  exercise_id: "0025",
  name: "barbell bench press",
  equipment: "barbell",
  gif_url: "https://cdn.example/videos/0025.gif",
  target_weight_kg: null,
  sets: 4,
  reps: 10,
  rpe: 8,
  rest_sec: 90,
};

const plan = {
  id: "sp1",
  goal_kind: "weight_loss",
  weeks: 8,
  frequency: 2,
  level: "intermediate",
  equipment: ["barbell"],
  start_date: "2026-07-13",
  status: "active",
  narrative: null,
  structure: {
    frequency: 2,
    level: "intermediate",
    equipment: ["barbell"],
    blocks: [
      { block: "adaptation", weeks: 2 },
      { block: "hypertrophy", weeks: 4 },
      { block: "strength", weeks: 2 },
    ],
    weeks: [
      {
        week: 1,
        start_date: "2026-07-13",
        block: "adaptation",
        is_deload: false,
        focus: "Groove the movements",
        sessions: [
          { day: 0, focus: "full", title: "Full body A", items: [item] },
          { day: 3, focus: "full", title: "Full body B", items: [item] },
        ],
      },
      {
        week: 2,
        start_date: "2026-07-20",
        block: "adaptation",
        is_deload: false,
        focus: "Groove the movements",
        sessions: [],
      },
    ],
  },
};

describe("StrengthView (M3)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("shows the setup form when no program exists and creates one", async () => {
    apiFetch
      .mockResolvedValueOnce({ plan: null })
      .mockResolvedValueOnce(plan);
    render(<StrengthView />);

    expect(
      await screen.findByRole("button", { name: /generate my program/i }),
    ).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /generate my program/i }));

    expect(await screen.findByText("Full body A")).toBeInTheDocument();
    expect(apiFetch).toHaveBeenLastCalledWith(
      "/strength/plans",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("renders the current program with sessions and prescriptions", async () => {
    apiFetch.mockResolvedValueOnce({ plan });
    render(<StrengthView />);

    expect(await screen.findByText("Full body A")).toBeInTheDocument();
    expect(screen.getAllByText("barbell bench press").length).toBeGreaterThan(0);
    expect(screen.getAllByText(/4 × 10/).length).toBeGreaterThan(0);
    expect(screen.getByText(/hypertrophy/i)).toBeInTheDocument();
  });

  it("upsells when the API says premium is required", async () => {
    apiFetch.mockRejectedValueOnce(new ApiError(402, "premium_required"));
    render(<StrengthView />);
    expect(
      await screen.findByText(/strength programs are premium/i),
    ).toBeInTheDocument();
  });

  it("shows an error state on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<StrengthView />);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
