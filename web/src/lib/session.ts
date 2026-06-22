import { createClient } from "@/lib/supabase/client";

/** Resolve the current Supabase access token for Bearer auth to the API. */
export async function getAccessToken(): Promise<string | undefined> {
  const {
    data: { session },
  } = await createClient().auth.getSession();
  return session?.access_token;
}
