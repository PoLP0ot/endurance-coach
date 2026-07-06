import { redirect } from "next/navigation";

/** Signals now live on the dashboard; keep old links working. */
export default function ExplorePage() {
  redirect("/dashboard");
}
