import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ExerciseLibrary } from "@/components/exercises/exercise-library";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

const row = (id: string, name: string) => ({
  id,
  name,
  body_part: "chest",
  target: "pectorals",
  equipment: "barbell",
  image_url: `https://cdn.example/images/${id}.jpg`,
  gif_url: `https://cdn.example/videos/${id}.gif`,
});

describe("ExerciseLibrary (M2)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders exercises and loads more pages", async () => {
    apiFetch
      .mockResolvedValueOnce({ items: [row("0001", "bench press")], next_cursor: "c1" })
      .mockResolvedValueOnce({ items: [row("0002", "cable fly")], next_cursor: null });
    render(<ExerciseLibrary />);

    expect(await screen.findByText("bench press")).toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: /load more/i }));
    expect(await screen.findByText("cable fly")).toBeInTheDocument();
    expect(screen.getByText("bench press")).toBeInTheDocument();
  });

  it("refetches with the body part filter", async () => {
    apiFetch.mockResolvedValue({ items: [row("0001", "bench press")], next_cursor: null });
    render(<ExerciseLibrary />);
    await screen.findByText("bench press");

    fireEvent.change(screen.getByLabelText(/body part/i), {
      target: { value: "chest" },
    });
    await waitFor(() =>
      expect(apiFetch).toHaveBeenLastCalledWith(
        expect.stringContaining("body_part=chest"),
        expect.anything(),
      ),
    );
  });

  it("searches by name", async () => {
    apiFetch.mockResolvedValue({ items: [], next_cursor: null });
    render(<ExerciseLibrary />);
    await screen.findByText(/no exercises found/i);

    fireEvent.change(screen.getByRole("searchbox"), {
      target: { value: "deadlift" },
    });
    await waitFor(() =>
      expect(apiFetch).toHaveBeenLastCalledWith(
        expect.stringContaining("q=deadlift"),
        expect.anything(),
      ),
    );
  });

  it("shows an error state on failure", async () => {
    apiFetch.mockRejectedValueOnce(new Error("boom"));
    render(<ExerciseLibrary />);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
