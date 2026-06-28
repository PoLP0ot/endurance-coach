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
