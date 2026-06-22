import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ConnectGarmin } from "@/components/onboarding/connect-garmin";

const { push, apiFetch, getSession } = vi.hoisted(() => ({
  push: vi.fn(),
  apiFetch: vi.fn(),
  getSession: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { getSession } }),
}));

describe("ConnectGarmin onboarding (US1.12)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getSession.mockResolvedValue({ data: { session: { access_token: "jwt" } } });
  });

  it("shows reassurance text and a skip link", () => {
    render(<ConnectGarmin />);
    expect(screen.getByText(/your data is encrypted/i)).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /i'll do this later/i }),
    ).toHaveAttribute("href", "/dashboard");
  });

  it("connects then redirects to the dashboard when import completes", async () => {
    apiFetch
      .mockResolvedValueOnce({ job_id: "job-1" }) // POST /garmin/connect
      .mockResolvedValueOnce({ status: "done", progress_label: "Building…" });
    render(<ConnectGarmin />);

    fireEvent.change(screen.getByLabelText(/garmin email/i), {
      target: { value: "u@example.com" },
    });
    fireEvent.change(screen.getByLabelText(/garmin password/i), {
      target: { value: "pw" },
    });
    fireEvent.click(screen.getByRole("button", { name: /connect garmin/i }));

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/garmin/connect",
        expect.objectContaining({ method: "POST", token: "jwt" }),
      ),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
  });

  it("shows an error when the connection fails", async () => {
    apiFetch.mockRejectedValueOnce(new Error("nope"));
    render(<ConnectGarmin />);
    fireEvent.click(screen.getByRole("button", { name: /connect garmin/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /couldn't connect to garmin/i,
    );
  });
});
