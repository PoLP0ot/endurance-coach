"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { ChevronRight } from "lucide-react";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { profileSchema, type Profile } from "@/schemas/profile";
import { GOALS } from "@/schemas/plan";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Switch } from "@/components/ui/switch";

type Phase = "loading" | "error" | "ready";

/** Account settings: profile, goal, units, email preference (US11a). */
export function SettingsView() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [profile, setProfile] = useState<Profile | null>(null);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/profile", { token });
      setProfile(profileSchema.parse(raw));
      setPhase("ready");
    } catch {
      setPhase("error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const patch = (fields: Partial<Profile>) =>
    setProfile((prev) => (prev ? { ...prev, ...fields } : prev));

  const save = async () => {
    if (!profile) return;
    setSaving(true);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/profile", {
        method: "PATCH",
        token,
        body: JSON.stringify({
          display_name: profile.display_name,
          primary_goal: profile.primary_goal,
          units: profile.units,
          weekly_email_opt_in: profile.weekly_email_opt_in,
        }),
      });
      setProfile(profileSchema.parse(raw));
      toast.success("Settings saved");
    } catch {
      toast.error("We couldn't save your settings.");
    } finally {
      setSaving(false);
    }
  };

  if (phase === "loading") return <LoadingState rows={4} label="Loading settings" />;
  if (phase === "error" || !profile) {
    return <ErrorState message="We couldn't load your settings." onRetry={() => void load()} />;
  }

  return (
    <div className="space-y-6">
      <div className="space-y-4 rounded-md border border-border p-5">
        <div className="space-y-1.5">
          <Label htmlFor="display_name">Display name</Label>
          <Input
            id="display_name"
            value={profile.display_name ?? ""}
            onChange={(e) => patch({ display_name: e.target.value })}
          />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="goal">Primary goal</Label>
          <select
            id="goal"
            value={profile.primary_goal ?? ""}
            onChange={(e) => patch({ primary_goal: e.target.value || null })}
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="">Not set</option>
            {GOALS.map((g) => (
              <option key={g.value} value={g.value}>
                {g.label}
              </option>
            ))}
          </select>
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="units">Units</Label>
          <select
            id="units"
            value={profile.units}
            onChange={(e) =>
              patch({ units: e.target.value as Profile["units"] })
            }
            className="h-9 w-full rounded-md border border-input bg-background px-3 text-sm"
          >
            <option value="metric">Metric (km)</option>
            <option value="imperial">Imperial (mi)</option>
          </select>
        </div>
        <div className="flex items-center justify-between">
          <Label htmlFor="weekly-email">Weekly coaching email</Label>
          <Switch
            id="weekly-email"
            checked={profile.weekly_email_opt_in}
            onCheckedChange={(v) => patch({ weekly_email_opt_in: v })}
          />
        </div>
        <Button onClick={save} disabled={saving}>
          {saving ? "Saving…" : "Save changes"}
        </Button>
      </div>

      <nav className="divide-y divide-border rounded-md border border-border">
        <Link
          href="/settings/subscription"
          className="flex items-center justify-between px-4 py-3 text-sm hover:bg-secondary/50"
        >
          Subscription
          <ChevronRight className="h-4 w-4 text-muted-foreground" aria-hidden />
        </Link>
        <Link
          href="/settings/privacy"
          className="flex items-center justify-between px-4 py-3 text-sm hover:bg-secondary/50"
        >
          Privacy &amp; data
          <ChevronRight className="h-4 w-4 text-muted-foreground" aria-hidden />
        </Link>
      </nav>
    </div>
  );
}
