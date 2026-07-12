"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Watch } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";

/** Garmin statuses that mean the data pipe is broken and needs the athlete. */
const NEEDS_RECONNECT = new Set(["auth_expired", "error"]);

/** A connected watch whose last sync is older than this reads as stale. */
const STALE_AFTER_DAYS = 3;

type BannerState =
  | { kind: "hidden" }
  | { kind: "reconnect" }
  | { kind: "stale"; days: number };

function staleDays(lastSyncIso: string | null | undefined): number | null {
  if (!lastSyncIso) return null;
  const last = new Date(lastSyncIso).getTime();
  if (Number.isNaN(last)) return null;
  return Math.floor((Date.now() - last) / 86400000);
}

/**
 * Shows when the Garmin pipe needs the athlete: dead token (reconnect) or a
 * connected watch that hasn't synced in days (the dashboard would quietly show
 * zeros otherwise). Progressive: silent while loading, on failure, when fine.
 */
export function GarminStatusBanner() {
  const [state, setState] = useState<BannerState>({ kind: "hidden" });
  const [syncStarted, setSyncStarted] = useState(false);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<{ status: string; last_sync_at?: string | null }>(
        "/garmin/status",
        { token },
      );
      if (NEEDS_RECONNECT.has(raw.status)) {
        setState({ kind: "reconnect" });
        return;
      }
      const days = staleDays(raw.last_sync_at);
      if (raw.status === "connected" && days !== null && days >= STALE_AFTER_DAYS) {
        setState({ kind: "stale", days });
        return;
      }
      setState({ kind: "hidden" });
    } catch {
      setState({ kind: "hidden" });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const syncNow = async () => {
    try {
      const token = await getAccessToken();
      await apiFetch("/garmin/sync", { method: "POST", token });
      setSyncStarted(true);
    } catch {
      // keep the banner; the athlete can retry
    }
  };

  if (state.kind === "hidden") return null;

  if (state.kind === "stale") {
    return (
      <div
        role="status"
        className="flex flex-wrap items-center justify-between gap-3 rounded border border-rust/40 bg-card p-4"
      >
        <p className="flex items-center gap-2.5 text-sm text-ink-soft">
          <Watch className="h-4 w-4 shrink-0 text-rust" aria-hidden />
          <span>
            <span className="font-semibold text-ink">
              Last sync was {state.days} days ago.
            </span>{" "}
            Your recent training isn&apos;t in yet — this week may look emptier
            than it was.
          </span>
        </p>
        {syncStarted ? (
          <span className="text-sm text-muted-foreground">
            Sync started — check back in a minute.
          </span>
        ) : (
          <button
            type="button"
            onClick={() => void syncNow()}
            className="text-sm font-semibold text-primary underline-offset-4 hover:underline"
          >
            Sync now →
          </button>
        )}
      </div>
    );
  }

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
