"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Loader2, Watch } from "lucide-react";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { Button } from "@/components/ui/button";

interface GarminStatus {
  status: string;
  garmin_username?: string | null;
  last_sync_at?: string | null;
}

/** Garmin connection status + on-demand "Sync now" (ST3.3). */
export function GarminCard() {
  const [status, setStatus] = useState<GarminStatus | null>(null);
  const [syncing, setSyncing] = useState(false);

  const load = useCallback(async () => {
    try {
      const token = await getAccessToken();
      setStatus(await apiFetch<GarminStatus>("/garmin/status", { token }));
    } catch {
      setStatus({ status: "disconnected" });
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const syncNow = async () => {
    setSyncing(true);
    try {
      const token = await getAccessToken();
      await apiFetch("/garmin/sync", { method: "POST", token });
      toast.success("Garmin sync complete.");
      await load();
    } catch {
      toast.error("Sync failed. Please try again.");
    } finally {
      setSyncing(false);
    }
  };

  const connected = status?.status === "connected";
  const lastSync = status?.last_sync_at
    ? new Date(status.last_sync_at).toLocaleString()
    : "never";

  return (
    <div className="rounded border border-line bg-card p-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-3">
          <Watch className="h-5 w-5 text-primary" aria-hidden />
          <div>
            <h2 className="font-display text-sm font-semibold text-ink">Garmin</h2>
            <p className="text-xs text-muted-foreground">
              {connected
                ? `${status?.garmin_username ?? "Connected"} · last sync ${lastSync}`
                : "Not connected"}
            </p>
          </div>
        </div>
        {connected ? (
          <Button size="sm" onClick={syncNow} disabled={syncing}>
            {syncing && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
            {syncing ? "Syncing…" : "Sync now"}
          </Button>
        ) : (
          <Button asChild size="sm">
            <Link href="/onboarding">Connect Garmin</Link>
          </Button>
        )}
      </div>
    </div>
  );
}
