"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { apiFetch } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";

/** GDPR self-service: export a data bundle or erase the account (US11b). */
export function PrivacyView() {
  const router = useRouter();
  const [exporting, setExporting] = useState(false);
  const [confirming, setConfirming] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const exportData = async () => {
    setExporting(true);
    try {
      const token = await getAccessToken();
      const bundle = await apiFetch<unknown>("/gdpr/export", { token });
      const blob = new Blob([JSON.stringify(bundle, null, 2)], {
        type: "application/json",
      });
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = "endurance-coach-export.json";
      link.click();
      URL.revokeObjectURL(url);
      toast.success("Your data export has downloaded.");
    } catch {
      toast.error("We couldn't export your data. Please try again.");
    } finally {
      setExporting(false);
    }
  };

  const deleteAccount = async () => {
    setDeleting(true);
    try {
      const token = await getAccessToken();
      await apiFetch("/gdpr/account", { method: "DELETE", token });
      await createClient().auth.signOut();
      toast.success("Your account and data have been deleted.");
      router.push("/");
    } catch {
      toast.error("We couldn't delete your account. Please try again.");
      setDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <section className="rounded-md border border-border p-5">
        <h2 className="font-display text-lg font-semibold">Export your data</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Download everything we hold about you as a JSON file (activities, health,
          chat, plans).
        </p>
        <Button className="mt-4" variant="outline" onClick={exportData} disabled={exporting}>
          {exporting ? "Preparing…" : "Export my data"}
        </Button>
      </section>

      <section className="rounded-md border border-destructive/40 p-5">
        <h2 className="font-display text-lg font-semibold">Delete your account</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Permanently erase your account and all associated data. This can&apos;t be
          undone.
        </p>
        {!confirming ? (
          <Button
            className="mt-4"
            variant="destructive"
            onClick={() => setConfirming(true)}
          >
            Delete my account
          </Button>
        ) : (
          <div className="mt-4 flex items-center gap-3">
            <Button variant="destructive" onClick={deleteAccount} disabled={deleting}>
              {deleting ? "Deleting…" : "Yes, permanently delete"}
            </Button>
            <Button variant="ghost" onClick={() => setConfirming(false)}>
              Cancel
            </Button>
          </div>
        )}
      </section>
    </div>
  );
}
