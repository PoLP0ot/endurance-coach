import { SessionRunner } from "@/components/strength/session-runner";

export default async function StrengthSessionPage({
  searchParams,
}: {
  searchParams: Promise<{ week?: string; day?: string }>;
}) {
  const { week, day } = await searchParams;
  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        Today&apos;s session
      </h1>
      <SessionRunner week={Number(week ?? 1)} day={Number(day ?? 0)} />
    </div>
  );
}
