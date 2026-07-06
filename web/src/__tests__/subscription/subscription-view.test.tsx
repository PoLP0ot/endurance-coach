import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SubscriptionView } from "@/components/subscription/subscription-view";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
vi.mock("sonner", () => ({
  toast: { info: vi.fn(), error: vi.fn(), success: vi.fn() },
}));

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

  it("cancels at period end after confirmation", async () => {
    apiFetch
      .mockResolvedValueOnce({
        status: "active",
        is_premium: true,
        current_period_end: "2026-12-31T00:00:00+00:00",
        cancel_at_period_end: false,
      })
      .mockResolvedValueOnce({
        status: "active",
        cancel_at_period_end: true,
        current_period_end: "2026-12-31T00:00:00+00:00",
      });
    render(<SubscriptionView />);

    fireEvent.click(
      await screen.findByRole("button", { name: /cancel subscription/i }),
    );
    fireEvent.click(
      await screen.findByRole("button", { name: /yes, cancel/i }),
    );

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/subscription/cancel",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByText(/won't renew/i)).toBeInTheDocument();
  });

  it("shows the scheduled-cancellation state without a cancel button", async () => {
    apiFetch.mockResolvedValueOnce({
      status: "active",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
      cancel_at_period_end: true,
    });
    render(<SubscriptionView />);
    expect(await screen.findByText(/won't renew/i)).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /cancel subscription/i }),
    ).not.toBeInTheDocument();
  });

  it("warns when a payment failed (past_due grace)", async () => {
    apiFetch.mockResolvedValueOnce({
      status: "past_due",
      is_premium: true,
      current_period_end: "2026-12-31T00:00:00+00:00",
      cancel_at_period_end: false,
    });
    render(<SubscriptionView />);
    expect(
      await screen.findByText(/last payment failed/i),
    ).toBeInTheDocument();
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
        interval: "month",
        environment: "sandbox",
        customer_email: "a@b.com",
        custom_data: { user_id: "u1" },
      });
    render(<SubscriptionView />);

    fireEvent.click(await screen.findByRole("button", { name: /upgrade to premium/i }));
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/subscription/checkout",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ interval: "month" }),
        }),
      ),
    );
  });

  it("passes the annual interval to checkout when selected", async () => {
    apiFetch
      .mockResolvedValueOnce({
        status: "free",
        is_premium: false,
        current_period_end: null,
      })
      .mockResolvedValueOnce({
        client_token: "tok",
        price_id: "pri_year",
        interval: "year",
        environment: "sandbox",
        customer_email: "a@b.com",
        custom_data: { user_id: "u1" },
      });
    render(<SubscriptionView />);

    fireEvent.click(await screen.findByRole("radio", { name: /annual/i }));
    fireEvent.click(
      screen.getByRole("button", { name: /upgrade to premium/i }),
    );
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/subscription/checkout",
        expect.objectContaining({
          body: JSON.stringify({ interval: "year" }),
        }),
      ),
    );
  });
});
