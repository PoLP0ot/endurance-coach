import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { ImportProgress } from "@/components/onboarding/import-progress";

describe("ImportProgress (D3)", () => {
  it("marks earlier pipeline steps done and the current one active", () => {
    render(<ImportProgress label="Analyzing metrics…" />);
    const active = screen.getByRole("listitem", { current: "step" });
    expect(active).toHaveTextContent(/analyzing metrics/i);
    // Steps before the active one read as completed.
    expect(
      screen.getByText(/fetching activities/i).closest("li"),
    ).toHaveAttribute("data-state", "done");
    expect(
      screen.getByText(/building your dashboard/i).closest("li"),
    ).toHaveAttribute("data-state", "upcoming");
  });

  it("starts on the first step", () => {
    render(<ImportProgress label="Fetching activities…" />);
    const active = screen.getByRole("listitem", { current: "step" });
    expect(active).toHaveTextContent(/fetching activities/i);
  });

  it("shows unknown labels verbatim without losing progress", () => {
    render(<ImportProgress label="Import hit a snag — retrying shortly…" />);
    expect(screen.getByText(/retrying shortly/i)).toBeInTheDocument();
    expect(screen.getAllByRole("listitem")).toHaveLength(4);
  });
});
