import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ForgotPasswordForm } from "@/components/auth/forgot-password-form";

const { resetPasswordForEmail } = vi.hoisted(() => ({
  resetPasswordForEmail: vi.fn(),
}));

vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { resetPasswordForEmail } }),
}));

describe("ForgotPasswordForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("shows a no-enumeration confirmation after submit (7b.4)", async () => {
    resetPasswordForEmail.mockResolvedValue({ error: null });
    render(<ForgotPasswordForm />);
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "user@example.com" },
    });
    fireEvent.click(screen.getByRole("button", { name: /send reset link/i }));

    expect(
      await screen.findByText(/if this email exists/i),
    ).toBeInTheDocument();
    expect(resetPasswordForEmail).toHaveBeenCalledWith(
      "user@example.com",
      expect.objectContaining({ redirectTo: expect.any(String) }),
    );
    expect(
      screen.getByRole("link", { name: /back to login/i }),
    ).toHaveAttribute("href", "/login");
  });

  it("links back to login before submit (7b.4)", () => {
    render(<ForgotPasswordForm />);
    expect(
      screen.getByRole("link", { name: /back to login/i }),
    ).toHaveAttribute("href", "/login");
  });
});
