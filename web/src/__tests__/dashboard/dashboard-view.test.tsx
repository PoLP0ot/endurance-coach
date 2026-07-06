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

const emptyWeek = { activity_count: 0, distance_m: 0, tss: 0, duration_s: 0 };
const payload = {
  goal: null,
  goal_structured: {
    kind: "marathon",
    label: "Race time",
    on_track_band: "on_track",
    headline: "Projected finish 3:28:00",
    projection: "3:28:00",
    target: "3:30:00",
    eta: null,
  },
  goal_variant: {
    kind: "marathon",
    panels: [
      { label: "Fitness", value: 62, unit: "CTL", hint: "42-day load" },
      { label: "Form", value: -9, unit: "TSB", hint: "balance" },
    ],
  },
  this_week: {
    this_week: { activity_count: 4, distance_m: 42000, tss: 240, duration_s: 14400 },
    last_week: emptyWeek,
    week_start: "2026-06-22",
  },
  health: null,
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

  it("renders the goal progress band and dedupes goal panels", async () => {
    apiFetch.mockResolvedValueOnce(payload);
    render(<DashboardView />);
    expect(await screen.findByText("On track")).toBeInTheDocument();
    expect(screen.getByText(/Projected finish 3:28:00/i)).toBeInTheDocument();
    // "Fitness"/"Form" goal panels duplicate the core grid — shown once only.
    expect(screen.getAllByText("Fitness")).toHaveLength(1);
    expect(screen.getAllByText("Form")).toHaveLength(1);
  });

  it("appends goal-unique panels to the metric grid", async () => {
    apiFetch.mockResolvedValueOnce({
      ...payload,
      goal_variant: {
        kind: "marathon",
        panels: [
          { label: "Fitness", value: 62, unit: "CTL", hint: "42-day load" },
          { label: "Threshold pace", value: "4:24/km", unit: "", hint: "best recent run" },
        ],
      },
    });
    render(<DashboardView />);
    expect(await screen.findByText("Threshold pace")).toBeInTheDocument();
    expect(screen.getAllByText("Fitness")).toHaveLength(1);
  });

  it("shows the goal banner and this-week table when present", async () => {
    apiFetch.mockResolvedValueOnce({
      ...payload,
      goal: {
        race_name: "Paris Marathon",
        race_date: "2026-09-14",
        days_to_go: 82,
        weeks_to_go: 12,
        progress_pct: 52,
        is_past: false,
      },
    });
    render(<DashboardView />);
    expect(await screen.findByText("Paris Marathon")).toBeInTheDocument();
    expect(screen.getByText(/12 weeks to go/i)).toBeInTheDocument();
    expect(screen.getByText(/This Week at a Glance/i)).toBeInTheDocument();
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
