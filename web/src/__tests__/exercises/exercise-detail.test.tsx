import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { ExerciseDetail } from "@/components/exercises/exercise-detail";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", () => ({ apiFetch }));
vi.mock("@/lib/session", () => ({ getAccessToken }));

const detail = {
  id: "0001",
  name: "3/4 sit-up",
  body_part: "waist",
  target: "abs",
  equipment: "body weight",
  image_url: "https://cdn.example/images/0001.jpg",
  gif_url: "https://cdn.example/videos/0001.gif",
  muscle_group: "hip flexors",
  secondary_muscles: ["hip flexors", "lower back"],
  instructions: ["Set up.", "Curl your torso."],
  attribution: "Gym visual",
};

describe("ExerciseDetail (M2)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders the sheet: gif, muscles and instruction steps", async () => {
    apiFetch.mockResolvedValueOnce(detail);
    render(<ExerciseDetail id="0001" />);

    expect(await screen.findByText("3/4 sit-up")).toBeInTheDocument();
    expect(screen.getByRole("img", { name: /3\/4 sit-up/i })).toHaveAttribute(
      "src",
      detail.gif_url,
    );
    expect(screen.getByText("Set up.")).toBeInTheDocument();
    expect(screen.getByText("Curl your torso.")).toBeInTheDocument();
    expect(screen.getByText(/abs/)).toBeInTheDocument();
    expect(screen.getByText(/lower back/)).toBeInTheDocument();
    expect(screen.getByText(/gym visual/i)).toBeInTheDocument();
  });

  it("shows an error state when the exercise is missing", async () => {
    apiFetch.mockRejectedValueOnce(new Error("exercise_not_found"));
    render(<ExerciseDetail id="9999" />);
    expect(await screen.findByRole("alert")).toBeInTheDocument();
  });
});
