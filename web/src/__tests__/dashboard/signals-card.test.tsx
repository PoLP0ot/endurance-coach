import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SignalsCard } from "@/components/dashboard/signals-card";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

const signals = [
  {
    key: "fitness",
    eyebrow: "Fitness · CTL trend",
    question: "How is my fitness trending?",
    points: [1, 2, 3],
    color: null,
    interpretation: "Fitness is climbing steadily.",
  },
];

describe("SignalsCard", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders each signal as a question with the coach's read", async () => {
    apiFetch.mockResolvedValueOnce({ signals });
    render(<SignalsCard />);
    expect(
      await screen.findByText("How is my fitness trending?"),
    ).toBeInTheDocument();
    expect(screen.getByText(/climbing steadily/i)).toBeInTheDocument();
  });

  it("renders nothing when signals fail to load", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    const { container } = render(<SignalsCard />);
    await vi.waitFor(() => expect(apiFetch).toHaveBeenCalled());
    expect(container).toBeEmptyDOMElement();
  });
});
