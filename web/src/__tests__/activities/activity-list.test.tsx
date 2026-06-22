import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ActivityList } from "@/components/activities/activity-list";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

const row = (id: string) => ({
  id,
  activity_type: "running",
  name: `Run ${id}`,
  start_time: "2026-06-20T07:00:00+00:00",
  distance_m: 10000,
  duration_s: 3600,
  avg_hr: 150,
  tss: 70,
});

describe("ActivityList (US9)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders activities and loads more pages", async () => {
    apiFetch
      .mockResolvedValueOnce({ items: [row("1")], next_cursor: "c1", windowed: true })
      .mockResolvedValueOnce({ items: [row("2")], next_cursor: null, windowed: true });
    render(<ActivityList />);

    expect(await screen.findByText("Run 1")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /load more/i }));
    expect(await screen.findByText("Run 2")).toBeInTheDocument();
    expect(screen.getByText("Run 1")).toBeInTheDocument();
    await waitFor(() =>
      expect(
        screen.queryByRole("button", { name: /load more/i }),
      ).not.toBeInTheDocument(),
    );
  });

  it("shows an empty state when there are no activities", async () => {
    apiFetch.mockResolvedValueOnce({
      items: [],
      next_cursor: null,
      windowed: true,
    });
    render(<ActivityList />);
    expect(await screen.findByText(/no activities yet/i)).toBeInTheDocument();
  });

  it("shows an error state on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<ActivityList />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /couldn't load your activities/i,
    );
  });
});
