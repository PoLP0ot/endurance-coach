"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { Loader2, Send } from "lucide-react";
import { ApiError, apiFetch } from "@/lib/api";
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

  const send = async (event: React.FormEvent) => {
    event.preventDefault();
    const text = draft.trim();
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
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          role: "assistant",
          content: "Sorry — I couldn't respond just now. Please try again.",
          created_at: null,
        },
      ]);
    } finally {
      setSending(false);
    }
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
    <div className="flex h-[calc(100vh-12rem)] flex-col">
      <div className="flex-1 space-y-3 overflow-y-auto pr-1">
        {messages.length === 0 && (
          <p className="text-sm text-muted-foreground">
            Ask your coach anything — training, recovery, or your next session.
          </p>
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
                "max-w-[80%] whitespace-pre-line rounded-md px-3 py-2 text-sm",
                m.role === "user"
                  ? "bg-primary text-primary-foreground"
                  : "border border-border bg-secondary/40",
              )}
            >
              {m.content}
            </p>
          </div>
        ))}
        {sending && (
          <div className="flex justify-start">
            <p className="flex items-center gap-2 rounded-md border border-border px-3 py-2 text-sm text-muted-foreground">
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
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
        />
        <Button type="submit" size="icon" aria-label="Send" disabled={sending}>
          <Send className="h-4 w-4" aria-hidden />
        </Button>
      </form>
    </div>
  );
}
