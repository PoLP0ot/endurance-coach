"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Activity, ChevronRight } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { activityPageSchema, type ActivitySummary } from "@/schemas/activity";
import { formatDate, formatDistance, formatDuration } from "@/lib/format";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";

type Phase = "loading" | "error" | "ready";

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
      <ul className="divide-y divide-border rounded-md border border-border">
        {items.map((a) => (
          <li key={a.id}>
            <Link
              href={`/activities/${a.id}`}
              className="flex items-center justify-between gap-4 px-4 py-3 transition-colors hover:bg-secondary/50"
            >
              <div className="min-w-0">
                <p className="truncate text-sm font-medium">
                  {a.name ?? a.activity_type}
                </p>
                <p className="text-xs text-muted-foreground">
                  {formatDate(a.start_time)} · {formatDistance(a.distance_m)} ·{" "}
                  {formatDuration(a.duration_s)}
                </p>
              </div>
              <ChevronRight
                className="h-4 w-4 shrink-0 text-muted-foreground"
                aria-hidden
              />
            </Link>
          </li>
        ))}
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
