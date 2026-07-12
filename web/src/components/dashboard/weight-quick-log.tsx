"use client";

import { useState } from "react";
import { Check, Loader2, Scale } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Phase = "idle" | "saving" | "saved" | "error";

/**
 * Inline weigh-in for the weight-loss goal — the trajectory's data input for
 * athletes without a connected scale. Upserts today's entry.
 */
export function WeightQuickLog({ onLogged }: { onLogged?: () => void }) {
  const [draft, setDraft] = useState("");
  const [phase, setPhase] = useState<Phase>("idle");

  const submit = async () => {
    const value = Number(draft);
    if (!draft || Number.isNaN(value)) return;
    setPhase("saving");
    try {
      const token = await getAccessToken();
      await apiFetch("/profile/weight", {
        method: "POST",
        token,
        body: JSON.stringify({ weight_kg: value }),
      });
      setPhase("saved");
      setDraft("");
      onLogged?.();
    } catch {
      setPhase("error");
    }
  };

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        void submit();
      }}
      className="flex flex-wrap items-center gap-2 rounded border border-line bg-card px-4 py-3"
    >
      <Scale className="h-4 w-4 shrink-0 text-muted-foreground" aria-hidden />
      <span className="text-sm text-ink-soft">Today&apos;s weight</span>
      <Input
        aria-label="Today's weight in kilograms"
        type="number"
        inputMode="decimal"
        step="0.1"
        placeholder="kg"
        className="h-9 w-24"
        value={draft}
        onChange={(e) => {
          setDraft(e.target.value);
          if (phase !== "idle") setPhase("idle");
        }}
      />
      <Button type="submit" size="sm" disabled={phase === "saving" || !draft}>
        {phase === "saving" ? (
          <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
        ) : (
          "Log"
        )}
      </Button>
      {phase === "saved" && (
        <span className="flex items-center gap-1 text-xs text-accent">
          <Check className="h-3.5 w-3.5" aria-hidden /> Logged
        </span>
      )}
      {phase === "error" && (
        <span role="alert" className="text-xs text-destructive">
          Couldn&apos;t save — try again.
        </span>
      )}
    </form>
  );
}
