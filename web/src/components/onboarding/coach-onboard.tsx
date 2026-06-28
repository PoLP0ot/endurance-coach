"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Msg {
  id: number;
  role: "coach" | "user";
  content: string;
}

const GOAL_OPTIONS: Array<{ value: string; label: string }> = [
  { value: "marathon", label: "Marathon" },
  { value: "weight_loss", label: "Weight loss" },
  { value: "hyrox", label: "Hyrox" },
  { value: "triathlon", label: "Triathlon" },
  { value: "health", label: "General health" },
  { value: "unsure", label: "Not sure yet" },
];

/** Per-goal follow-up: a quick chip choice or a single number, → goal_params. */
type MetaChip = { label: string; params: Record<string, unknown> };
interface GoalMeta {
  prompt: string;
  kind: "chips" | "number";
  chips?: MetaChip[];
  inputKey?: string;
  inputLabel?: string;
  inputUnit?: string;
}

const GOAL_META: Record<string, GoalMeta> = {
  marathon: {
    prompt: "What finish time are you chasing?",
    kind: "chips",
    chips: [
      { label: "Sub-3:30", params: { target_time_s: 12600 } },
      { label: "Sub-4:00", params: { target_time_s: 14400 } },
      { label: "Sub-4:30", params: { target_time_s: 16200 } },
      { label: "Just finish", params: {} },
    ],
  },
  weight_loss: {
    prompt: "What's your target weight?",
    kind: "number",
    inputKey: "target_weight_kg",
    inputLabel: "Target weight",
    inputUnit: "kg",
  },
  health: {
    prompt: "How many active days per week are you aiming for?",
    kind: "chips",
    chips: [
      { label: "3 days", params: { weekly_activity_target: 3 } },
      { label: "4 days", params: { weekly_activity_target: 4 } },
      { label: "5 days", params: { weekly_activity_target: 5 } },
    ],
  },
};

const FOLLOW_UP: Record<string, string> = {
  marathon:
    "A marathon — love it. I'll build a periodized plan around your long runs and threshold work, and I'll watch your fatigue so you arrive on race day fresh.",
  weight_loss:
    "Weight loss it is. I'll keep most sessions in the easy aerobic zone to maximise fat use, and surface calorie balance and step trends alongside your training.",
  hyrox:
    "Hyrox — a proper hybrid challenge. I'll balance running volume with strength-endurance and track how the two loads interact week to week.",
  triathlon:
    "Triathlon. I'll pull running, riding and swimming into one combined load picture so nothing gets double-counted, and pace your build across all three.",
  health:
    "General health is a great goal. I'll focus on consistency, recovery (sleep, HRV, resting HR) and gentle progression rather than chasing a race.",
  unsure:
    "No problem — we can start broad. I'll keep an eye on your fitness, fatigue and recovery, and we can sharpen the goal once we see a few weeks of data.",
};

/** Conversational onboarding: the coach discovers the athlete's goal through chat (A15). */
export function CoachOnboard() {
  const router = useRouter();
  const [messages, setMessages] = useState<Msg[]>([
    {
      id: 1,
      role: "coach",
      content:
        "I've pulled in your recent training from Garmin. Before I start coaching, tell me — what are you training for right now?",
    },
  ]);
  const [step, setStep] = useState<"asking" | "meta" | "done">("asking");
  const [goal, setGoal] = useState<string | null>(null);
  const [numberDraft, setNumberDraft] = useState("");

  const say = (role: Msg["role"], content: string) =>
    setMessages((prev) => [...prev, { id: prev.length + 1, role, content }]);

  const patchProfile = async (body: Record<string, unknown>) => {
    try {
      const token = await getAccessToken();
      await apiFetch("/profile", {
        method: "PATCH",
        token,
        body: JSON.stringify(body),
      });
    } catch {
      // best-effort — onboarding still proceeds
    }
  };

  const choose = async (option: { value: string; label: string }) => {
    say("user", option.label);
    setGoal(option.value);
    await patchProfile({ primary_goal: option.value });
    say("coach", FOLLOW_UP[option.value]);
    if (GOAL_META[option.value]) {
      say("coach", GOAL_META[option.value].prompt);
      setStep("meta");
    } else {
      setStep("done");
    }
  };

  const answerMeta = async (label: string, params: Record<string, unknown>) => {
    say("user", label);
    if (goal && Object.keys(params).length > 0) {
      await patchProfile({ primary_goal: goal, goal_params: params });
    }
    say("coach", "Got it — that gives me a target to coach you toward.");
    setStep("done");
  };

  const submitNumber = async () => {
    const meta = goal ? GOAL_META[goal] : undefined;
    const value = Number(numberDraft);
    if (!meta?.inputKey || !numberDraft || Number.isNaN(value)) return;
    await answerMeta(`${numberDraft} ${meta.inputUnit ?? ""}`.trim(), {
      [meta.inputKey]: value,
    });
  };

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-2xl flex-col px-4">
      <header className="flex items-center gap-2 border-b border-line py-4">
        <span className="grid h-5 w-5 place-items-center rounded-full border border-ink">
          <span className="h-1 w-1 rounded-full bg-primary" />
        </span>
        <span className="font-mono text-[10px] uppercase tracking-[0.16em] text-muted-foreground">
          Step 3 of 3 · Your goal
        </span>
      </header>

      <div className="flex-1 space-y-4 overflow-y-auto py-6">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn("flex", m.role === "user" ? "justify-end" : "justify-start")}
          >
            <p
              className={cn(
                "max-w-[84%] whitespace-pre-line rounded-[12px] px-4 py-3 text-[14.5px] leading-relaxed",
                m.role === "user"
                  ? "rounded-tr-[3px] bg-ink text-paper"
                  : "rounded-tl-[3px] border border-line bg-card text-ink-soft",
              )}
            >
              {m.content}
            </p>
          </div>
        ))}
      </div>

      <div className="border-t border-line py-5">
        {step === "asking" && (
          <div className="flex flex-wrap gap-2">
            {GOAL_OPTIONS.map((o) => (
              <button
                key={o.value}
                type="button"
                onClick={() => void choose(o)}
                className="rounded-full border border-line bg-card px-3.5 py-1.5 text-sm text-ink-soft transition-colors hover:border-primary hover:text-ink"
              >
                {o.label}
              </button>
            ))}
          </div>
        )}
        {step === "meta" && goal && GOAL_META[goal]?.kind === "chips" && (
          <div className="flex flex-wrap gap-2">
            {GOAL_META[goal].chips!.map((c) => (
              <button
                key={c.label}
                type="button"
                onClick={() => void answerMeta(c.label, c.params)}
                className="rounded-full border border-line bg-card px-3.5 py-1.5 text-sm text-ink-soft transition-colors hover:border-primary hover:text-ink"
              >
                {c.label}
              </button>
            ))}
          </div>
        )}
        {step === "meta" && goal && GOAL_META[goal]?.kind === "number" && (
          <form
            onSubmit={(e) => {
              e.preventDefault();
              void submitNumber();
            }}
            className="flex items-center gap-2"
          >
            <Input
              type="number"
              inputMode="decimal"
              aria-label={GOAL_META[goal].inputLabel ?? "Value"}
              placeholder={GOAL_META[goal].inputLabel}
              value={numberDraft}
              onChange={(e) => setNumberDraft(e.target.value)}
            />
            <Button type="submit" disabled={!numberDraft}>
              Save
            </Button>
          </form>
        )}
        {step === "done" && (
          <Button className="w-full" onClick={() => router.push("/dashboard")}>
            Let&apos;s go →
          </Button>
        )}
      </div>
    </div>
  );
}
