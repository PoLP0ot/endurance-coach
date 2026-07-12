import { ExerciseLibrary } from "@/components/exercises/exercise-library";

export default function ExercisesPage() {
  return (
    <div className="space-y-6">
      <h1 className="font-display text-2xl font-semibold tracking-tight">
        Exercise library
      </h1>
      <ExerciseLibrary />
    </div>
  );
}
