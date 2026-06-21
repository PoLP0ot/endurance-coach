import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "@/app/page";

describe("Landing page", () => {
  it("renders the coach-first headline", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", { level: 1, name: /coaching/i }),
    ).toBeInTheDocument();
  });

  it("shows a primary call to action", () => {
    render(<Home />);
    expect(
      screen.getByRole("button", { name: /get started/i }),
    ).toBeInTheDocument();
  });

  it("highlights the deterministic-metrics differentiator", () => {
    render(<Home />);
    expect(screen.getByText(/never invented by an AI/i)).toBeInTheDocument();
  });
});
