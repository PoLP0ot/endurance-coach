import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { PrivacyView } from "@/components/settings/privacy-view";

const { apiFetch, getAccessToken, push, signOut } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
  push: vi.fn(),
  signOut: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { signOut } }),
}));
vi.mock("sonner", () => ({ toast: { success: vi.fn(), error: vi.fn() } }));

beforeEach(() => {
  vi.clearAllMocks();
  getAccessToken.mockResolvedValue("jwt");
  signOut.mockResolvedValue({ error: null });
  URL.createObjectURL = vi.fn(() => "blob:x");
  URL.revokeObjectURL = vi.fn();
});

describe("PrivacyView (US11b)", () => {
  it("exports the data bundle", async () => {
    apiFetch.mockResolvedValueOnce({ json: {}, csv: {} });
    render(<PrivacyView />);
    fireEvent.click(screen.getByRole("button", { name: /export my data/i }));
    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith("/gdpr/export", expect.anything()),
    );
  });

  it("requires confirmation before deleting, then erases and redirects", async () => {
    apiFetch.mockResolvedValueOnce({ deleted: true });
    render(<PrivacyView />);

    fireEvent.click(screen.getByRole("button", { name: /^delete my account$/i }));
    fireEvent.click(
      screen.getByRole("button", { name: /yes, permanently delete/i }),
    );

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/gdpr/account",
        expect.objectContaining({ method: "DELETE" }),
      ),
    );
    await waitFor(() => expect(signOut).toHaveBeenCalled());
    await waitFor(() => expect(push).toHaveBeenCalledWith("/"));
  });
});
