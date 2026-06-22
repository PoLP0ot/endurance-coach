"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { cn } from "@/lib/utils";
import { Button } from "@/components/ui/button";

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
  const [step, setStep] = useState<"asking" | "typing" | "done">("asking");

  const choose = async (option: { value: string; label: string }) => {
    setMessages((prev) => [
      ...prev,
      { id: prev.length + 1, role: "user", content: option.label },
    ]);
    setStep("typing");

    // Persist the goal (best-effort; the coach continues regardless).
    try {
      const token = await getAccessToken();
      await apiFetch("/profile", {
        method: "PATCH",
        token,
        body: JSON.stringify({ primary_goal: option.value }),
      });
    } catch {
      // ignore — onboarding still proceeds
    }

    setMessages((prev) => [
      ...prev,
      { id: prev.length + 1, role: "coach", content: FOLLOW_UP[option.value] },
    ]);
    setStep("done");
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
        {step === "done" && (
          <Button className="w-full" onClick={() => router.push("/dashboard")}>
            Let&apos;s go →
          </Button>
        )}
      </div>
    </div>
  );
}
