import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import TermsPage from "@/app/terms/page";
import PrivacyPage from "@/app/privacy/page";
import ContactPage from "@/app/contact/page";

describe("Legal pages (S1)", () => {
  it("renders the terms of service with the Garmin disclaimer and cancellation terms", () => {
    render(<TermsPage />);
    expect(
      screen.getByRole("heading", { name: /terms of service/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/not affiliated with garmin/i)).toBeInTheDocument();
    expect(screen.getByText(/cancel your subscription at any time/i)).toBeInTheDocument();
  });

  it("renders the privacy policy naming health data and processors", () => {
    render(<PrivacyPage />);
    expect(
      screen.getByRole("heading", { name: /privacy policy/i }),
    ).toBeInTheDocument();
    expect(screen.getByText(/heart rate/i)).toBeInTheDocument();
    expect(screen.getByText(/supabase/i)).toBeInTheDocument();
    expect(screen.getByText(/paddle/i)).toBeInTheDocument();
    expect(screen.getByText(/export.*delete/i)).toBeInTheDocument();
  });

  it("renders the contact page with a support email", () => {
    render(<ContactPage />);
    expect(screen.getByRole("heading", { name: /contact/i })).toBeInTheDocument();
    expect(
      screen.getByRole("link", { name: /support@endurancecoach\.app/i }),
    ).toBeInTheDocument();
  });
});
