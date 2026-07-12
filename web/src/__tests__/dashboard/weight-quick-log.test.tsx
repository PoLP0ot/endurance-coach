import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { WeightQuickLog } from "@/components/dashboard/weight-quick-log";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

describe("WeightQuickLog (audit P0)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("logs today's weight and confirms", async () => {
    apiFetch.mockResolvedValueOnce({ day: "2026-07-12", weight_kg: 88.5 });
    const onLogged = vi.fn();
    render(<WeightQuickLog onLogged={onLogged} />);

    fireEvent.change(screen.getByLabelText(/today's weight/i), {
      target: { value: "88.5" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log/i }));

    expect(await screen.findByText(/logged/i)).toBeInTheDocument();
    expect(apiFetch).toHaveBeenCalledWith(
      "/profile/weight",
      expect.objectContaining({ method: "POST" }),
    );
    expect(onLogged).toHaveBeenCalled();
  });

  it("shows an error when saving fails", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<WeightQuickLog />);
    fireEvent.change(screen.getByLabelText(/today's weight/i), {
      target: { value: "88.5" },
    });
    fireEvent.click(screen.getByRole("button", { name: /log/i }));
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
