import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { CoachOnboard } from "@/components/onboarding/coach-onboard";

const { apiFetch, getAccessToken, push } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
  push: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));

describe("CoachOnboard (A15)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
    apiFetch.mockResolvedValue({});
  });

  it("collects goal then metadata and persists goal_params", async () => {
    render(<CoachOnboard />);

    fireEvent.click(screen.getByRole("button", { name: "Marathon" }));
    // First PATCH stores the goal kind.
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/profile",
        expect.objectContaining({ method: "PATCH" }),
      ),
    );
    // Metadata prompt appears.
    expect(await screen.findByText(/finish time/i)).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Sub-3:30" }));

    await waitFor(() => {
      const goalParamsCall = apiFetch.mock.calls.find(
        ([, opts]) =>
          typeof opts?.body === "string" && opts.body.includes("target_time_s"),
      );
      expect(goalParamsCall).toBeTruthy();
      expect(JSON.parse(goalParamsCall![1].body).goal_params.target_time_s).toBe(12600);
    });
    expect(screen.getByRole("button", { name: /let's go/i })).toBeInTheDocument();
  });

  it("goes straight to done for goals without metadata (triathlon)", async () => {
    render(<CoachOnboard />);
    fireEvent.click(screen.getByRole("button", { name: "Triathlon" }));
    expect(await screen.findByRole("button", { name: /let's go/i })).toBeInTheDocument();
  });
});

describe("CoachOnboard weight-loss discovery (audit 2.2/2.3)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
    apiFetch.mockResolvedValue({});
  });

  it("asks weight, deadline and weekly availability, then saves all params", async () => {
    render(<CoachOnboard />);
    fireEvent.click(screen.getByRole("button", { name: /weight loss/i }));

    fireEvent.change(await screen.findByLabelText(/target weight/i), {
      target: { value: "80" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    fireEvent.change(await screen.findByLabelText(/target date/i), {
      target: { value: "2026-12-31" },
    });
    fireEvent.click(screen.getByRole("button", { name: /save/i }));

    fireEvent.click(await screen.findByRole("button", { name: /4 days/i }));

    await screen.findByRole("button", { name: /let's go/i });
    const paramsCall = apiFetch.mock.calls.find(
      ([, opts]) =>
        typeof opts?.body === "string" && opts.body.includes("goal_params"),
    );
    const body = JSON.parse(paramsCall![1].body);
    expect(body.goal_params).toEqual({
      target_weight_kg: 80,
      target_date: "2026-12-31",
      weekly_activity_target: 4,
    });
  });
});
