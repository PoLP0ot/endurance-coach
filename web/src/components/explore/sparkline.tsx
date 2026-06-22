interface SparklineProps {
  points: number[];
  width?: number;
  height?: number;
  className?: string;
}

/** Minimal inline SVG sparkline. Renders nothing for < 2 points. */
export function Sparkline({
  points,
  width = 240,
  height = 44,
  className,
}: SparklineProps) {
  if (points.length < 2) return null;
  const min = Math.min(...points);
  const max = Math.max(...points);
  const range = max - min || 1;
  const dx = width / (points.length - 1);
  const d = points
    .map((p, i) => {
      const x = (i * dx).toFixed(1);
      const y = (height - ((p - min) / range) * (height - 4) - 2).toFixed(1);
      return `${i === 0 ? "M" : "L"}${x},${y}`;
    })
    .join(" ");
  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className={className}
      role="img"
      aria-hidden
      preserveAspectRatio="none"
    >
      <path
        d={d}
        fill="none"
        stroke="currentColor"
        strokeWidth={2}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}
