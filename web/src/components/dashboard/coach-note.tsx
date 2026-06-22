interface CoachNoteProps {
  headline: string;
  detail: string;
}

/** Coach's Assessment card (prototype): ai-dot header + THIS WEEK badge, then narrative. */
export function CoachNote({ headline, detail }: CoachNoteProps) {
  return (
    <section
      aria-label="Coach summary"
      className="rounded border border-line bg-card"
    >
      <div className="flex items-center gap-2.5 px-6 pt-4">
        <span className="h-2 w-2 flex-none rounded-full bg-primary" aria-hidden />
        <h2 className="font-display text-sm font-semibold text-ink">
          Coach&apos;s Assessment
        </h2>
        <span className="ml-auto font-mono text-[9px] uppercase tracking-[0.14em] text-primary">
          This week
        </span>
      </div>
      <div className="px-6 pb-5 pt-3.5">
        <p className="text-[15px] leading-[1.72] text-ink-soft">
          <b className="font-semibold text-ink">{headline}</b> {detail}
        </p>
      </div>
    </section>
  );
}
