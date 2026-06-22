import { render, screen, fireEvent } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Activity } from "lucide-react";

describe("Global states (US12)", () => {
  it("EmptyState shows title, description and an action", () => {
    render(
      <EmptyState
        icon={Activity}
        title="No activities yet"
        description="Connect your Garmin to get started."
        action={<button>Connect</button>}
      />,
    );
    expect(screen.getByText("No activities yet")).toBeInTheDocument();
    expect(
      screen.getByText(/connect your garmin to get started/i),
    ).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /connect/i })).toBeInTheDocument();
  });

  it("ErrorState renders an alert and retries on demand", () => {
    const onRetry = vi.fn();
    render(<ErrorState message="Something broke" onRetry={onRetry} />);
    expect(screen.getByRole("alert")).toHaveTextContent("Something broke");
    fireEvent.click(screen.getByRole("button", { name: /try again/i }));
    expect(onRetry).toHaveBeenCalledOnce();
  });

  it("ErrorState omits the retry button when no handler is given", () => {
    render(<ErrorState message="Read only" />);
    expect(
      screen.queryByRole("button", { name: /try again/i }),
    ).not.toBeInTheDocument();
  });

  it("LoadingState exposes a busy status with the requested number of rows", () => {
    render(<LoadingState rows={3} label="Loading your dashboard" />);
    const status = screen.getByRole("status");
    expect(status).toHaveAttribute("aria-busy", "true");
    expect(status).toHaveAccessibleName(/loading your dashboard/i);
    expect(status.querySelectorAll("[data-skeleton]")).toHaveLength(3);
  });
});
