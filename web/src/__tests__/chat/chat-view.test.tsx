import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ChatView } from "@/components/chat/chat-view";
import { ApiError } from "@/lib/api";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch };
});
vi.mock("@/lib/session", () => ({ getAccessToken }));

beforeEach(() => {
  vi.clearAllMocks();
  getAccessToken.mockResolvedValue("jwt");
  Element.prototype.scrollIntoView = vi.fn();
});

describe("ChatView (US4)", () => {
  it("loads history and sends a message, showing the reply", async () => {
    apiFetch.mockResolvedValueOnce({ messages: [] }).mockResolvedValueOnce({
      id: 2,
      role: "assistant",
      content: "Rest today, then build.",
      created_at: null,
    });
    render(<ChatView />);

    const input = await screen.findByLabelText(/message your coach/i);
    fireEvent.change(input, { target: { value: "How do I feel?" } });
    fireEvent.click(screen.getByRole("button", { name: /send/i }));

    expect(await screen.findByText("How do I feel?")).toBeInTheDocument();
    expect(await screen.findByText("Rest today, then build.")).toBeInTheDocument();
  });

  it("shows a premium upsell when chat is gated (402)", async () => {
    apiFetch.mockRejectedValueOnce(new ApiError(402, "premium_required"));
    render(<ChatView />);
    expect(await screen.findByText(/coach chat is premium/i)).toBeInTheDocument();
  });
});
