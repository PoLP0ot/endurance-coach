"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { Dumbbell } from "lucide-react";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  BODY_PARTS,
  EQUIPMENT_TYPES,
  exercisePageSchema,
  type ExerciseSummary,
} from "@/schemas/exercise";
import { EmptyState } from "@/components/states/empty-state";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Phase = "loading" | "error" | "ready";

const SEARCH_DEBOUNCE_MS = 300;

const SELECT_CLASS =
  "w-full rounded border border-input bg-card px-3 py-2.5 text-sm text-foreground focus-visible:border-primary focus-visible:outline-none";

function buildQuery(
  bodyPart: string,
  equipment: string,
  q: string,
  cursor: string | null,
): string {
  const params = new URLSearchParams();
  if (bodyPart) params.set("body_part", bodyPart);
  if (equipment) params.set("equipment", equipment);
  if (q) params.set("q", q);
  if (cursor) params.set("cursor", cursor);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

/** Browsable strength exercise library with filters and name search (M2). */
export function ExerciseLibrary() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [items, setItems] = useState<ExerciseSummary[]>([]);
  const [cursor, setCursor] = useState<string | null>(null);
  const [loadingMore, setLoadingMore] = useState(false);
  const [bodyPart, setBodyPart] = useState("");
  const [equipment, setEquipment] = useState("");
  const [search, setSearch] = useState("");
  const [q, setQ] = useState("");

  useEffect(() => {
    const handle = setTimeout(() => setQ(search.trim()), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(handle);
  }, [search]);

  const fetchPage = useCallback(
    async (next: string | null) => {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>(
        `/exercises${buildQuery(bodyPart, equipment, q, next)}`,
        { token },
      );
      return exercisePageSchema.parse(raw);
    },
    [bodyPart, equipment, q],
  );

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

  return (
    <div className="space-y-4">
      <div className="grid gap-3 sm:grid-cols-3">
        <div className="space-y-1.5 sm:col-span-1">
          <Label htmlFor="exercise-search">Search</Label>
          <Input
            id="exercise-search"
            type="search"
            placeholder="e.g. bench press"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="body-part">Body part</Label>
          <select
            id="body-part"
            value={bodyPart}
            onChange={(e) => setBodyPart(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">All body parts</option>
            {BODY_PARTS.map((part) => (
              <option key={part} value={part}>
                {part}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="equipment">Equipment</Label>
          <select
            id="equipment"
            value={equipment}
            onChange={(e) => setEquipment(e.target.value)}
            className={SELECT_CLASS}
          >
            <option value="">All equipment</option>
            {EQUIPMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {type}
              </option>
            ))}
          </select>
        </div>
      </div>

      {phase === "loading" && <LoadingState rows={6} label="Loading exercises" />}
      {phase === "error" && (
        <ErrorState
          message="We couldn't load the exercise library."
          onRetry={() => void loadInitial()}
        />
      )}
      {phase === "ready" && items.length === 0 && (
        <EmptyState
          icon={Dumbbell}
          title="No exercises found"
          description="Try another search or loosen the filters."
        />
      )}

      {phase === "ready" && items.length > 0 && (
        <>
          <ul className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-4">
            {items.map((exercise, index) => (
              <li key={exercise.id}>
                <Link
                  href={`/exercises/${exercise.id}`}
                  className="block overflow-hidden rounded border border-line bg-card transition-colors hover:border-primary"
                >
                  {/* eslint-disable-next-line @next/next/no-img-element -- CDN gifs/thumbnails, no Next loader */}
                  <img
                    src={exercise.image_url}
                    alt={exercise.name}
                    loading={index < 8 ? "eager" : "lazy"}
                    className="aspect-square w-full object-cover"
                  />
                  <div className="space-y-0.5 p-3">
                    <p className="truncate font-display text-sm font-semibold text-ink">
                      {exercise.name}
                    </p>
                    <p className="truncate text-xs text-muted-foreground">
                      {exercise.target} · {exercise.equipment}
                    </p>
                  </div>
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
        </>
      )}
    </div>
  );
}
