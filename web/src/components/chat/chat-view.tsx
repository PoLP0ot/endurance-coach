"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Loader2, Send } from "lucide-react";
import { ApiError, apiFetch, isCoachUnavailable } from "@/lib/api";
import { getAccessToken } from "@/lib/session";
import {
  chatHistorySchema,
  chatMessageSchema,
  type ChatMessage,
} from "@/schemas/chat";
import { cn } from "@/lib/utils";
import { ErrorState } from "@/components/states/error-state";
import { LoadingState } from "@/components/states/loading-state";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

type Phase = "loading" | "error" | "premium" | "ready";

/** Grounded conversation starters shown while the thread is empty. */
const STARTERS = [
  "What should I do today?",
  "Am I on track for my goal?",
  "How is my recovery?",
  "Was my last session any good?",
] as const;

/** Conversational coach (US4): grounded chat with optimistic send (premium). */
export function ChatView() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    setPhase("loading");
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/chat/messages", { token });
      setMessages(chatHistorySchema.parse(raw).messages);
      setPhase("ready");
    } catch (err) {
      setPhase(err instanceof ApiError && err.status === 402 ? "premium" : "error");
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, sending]);

  const sendText = async (raw: string) => {
    const text = raw.trim();
    if (!text || sending) return;
    setDraft("");
    setSending(true);
    const optimistic: ChatMessage = {
      id: Date.now(),
      role: "user",
      content: text,
      created_at: null,
    };
    setMessages((prev) => [...prev, optimistic]);
    try {
      const token = await getAccessToken();
      const raw = await apiFetch<unknown>("/chat", {
        method: "POST",
        token,
        body: JSON.stringify({ message: text }),
      });
      setMessages((prev) => [...prev, chatMessageSchema.parse(raw)]);
    } catch (err) {
      const content = isCoachUnavailable(err)
        ? "Your coach is temporarily unavailable. Please try again in a moment."
        : "Sorry — I couldn't respond just now. Please try again.";
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content,
          created_at: null,
        },
      ]);
    } finally {
      setSending(false);
    }
  };

  const send = (event: React.FormEvent) => {
    event.preventDefault();
    void sendText(draft);
  };

  if (phase === "loading") return <LoadingState rows={4} label="Loading your coach" />;
  if (phase === "error") {
    return (
      <ErrorState message="We couldn't load your coach." onRetry={() => void load()} />
    );
  }
  if (phase === "premium") {
    return (
      <div className="rounded-md border border-border p-6 text-center">
        <h2 className="font-display text-lg font-semibold">Coach chat is premium</h2>
        <p className="mt-2 text-sm text-muted-foreground">
          Upgrade to chat with your AI coach anytime.
        </p>
        <Button asChild className="mt-4">
          <Link href="/settings/subscription">Upgrade to Premium</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-9rem)] flex-col">
      <div className="mb-4 border-b border-line pb-4">
        <h1 className="flex items-center gap-3 font-display text-xl font-semibold tracking-tight text-ink">
          Coach
          <span className="flex items-center gap-1.5 font-mono text-[10px] uppercase tracking-[0.12em] text-olive">
            <span className="h-1.5 w-1.5 rounded-full bg-olive" aria-hidden />
            Online
          </span>
        </h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Ask me anything about your training. I know your Garmin data.
        </p>
      </div>

      <div className="flex-1 space-y-4 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <div className="space-y-3">
            <p className="text-sm text-muted-foreground">
              Ask your coach anything — training, recovery, or your next
              session.
            </p>
            <div className="flex flex-wrap gap-2">
              {STARTERS.map((q) => (
                <button
                  key={q}
                  type="button"
                  onClick={() => void sendText(q)}
                  disabled={sending}
                  className="rounded-full border border-line bg-card px-3.5 py-2 text-[13px] text-ink-soft transition-colors hover:border-primary hover:text-ink focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn(
              "flex",
              m.role === "user" ? "justify-end" : "justify-start",
            )}
          >
            <p
              className={cn(
                "max-w-[84%] whitespace-pre-line rounded-[12px] px-4 py-3 text-[14.5px] leading-relaxed",
                m.role === "user"
                  ? "rounded-tr-[3px] bg-ink text-paper"
                  : "rounded-tl-[3px] border border-line bg-card text-ink-soft",
              )}
            >
              {m.content}
            </p>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <p className="flex items-center gap-2 rounded-[12px] rounded-tl-[3px] border border-line bg-card px-4 py-3 text-[14.5px] text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" aria-hidden />
              Coach is thinking…
            </p>
          </div>
        )}
        <div ref={endRef} />
      </div>

      <form onSubmit={send} className="mt-4 flex items-center gap-2">
        <Input
          aria-label="Message your coach"
          placeholder="Message your coach…"
          className="rounded-full"
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <Button
          type="submit"
          size="icon"
          aria-label="Send"
          className="shrink-0 rounded-full"
          disabled={sending}
        >
          <Send className="h-4 w-4" aria-hidden />
        </Button>
      </form>
    </div>
  );
}
