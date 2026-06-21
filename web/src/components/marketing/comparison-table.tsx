import { Check, X, Minus } from "lucide-react";
import { cn } from "@/lib/utils";

type Cell = "yes" | "no" | "partial" | string;

const COLUMNS = [
  "Endurance Coach",
  "Garmin Connect",
  "Strava",
  "TrainingPeaks",
] as const;

const ROWS: { feature: string; cells: Cell[] }[] = [
  { feature: "Import Garmin data", cells: ["yes", "yes", "yes", "yes"] },
  { feature: "Deep analytics", cells: ["yes", "partial", "yes", "yes"] },
  { feature: "AI Coach (chat)", cells: ["yes", "no", "no", "no"] },
  { feature: "Adaptive training plan", cells: ["yes", "partial", "no", "no"] },
  { feature: "Price / month", cells: ["$8", "$6.99", "$11.99", "$19.95"] },
];

function CellValue({ value }: { value: Cell }) {
  if (value === "yes") {
    return (
      <>
        <Check className="mx-auto h-4 w-4 text-success" aria-hidden />
        <span className="sr-only">Yes</span>
      </>
    );
  }
  if (value === "no") {
    return (
      <>
        <X className="mx-auto h-4 w-4 text-muted-foreground" aria-hidden />
        <span className="sr-only">No</span>
      </>
    );
  }
  if (value === "partial") {
    return (
      <>
        <Minus className="mx-auto h-4 w-4 text-warning" aria-hidden />
        <span className="sr-only">Limited</span>
      </>
    );
  }
  return <span className="font-mono tabular-nums">{value}</span>;
}

/** Competitor comparison table with our column highlighted (1.5). */
export function ComparisonTable() {
  return (
    <section className="container py-20">
      <h2 className="text-center font-display text-3xl font-bold tracking-tight">
        How we compare
      </h2>
      <div className="mt-10 overflow-x-auto">
        <table className="w-full min-w-[640px] border-collapse text-sm">
          <thead>
            <tr className="border-b border-border">
              <th scope="col" className="px-4 py-3 text-left font-medium">
                Feature
              </th>
              {COLUMNS.map((col, index) => (
                <th
                  key={col}
                  scope="col"
                  data-highlighted={index === 0 ? "true" : undefined}
                  className={cn(
                    "px-4 py-3 text-center font-medium",
                    index === 0 && "bg-accent/10 text-foreground",
                  )}
                >
                  {col}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {ROWS.map((row) => (
              <tr key={row.feature} className="border-b border-border">
                <th
                  scope="row"
                  className="px-4 py-3 text-left font-normal text-muted-foreground"
                >
                  {row.feature}
                </th>
                {row.cells.map((cell, index) => (
                  <td
                    key={`${row.feature}-${index}`}
                    data-highlighted={index === 0 ? "true" : undefined}
                    className={cn(
                      "px-4 py-3 text-center",
                      index === 0 && "bg-accent/10 font-medium",
                    )}
                  >
                    <CellValue value={cell} />
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
