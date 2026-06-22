import Link from "next/link";
import { PrivacyView } from "@/components/settings/privacy-view";

export default function PrivacyPage() {
  return (
    <div className="space-y-6">
      <div>
        <Link
          href="/settings"
          className="text-sm text-muted-foreground underline-offset-4 hover:underline"
        >
          ← Settings
        </Link>
        <h1 className="mt-2 font-display text-2xl font-semibold tracking-tight">
          Privacy &amp; data
        </h1>
      </div>
      <PrivacyView />
    </div>
  );
}
