import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ConnectGarmin } from "@/components/onboarding/connect-garmin";
import { ApiError } from "@/lib/api";

const { push, apiFetch, getSession } = vi.hoisted(() => ({
  push: vi.fn(),
  apiFetch: vi.fn(),
  getSession: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/api", async () => {
  const actual = await vi.importActual<typeof import("@/lib/api")>("@/lib/api");
  return { ...actual, apiFetch };
});
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { getSession } }),
}));

function fillAndSubmit() {
  fireEvent.change(screen.getByLabelText(/garmin email/i), {
    target: { value: "u@example.com" },
  });
  fireEvent.change(screen.getByLabelText(/garmin password/i), {
    target: { value: "pw" },
  });
  fireEvent.click(screen.getByRole("button", { name: /connect garmin/i }));
}

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

  it("tells wrong credentials apart from a locked account", async () => {
    apiFetch.mockRejectedValueOnce(new ApiError(401, "garmin_auth_failed"));
    render(<ConnectGarmin />);
    fillAndSubmit();
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /check your garmin email and password/i,
    );

    apiFetch.mockRejectedValueOnce(new ApiError(423, "garmin_account_locked"));
    fireEvent.click(screen.getByRole("button", { name: /connect garmin/i }));
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /temporarily locked/i,
    );
  });

  it("asks for the MFA code on 409 and completes the connect with it", async () => {
    apiFetch
      .mockRejectedValueOnce(new ApiError(409, "garmin_mfa_required")) // connect
      .mockResolvedValueOnce({ job_id: "job-2" }) // POST /garmin/mfa
      .mockResolvedValueOnce({ status: "done", progress_label: null }); // poll
    render(<ConnectGarmin />);
    fillAndSubmit();

    const codeInput = await screen.findByLabelText(/verification code/i);
    fireEvent.change(codeInput, { target: { value: "123456" } });
    fireEvent.click(screen.getByRole("button", { name: /verify/i }));

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/garmin/mfa",
        expect.objectContaining({
          method: "POST",
          body: JSON.stringify({ code: "123456" }),
        }),
      ),
    );
    await waitFor(() => expect(push).toHaveBeenCalledWith("/dashboard"));
  });

  it("surfaces an invalid MFA code and allows retry", async () => {
    apiFetch
      .mockRejectedValueOnce(new ApiError(409, "garmin_mfa_required"))
      .mockRejectedValueOnce(new ApiError(401, "garmin_mfa_invalid"));
    render(<ConnectGarmin />);
    fillAndSubmit();

    const codeInput = await screen.findByLabelText(/verification code/i);
    fireEvent.change(codeInput, { target: { value: "000000" } });
    fireEvent.click(screen.getByRole("button", { name: /verify/i }));

    expect(await screen.findByRole("alert")).toHaveTextContent(
      /code didn't match/i,
    );
    expect(screen.getByLabelText(/verification code/i)).toBeInTheDocument();
  });
});
