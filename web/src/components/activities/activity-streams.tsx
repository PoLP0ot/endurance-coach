import type { ActivityStreams, StreamSample } from "@/schemas/analysis";
import { formatDuration } from "@/lib/format";

/** Build an SVG path from numeric values, scaled to the given box. */
function linePath(
  values: Array<number | null>,
  width: number,
  height: number,
  pad = 2,
): string {
  const nums = values.filter((v): v is number => v !== null);
  if (nums.length < 2) return "";
  const min = Math.min(...nums);
  const max = Math.max(...nums);
  const span = max - min || 1;
  const n = values.length;
  let path = "";
  let started = false;
  values.forEach((v, i) => {
    if (v === null) return;
    const x = pad + (i / (n - 1)) * (width - 2 * pad);
    const y = pad + (1 - (v - min) / span) * (height - 2 * pad);
    path += `${started ? "L" : "M"}${x.toFixed(1)} ${y.toFixed(1)} `;
    started = true;
  });
  return path.trim();
}

/** Route polyline from [lat,lng] pairs, projected into an SVG viewBox. */
function RouteMap({ route }: { route: number[][] }) {
  const w = 600;
  const h = 240;
  const lats = route.map((p) => p[0]);
  const lngs = route.map((p) => p[1]);
  const minLat = Math.min(...lats);
  const maxLat = Math.max(...lats);
  const minLng = Math.min(...lngs);
  const maxLng = Math.max(...lngs);
  const latSpan = maxLat - minLat || 1;
  const lngSpan = maxLng - minLng || 1;
  // Keep aspect roughly correct: longitude degrees shrink with latitude.
  const aspect = Math.cos((((minLat + maxLat) / 2) * Math.PI) / 180);
  const pad = 16;
  const points = route
    .map((p) => {
      const x = pad + ((p[1] - minLng) / lngSpan) * (w - 2 * pad) * aspect;
      const y = pad + (1 - (p[0] - minLat) / latSpan) * (h - 2 * pad);
      return `${x.toFixed(1)},${y.toFixed(1)}`;
    })
    .join(" ");

  return (
    <div className="rounded border border-line bg-card p-4">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
        Route
      </p>
      <svg
        viewBox={`0 0 ${w} ${h}`}
        className="h-auto w-full"
        role="img"
        aria-label="Activity route"
        preserveAspectRatio="xMidYMid meet"
      >
        <polyline
          points={points}
          fill="none"
          stroke="hsl(var(--primary))"
          strokeWidth={2.5}
          strokeLinejoin="round"
          strokeLinecap="round"
        />
      </svg>
    </div>
  );
}

/** HR + elevation overlay chart from the downsampled samples. */
function range(values: Array<number | null>): [number, number] | null {
  const nums = values.filter((v): v is number => v !== null);
  if (nums.length === 0) return null;
  return [Math.min(...nums), Math.max(...nums)];
}

function StreamChart({ samples }: { samples: StreamSample[] }) {
  const w = 600;
  const h = 160;
  const hr = samples.map((s) => s.hr);
  const elev = samples.map((s) => s.elevation_m);
  const hrRange = range(hr);
  const elevRange = range(elev);
  if (!hrRange && !elevRange) return null;

  // Total elapsed time for the x-axis (last non-null sample time).
  const times = samples.map((s) => s.t).filter((t): t is number => t !== null);
  const totalS = times.length ? Math.max(...times) : 0;

  return (
    <div className="rounded border border-line bg-card p-4">
      <div className="mb-2 flex flex-wrap items-center gap-x-4 gap-y-1 font-mono text-[10px] uppercase tracking-[0.14em]">
        {hrRange && (
          <span className="text-destructive">
            — Heart rate {hrRange[0]}–{hrRange[1]} bpm
          </span>
        )}
        {elevRange && (
          <span className="text-olive">
            — Elevation {Math.round(elevRange[0])}–{Math.round(elevRange[1])} m
          </span>
        )}
      </div>
      <div className="flex gap-2">
        {/* HR y-axis scale (left) */}
        {hrRange && (
          <div className="flex w-7 flex-col justify-between py-0.5 text-right font-mono text-[9px] text-muted-foreground">
            <span>{hrRange[1]}</span>
            <span>{Math.round((hrRange[0] + hrRange[1]) / 2)}</span>
            <span>{hrRange[0]}</span>
          </div>
        )}
        <svg
          viewBox={`0 0 ${w} ${h}`}
          className="h-40 w-full"
          role="img"
          aria-label="Heart rate and elevation over the activity"
          preserveAspectRatio="none"
        >
          {elevRange && (
            <path
              d={linePath(elev, w, h)}
              fill="none"
              stroke="hsl(var(--olive))"
              strokeWidth={1.5}
              opacity={0.6}
              vectorEffect="non-scaling-stroke"
            />
          )}
          {hrRange && (
            <path
              d={linePath(hr, w, h)}
              fill="none"
              stroke="hsl(var(--destructive))"
              strokeWidth={1.5}
              vectorEffect="non-scaling-stroke"
            />
          )}
        </svg>
      </div>
      {/* time x-axis */}
      <div className="ml-9 flex justify-between font-mono text-[9px] text-muted-foreground">
        <span>0:00</span>
        <span>{formatDuration(Math.round(totalS / 2))}</span>
        <span>{formatDuration(totalS)}</span>
      </div>
    </div>
  );
}

/** Per-kilometre splits table with a relative pace bar. */
function SplitsTable({ splits }: { splits: ActivityStreams["splits"] }) {
  if (splits.length === 0) return null;
  const slowest = Math.max(...splits.map((s) => s.duration_s));
  return (
    <div className="rounded border border-line bg-card">
      <p className="border-b border-line px-4 py-3 font-mono text-[10px] uppercase tracking-[0.14em] text-muted-foreground">
        Splits · per km
      </p>
      <div className="divide-y divide-line/60">
        {splits.map((s) => (
          <div key={s.km} className="flex items-center gap-3 px-4 py-2 text-sm">
            <span className="w-8 font-mono text-xs text-muted-foreground">
              {s.km}
            </span>
            <div className="h-2 flex-1 overflow-hidden rounded-full bg-secondary">
              <div
                className="h-full rounded-full bg-primary"
                style={{ width: `${(s.duration_s / slowest) * 100}%` }}
              />
            </div>
            <span className="w-14 text-right tabular-nums text-ink">
              {formatDuration(s.duration_s)}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/** Map + HR/elevation chart + splits, all from real stored streams (US3/2.4). */
export function ActivityStreamsView({ streams }: { streams: ActivityStreams }) {
  const hasContent =
    streams.has_route ||
    streams.splits.length > 0 ||
    streams.samples.some((s) => s.hr !== null || s.elevation_m !== null);
  if (!hasContent) return null;

  return (
    <div className="space-y-4">
      {streams.has_route && <RouteMap route={streams.route} />}
      <StreamChart samples={streams.samples} />
      <SplitsTable splits={streams.splits} />
    </div>
  );
}
