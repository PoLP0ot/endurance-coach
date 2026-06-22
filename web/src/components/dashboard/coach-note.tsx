interface CoachNoteProps {
  headline: string;
  detail: string;
}

/** Coach-first narrative shown before raw data (US2, coach-first philosophy). */
export function CoachNote({ headline, detail }: CoachNoteProps) {
  return (
    <section
      aria-label="Coach summary"
      className="rounded-md border-l-2 border-primary bg-secondary/40 p-5"
    >
      <h2 className="font-display text-xl font-semibold tracking-tight">
        {headline}
      </h2>
      <p className="mt-1 text-sm text-muted-foreground">{detail}</p>
    </section>
  );
}
