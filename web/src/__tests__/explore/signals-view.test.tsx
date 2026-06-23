import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SignalsView } from "@/components/explore/signals-view";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

const payload = {
  signals: [
    {
      key: "fitness",
      eyebrow: "Fitness · CTL trend",
      question: "How is my fitness trending?",
      points: [50, 51, 52, 53],
      color: "text-primary",
      interpretation: "You're building well.",
    },
    {
      key: "recovery",
      eyebrow: "Recovery · today",
      question: "Am I recovered enough to push?",
      points: null,
      color: "text-accent",
      interpretation: "Recovery is strong at 74/100.",
    },
  ],
};

describe("SignalsView (2.3)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders signal questions and coach answers from /signals", async () => {
    apiFetch.mockResolvedValueOnce(payload);
    render(<SignalsView />);
    expect(
      await screen.findByText("How is my fitness trending?"),
    ).toBeInTheDocument();
    expect(screen.getByText("You're building well.")).toBeInTheDocument();
    expect(screen.getByText(/recovery is strong/i)).toBeInTheDocument();
    expect(apiFetch).toHaveBeenCalledWith("/signals", { token: "jwt" });
  });

  it("shows an empty state when there are no signals", async () => {
    apiFetch.mockResolvedValueOnce({ signals: [] });
    render(<SignalsView />);
    expect(await screen.findByText(/no signals yet/i)).toBeInTheDocument();
  });

  it("shows an error state on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<SignalsView />);
    expect(await screen.findByText(/couldn't load your signals/i)).toBeInTheDocument();
  });
});
