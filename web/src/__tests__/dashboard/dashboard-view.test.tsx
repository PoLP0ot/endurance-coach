import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { DashboardView } from "@/components/dashboard/dashboard-view";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
// Recharts needs layout; stub the chart so jsdom stays quiet.
vi.mock("@/components/dashboard/training-load-chart", () => ({
  TrainingLoadChart: () => <div data-testid="chart" />,
}));

const payload = {
  fitness: { ctl: 42, atl: 55, tsb: -13 },
  form: {
    band: "productive",
    headline: "You're in the productive training zone.",
    detail: "Fatigue is elevated but this is where fitness is built.",
  },
  recovery: 64,
  load_series: [{ date: "2026-06-01", ctl: 1, atl: 1, tsb: 0 }],
  totals: { activity_count: 12, total_distance_m: 84000, window_days: 42 },
  latest_activity: null,
};

describe("DashboardView (US2)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("shows a loading state then the coach note and metrics", async () => {
    apiFetch.mockResolvedValueOnce(payload);
    render(<DashboardView />);
    expect(screen.getByRole("status")).toHaveAttribute("aria-busy", "true");
    expect(
      await screen.findByText(/productive training zone/i),
    ).toBeInTheDocument();
    expect(screen.getByText("42")).toBeInTheDocument(); // CTL
    expect(screen.getByText("64")).toBeInTheDocument(); // recovery
    expect(screen.getByText(/12 activities/i)).toBeInTheDocument();
  });

  it("renders an empty state when there is no data", async () => {
    apiFetch.mockResolvedValueOnce({
      ...payload,
      totals: { activity_count: 0, total_distance_m: 0, window_days: 42 },
    });
    render(<DashboardView />);
    expect(await screen.findByText(/no training data yet/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /connect garmin/i }),
    ).toHaveAttribute("href", "/onboarding");
  });

  it("renders an error state with retry on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<DashboardView />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /couldn't load your dashboard/i,
    );
  });
});
