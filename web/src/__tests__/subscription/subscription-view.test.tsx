import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SubscriptionView } from "@/components/subscription/subscription-view";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
vi.mock("sonner", () => ({ toast: { info: vi.fn(), error: vi.fn() } }));

beforeEach(() => {
  vi.clearAllMocks();
  getAccessToken.mockResolvedValue("jwt");
});

describe("SubscriptionView (US8)", () => {
  it("shows premium state for subscribers", async () => {
    apiFetch.mockResolvedValueOnce({
      status: "active",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
    });
    render(<SubscriptionView />);
    expect(await screen.findByText(/you're on premium/i)).toBeInTheDocument();
  });

  it("offers an upgrade and starts checkout for free users", async () => {
    apiFetch
      .mockResolvedValueOnce({
        status: "free",
        is_premium: false,
        current_period_end: null,
      })
      .mockResolvedValueOnce({
        client_token: "tok",
        price_id: "pri_1",
        environment: "sandbox",
        customer_email: "a@b.com",
        custom_data: { user_id: "u1" },
      });
    render(<SubscriptionView />);

    fireEvent.click(await screen.findByRole("button", { name: /upgrade to premium/i }));
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/subscription/checkout",
        expect.objectContaining({ method: "POST" }),
      ),
    );
  });
});
