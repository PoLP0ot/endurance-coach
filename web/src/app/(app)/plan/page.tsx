import { PlanView } from "@/components/plan/plan-view";

export default function PlanPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        Training plan
      </h1>
      <PlanView />
    </div>
  );
}
