"use client";

import { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2, Lock, ShieldCheck, Watch } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { ApiError, apiFetch } from "@/lib/api";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";

type Phase = "idle" | "importing" | "mfa";

interface ConnectResponse {
  job_id: string;
}

interface ImportStatus {
  status: "queued" | "running" | "done" | "error";
  progress_label: string | null;
}

/** Human message for each typed Garmin connect failure. */
function connectErrorMessage(err: unknown): string {
  if (err instanceof ApiError) {
    if (err.status === 401) {
      return "Garmin didn't accept those credentials. Check your Garmin email and password.";
    }
    if (err.status === 423) {
      return "Your Garmin account is temporarily locked after too many attempts. Wait a few minutes, then try again.";
    }
  }
  return "We couldn't connect to Garmin. Please try again.";
}

async function getToken(): Promise<string | undefined> {
  const supabase = createClient();
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.access_token;
}

/** Onboarding: connect Garmin (incl. MFA), then poll import progress (US1.12, S2). */
export function ConnectGarmin() {
  const router = useRouter();
  const [phase, setPhase] = useState<Phase>("idle");
  const [error, setError] = useState<string | null>(null);
  const [label, setLabel] = useState("Importing your Garmin data…");

  const poll = async (jobId: string, token: string | undefined) => {
    const status = await apiFetch<ImportStatus>(
      `/garmin/import-status/${jobId}`,
      { token },
    );
    if (status.progress_label) setLabel(status.progress_label);
    if (status.status === "done") {
      router.push("/dashboard");
    } else if (status.status === "error") {
      setPhase("idle");
      setError(
        "The import failed partway. Your connection is saved — try a sync from Settings.",
      );
    } else {
      setTimeout(() => void poll(jobId, token), 1500);
    }
  };

  const onSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError(null);
    setPhase("importing");
    try {
      const token = await getToken();
      const { job_id } = await apiFetch<ConnectResponse>("/garmin/connect", {
        method: "POST",
        token,
        body: JSON.stringify({
          username: form.get("username"),
          password: form.get("password"),
        }),
      });
      await poll(job_id, token);
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setPhase("mfa");
        return;
      }
      setPhase("idle");
      setError(connectErrorMessage(err));
    }
  };

  const onSubmitCode = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    setError(null);
    try {
      const token = await getToken();
      const { job_id } = await apiFetch<ConnectResponse>("/garmin/mfa", {
        method: "POST",
        token,
        body: JSON.stringify({ code: form.get("code") }),
      });
      setPhase("importing");
      await poll(job_id, token);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        setError("That code didn't match — check it and try again.");
        return; // stay on the MFA step, the challenge is still open
      }
      if (err instanceof ApiError && err.status === 410) {
        setPhase("idle");
        setError(
          "The verification window expired. Enter your credentials again to get a new code.",
        );
        return;
      }
      setPhase("idle");
      setError(connectErrorMessage(err));
    }
  };

  if (phase === "importing") {
    return (
      <div className="flex flex-col items-center gap-4 text-center">
        <Loader2 className="h-8 w-8 animate-spin text-accent" aria-hidden />
        <p role="status" className="text-sm text-muted-foreground">
          {label}
        </p>
      </div>
    );
  }

  if (phase === "mfa") {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-center gap-3 text-accent">
          <ShieldCheck className="h-8 w-8" aria-hidden />
        </div>
        <p className="text-center text-sm text-muted-foreground">
          Garmin sent a verification code to your email or authenticator app.
          Enter it to finish connecting.
        </p>
        <form onSubmit={onSubmitCode} className="space-y-4" noValidate>
          <div className="space-y-1.5">
            <Label htmlFor="code">Verification code</Label>
            <Input
              id="code"
              name="code"
              inputMode="numeric"
              autoComplete="one-time-code"
              autoFocus
            />
          </div>
          {error && (
            <p role="alert" className="text-sm text-destructive">
              {error}
            </p>
          )}
          <Button type="submit" className="w-full">
            Verify
          </Button>
        </form>
        <p className="text-center text-sm">
          <button
            type="button"
            onClick={() => {
              setPhase("idle");
              setError(null);
            }}
            className="text-muted-foreground underline-offset-4 hover:underline"
          >
            Start over
          </button>
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-center gap-3 text-accent">
        <Watch className="h-8 w-8" aria-hidden />
      </div>
      <form onSubmit={onSubmit} className="space-y-4" noValidate>
        <div className="space-y-1.5">
          <Label htmlFor="username">Garmin email</Label>
          <Input id="username" name="username" type="email" autoComplete="username" />
        </div>
        <div className="space-y-1.5">
          <Label htmlFor="password">Garmin password</Label>
          <Input
            id="password"
            name="password"
            type="password"
            autoComplete="current-password"
          />
        </div>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <Button type="submit" className="w-full">
          Connect Garmin
        </Button>
      </form>
      <p className="flex items-center justify-center gap-2 text-center text-xs text-muted-foreground">
        <Lock className="h-3 w-3" aria-hidden />
        Your data is encrypted. We never share it. You can revoke access anytime.
      </p>
      <p className="text-center text-sm">
        <Link
          href="/dashboard"
          className="text-muted-foreground underline-offset-4 hover:underline"
        >
          I&apos;ll do this later
        </Link>
      </p>
    </div>
  );
}
