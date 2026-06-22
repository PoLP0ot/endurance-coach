import { ActivityList } from "@/components/activities/activity-list";

export default function ActivitiesPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        Activity history
      </h1>
      <ActivityList />
    </div>
  );
}
