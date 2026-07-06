"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import {
  Activity,
  Bike,
  ChevronRight,
  Dumbbell,
  Footprints,
  Waves,
  type LucideIcon,
} from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { activityPageSchema, type ActivitySummary } from "@/schemas/activity";
import {
  formatDate,
  formatDistance,
  formatDuration,
  formatPace,
} from "@/lib/format";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";

type Phase = "loading" | "error" | "ready";

/** Sport glyph for a Garmin activity_type string (running/cycling/…). */
function typeIcon(activityType: string): LucideIcon {
  const t = activityType.toLowerCase();
  if (t.includes("run")) return Footprints;
  if (t.includes("cycl") || t.includes("bik") || t.includes("ride")) return Bike;
  if (t.includes("swim")) return Waves;
  if (t.includes("strength") || t.includes("training")) return Dumbbell;
  return Activity;
}

/** Pace only makes sense for foot sports; rides get avg speed elsewhere. */
function rowPace(a: ActivitySummary): string | null {
  if (!a.activity_type.toLowerCase().includes("run")) return null;
  return formatPace(a.distance_m, a.duration_s);
}

/** Paginated activity history with cursor-based "load more" (US9). */
export function ActivityList() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [items, setItems] = useState<ActivitySummary[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);

  const fetchPage = useCallback(async (next: string | null) => {
    const token = await getAccessToken();
    const query = next ? `?cursor=${encodeURIComponent(next)}` : "";
    const raw = await apiFetch<unknown>(`/activities${query}`, { token });
    return activityPageSchema.parse(raw);
  }, []);

  const loadInitial = useCallback(async () => {
    setPhase("loading");
    try {
      const page = await fetchPage(null);
      setItems(page.items);
      setCursor(page.next_cursor);
      setPhase("ready");
    } catch {
      setPhase("error");
    }
  }, [fetchPage]);

  useEffect(() => {
    void loadInitial();
  }, [loadInitial]);

  const loadMore = async () => {
    if (!cursor) return;
    setLoadingMore(true);
    try {
      const page = await fetchPage(cursor);
      setItems((prev) => [...prev, ...page.items]);
      setCursor(page.next_cursor);
    } finally {
      setLoadingMore(false);
    }
  };

  if (phase === "loading") {
    return <LoadingState rows={6} label="Loading your activities" />;
  }
  if (phase === "error") {
    return (
      <ErrorState
        message="We couldn't load your activities."
        onRetry={() => void loadInitial()}
      />
    );
  }
  if (items.length === 0) {
    return (
      <EmptyState
        icon={Activity}
        title="No activities yet"
        description="Once your Garmin data is imported, your runs will appear here."
      />
    );
  }

  return (
    <div className="space-y-4">
      <ul className="divide-y divide-line rounded border border-line bg-card">
        {items.map((a) => {
          const Icon = typeIcon(a.activity_type);
          const pace = rowPace(a);
          return (
            <li key={a.id}>
              <Link
                href={`/activities/${a.id}`}
                className="flex items-center gap-4 px-4 py-3 transition-colors hover:bg-secondary/50"
              >
                <span
                  className="grid h-9 w-9 shrink-0 place-items-center rounded-full border border-line text-muted-foreground"
                  title={a.activity_type}
                >
                  <Icon className="h-4 w-4" aria-hidden />
                </span>
                <div className="min-w-0 flex-1">
                  <p className="truncate font-display text-sm font-semibold text-ink">
                    {a.name ?? a.activity_type}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {formatDate(a.start_time)} · {formatDistance(a.distance_m)} ·{" "}
                    {formatDuration(a.duration_s)}
                    {pace && ` · ${pace}`}
                  </p>
                </div>
                {a.tss !== null && (
                  <span className="shrink-0 text-right">
                    <span className="font-display text-sm font-semibold tabular-nums text-ink">
                      {a.tss.toFixed(0)}
                    </span>
                    <span className="ml-1 font-mono text-[10px] text-muted-foreground">
                      TSS
                    </span>
                  </span>
                )}
                <ChevronRight
                  className="h-4 w-4 shrink-0 text-muted-foreground"
                  aria-hidden
                />
              </Link>
            </li>
          );
        })}
      </ul>
      {cursor && (
        <div className="flex justify-center">
          <Button variant="outline" onClick={loadMore} disabled={loadingMore}>
            {loadingMore ? "Loading…" : "Load more"}
          </Button>
        </div>
      )}
    </div>
  );
}
