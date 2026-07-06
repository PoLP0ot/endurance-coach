"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Watch } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";

/** Garmin statuses that mean the data pipe is broken and needs the athlete. */
const NEEDS_RECONNECT = new Set(["auth_expired", "error"]);

/**
 * Shows only when the Garmin connection stopped working (dead token) — the
 * dashboard would otherwise go quietly stale. Progressive: silent while
 * loading, on failure, and while everything is fine.
 */
export function GarminStatusBanner() {
  const [needsReconnect, setNeedsReconnect] = useState(false);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<{ status: string }>("/garmin/status", { token });
      setNeedsReconnect(NEEDS_RECONNECT.has(raw.status));
    } catch {
      setNeedsReconnect(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  if (!needsReconnect) return null;

  return (
    <div
      role="alert"
      className="flex flex-wrap items-center justify-between gap-3 rounded border border-destructive/40 bg-card p-4"
    >
      <p className="flex items-center gap-2.5 text-sm text-ink-soft">
        <Watch className="h-4 w-4 shrink-0 text-destructive" aria-hidden />
        <span>
          <span className="font-semibold text-ink">
            Your Garmin connection has expired.
          </span>{" "}
          New activities aren&apos;t coming in — sign in again to resume syncing.
        </span>
      </p>
      <Link
        href="/onboarding"
        className="text-sm font-semibold text-primary underline-offset-4 hover:underline"
      >
        Reconnect Garmin →
      </Link>
    </div>
  );
}
