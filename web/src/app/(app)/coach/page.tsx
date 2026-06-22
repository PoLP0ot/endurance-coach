import { ChatView } from "@/components/chat/chat-view";

export default function CoachPage() {
  return (
    <div className="space-y-4">
      <h1 className="font-display text-2xl font-semibold tracking-tight">Coach</h1>
      <ChatView />
    </div>
  );
}
