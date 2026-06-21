import { render, screen, fireEvent, within } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import Home from "@/app/page";

describe("Landing page — hero (7a.1)", () => {
  it("renders the decoded headline", () => {
    render(<Home />);
    expect(
      screen.getByRole("heading", {
        level: 1,
        name: /your garmin data, finally decoded/i,
      }),
    ).toBeInTheDocument();
  });

  it("shows the AI-coaching subheadline", () => {
    render(<Home />);
    expect(
      screen.getAllByText(/10x cheaper than a human coach/i).length,
    ).toBeGreaterThan(0);
  });

  it("has a primary CTA linking to signup", () => {
    render(<Home />);
    const cta = screen.getByRole("link", { name: /connect your garmin/i });
    expect(cta).toHaveAttribute("href", "/signup");
  });

  it("has a secondary anchor to how it works", () => {
    render(<Home />);
    const anchor = screen.getByRole("link", { name: /see how it works/i });
    expect(anchor).toHaveAttribute("href", "#how-it-works");
  });
});

describe("Landing page — how it works (7a.2)", () => {
  it("renders three steps", () => {
    render(<Home />);
    const section = document.getElementById("how-it-works");
    expect(section).not.toBeNull();
    expect(within(section!).getByText(/connect garmin/i)).toBeInTheDocument();
    expect(
      within(section!).getByText(/get your dashboard/i),
    ).toBeInTheDocument();
    expect(within(section!).getByText(/^ai coaching$/i)).toBeInTheDocument();
  });
});

describe("Landing page — features (7a.3)", () => {
  it("renders three feature columns each with bullet benefits", () => {
    render(<Home />);
    const section = document.getElementById("features");
    expect(section).not.toBeNull();
    expect(
      within(section!).getByText(/understand every metric/i),
    ).toBeInTheDocument();
    expect(within(section!).getByText(/ask anything/i)).toBeInTheDocument();
    expect(within(section!).getByText(/adaptive plans/i)).toBeInTheDocument();
    // every feature exposes a bullet list
    expect(within(section!).getAllByRole("list").length).toBe(3);
  });
});

describe("Landing page — comparison table (7a.4)", () => {
  it("renders competitors with our column highlighted", () => {
    render(<Home />);
    const table = screen.getByRole("table");
    expect(within(table).getByText(/garmin connect/i)).toBeInTheDocument();
    expect(within(table).getByText(/strava/i)).toBeInTheDocument();
    expect(within(table).getByText(/trainingpeaks/i)).toBeInTheDocument();
    expect(
      table.querySelector('[data-highlighted="true"]'),
    ).not.toBeNull();
  });
});

describe("Landing page — pricing (7a.5)", () => {
  it("toggles between monthly and annual price", () => {
    render(<Home />);
    const pricing = document.getElementById("pricing")!;
    expect(within(pricing).getByText(/save 18%/i)).toBeInTheDocument();
    expect(within(pricing).getAllByText(/\$8/).length).toBeGreaterThan(0);
    expect(within(pricing).queryByText(/\$79/)).toBeNull();
    fireEvent.click(within(pricing).getByRole("button", { name: /annual/i }));
    expect(within(pricing).getAllByText(/\$79/).length).toBeGreaterThan(0);
  });

  it("pricing CTAs point to signup", () => {
    render(<Home />);
    const pricing = document.getElementById("pricing")!;
    const links = within(pricing).getAllByRole("link");
    expect(links.length).toBeGreaterThan(0);
    links.forEach((link) => expect(link).toHaveAttribute("href", "/signup"));
  });
});

describe("Landing page — testimonials (7a.6)", () => {
  it("shows pre-launch founder fallback", () => {
    render(<Home />);
    expect(screen.getByText(/be one of the first/i)).toBeInTheDocument();
  });
});

describe("Landing page — FAQ (7a.7)", () => {
  it("expands an answer on click", () => {
    render(<Home />);
    const faq = document.getElementById("faq")!;
    const trigger = within(faq).getByRole("button", {
      name: /is my garmin data safe/i,
    });
    expect(trigger).toHaveAttribute("data-state", "closed");
    fireEvent.click(trigger);
    expect(trigger).toHaveAttribute("data-state", "open");
  });
});

describe("Landing page — footer (7a.8)", () => {
  it("renders legal links and copyright", () => {
    render(<Home />);
    const footer = screen.getByRole("contentinfo");
    expect(
      within(footer).getByRole("link", { name: /privacy/i }),
    ).toBeInTheDocument();
    expect(
      within(footer).getByRole("link", { name: /terms/i }),
    ).toBeInTheDocument();
    expect(
      within(footer).getByRole("link", { name: /contact/i }),
    ).toBeInTheDocument();
    expect(within(footer).getByText(/©\s*2026/)).toBeInTheDocument();
  });
});
