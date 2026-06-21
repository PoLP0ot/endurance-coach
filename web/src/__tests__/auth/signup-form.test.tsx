import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SignupForm } from "@/components/auth/signup-form";

const { push, signUp, signInWithOAuth } = vi.hoisted(() => ({
  push: vi.fn(),
  signUp: vi.fn(),
  signInWithOAuth: vi.fn(),
}));

vi.mock("next/navigation", () => ({ useRouter: () => ({ push }) }));
vi.mock("@/lib/supabase/client", () => ({
  createClient: () => ({ auth: { signUp, signInWithOAuth } }),
}));

function fill(email: string, password: string) {
  fireEvent.change(screen.getByLabelText("Email"), {
    target: { value: email },
  });
  fireEvent.change(screen.getByLabelText("Password"), {
    target: { value: password },
  });
}

describe("SignupForm", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("validates email and password length (7b.1)", async () => {
    render(<SignupForm />);
    fill("not-an-email", "short");
    fireEvent.click(screen.getByRole("button", { name: /create account/i }));

    expect(
      await screen.findByText(/please enter a valid email/i),
    ).toBeInTheDocument();
    expect(
      await screen.findByText(/at least 8 characters/i),
    ).toBeInTheDocument();
    expect(signUp).not.toHaveBeenCalled();
  });

  it("shows an account-exists message with a login link (7b.2)", async () => {
    signUp.mockResolvedValue({
      data: { user: null },
      error: { message: "User already registered" },
    });
    render(<SignupForm />);
    fill("taken@example.com", "password123");
    fireEvent.click(screen.getByRole("button", { name: /create account/i }));

    expect(
      await screen.findByText(/already exists/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /log in\?/i })).toHaveAttribute(
      "href",
      "/login",
    );
  });

  it("redirects to onboarding on success (7b.2)", async () => {
    signUp.mockResolvedValue({
      data: { user: { identities: [{}] } },
      error: null,
    });
    render(<SignupForm />);
    fill("new@example.com", "password123");
    fireEvent.click(screen.getByRole("button", { name: /create account/i }));

    await waitFor(() => expect(push).toHaveBeenCalledWith("/onboarding"));
  });

  it("offers Google signup and a login link (7b.1)", () => {
    render(<SignupForm />);
    expect(
      screen.getByRole("button", { name: /continue with google/i }),
    ).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /^log in$/i })).toHaveAttribute(
      "href",
      "/login",
    );
  });
});
