import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { SessionRunner } from "@/components/strength/session-runner";

const { apiFetch, getAccessToken } = vi.hoisted(() => ({
  apiFetch: vi.fn(),
  getAccessToken: vi.fn(),
}));

vi.mock("@/lib/api", async (importOriginal) => {
  const mod = await importOriginal<typeof import("@/lib/api")>();
  return { ...mod, apiFetch };
});
vi.mock("@/lib/session", () => ({ getAccessToken }));

const item = {
  slot: "push",
  exercise_id: "0025",
  name: "barbell bench press",
  equipment: "barbell",
  gif_url: "https://cdn.example/videos/0025.gif",
  target_weight_kg: null,
  sets: 2,
  reps: 10,
  rpe: 8,
  rest_sec: 90,
};

const plan = {
  id: "sp1",
  goal_kind: null,
  weeks: 8,
  frequency: 2,
  level: "intermediate",
  equipment: ["barbell"],
  start_date: "2026-07-13",
  status: "active",
  narrative: null,
  structure: {
    frequency: 2,
    level: "intermediate",
    equipment: ["barbell"],
    blocks: [{ block: "adaptation", weeks: 2 }],
    weeks: [
      {
        week: 1,
        start_date: "2026-07-13",
        block: "adaptation",
        is_deload: false,
        focus: "Groove the movements",
        sessions: [{ day: 0, focus: "full", title: "Full body A", items: [item] }],
      },
    ],
  },
};

const emptyLogs = {
  sets: [],
  summary: {
    week: 1,
    day: 0,
    title: "Full body A",
    sets_prescribed: 2,
    sets_logged: 0,
    volume_kg: 0,
    completed: false,
  },
};

function mockRoutes(overrides: Record<string, unknown> = {}) {
  apiFetch.mockImplementation(async (path: string, options?: { method?: string }) => {
    const method = options?.method ?? "GET";
    const key = `${method} ${path.split("?")[0]}`;
    const routes: Record<string, unknown> = {
      "GET /strength/plans/current": { plan },
      "GET /strength/logs": emptyLogs,
      "POST /strength/logs": {
        exercise_id: "0025",
        set_index: 1,
        weight_kg: 40,
        reps: 10,
        rpe: null,
      },
      "POST /strength/sessions/complete": {
        ...emptyLogs.summary,
        sets_logged: 1,
        volume_kg: 400,
        completed: true,
      },
      ...overrides,
    };
    if (!(key in routes)) throw new Error(`no mock for ${key}`);
    return routes[key];
  });
}

describe("SessionRunner (M4)", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    getAccessToken.mockResolvedValue("jwt");
  });

  it("renders the session with prefilled reps and set rows", async () => {
    mockRoutes();
    render(<SessionRunner week={1} day={0} />);

    expect(await screen.findByText("barbell bench press")).toBeInTheDocument();
    expect(screen.getByText("Set 1")).toBeInTheDocument();
    expect(screen.getByText("Set 2")).toBeInTheDocument();
    expect(screen.getByLabelText(/set 1 reps/i)).toHaveValue(10);
  });

  it("logs a set and starts the rest timer", async () => {
    mockRoutes();
    render(<SessionRunner week={1} day={0} />);
    await screen.findByText("barbell bench press");

    fireEvent.change(screen.getByLabelText(/set 1 weight/i), {
      target: { value: "40" },
    });
    fireEvent.click(screen.getAllByRole("button", { name: "Log" })[0]);

    await waitFor(() =>
      expect(apiFetch).toHaveBeenCalledWith(
        "/strength/logs",
        expect.objectContaining({ method: "POST" }),
      ),
    );
    expect(await screen.findByText(/Rest 90s/)).toBeInTheDocument();
  });

  it("finishes the session and shows the summary", async () => {
    mockRoutes();
    render(<SessionRunner week={1} day={0} />);
    await screen.findByText("barbell bench press");

    fireEvent.click(screen.getByRole("button", { name: /finish session/i }));

    expect(await screen.findByText(/session complete/i)).toBeInTheDocument();
    expect(screen.getByText(/400 kg total volume/i)).toBeInTheDocument();
  });

  it("prefills the suggested weight and shows the last performance", async () => {
    mockRoutes({
      "GET /strength/logs": {
        ...emptyLogs,
        suggestions: {
          "0025": { weight_kg: 42.5, last: { weight_kg: 40, reps: 10 } },
        },
      },
    });
    render(<SessionRunner week={1} day={0} />);
    await screen.findByText("barbell bench press");

    expect(screen.getByLabelText(/set 1 weight/i)).toHaveValue(42.5);
    expect(screen.getByText(/Last: 40 kg × 10/)).toBeInTheDocument();
  });

  it("says so when the session is not in the program", async () => {
    mockRoutes();
    render(<SessionRunner week={5} day={0} />);
    expect(await screen.findByRole("alert")).toHaveTextContent(
      /isn't part of your current program/i,
    );
  });
});
