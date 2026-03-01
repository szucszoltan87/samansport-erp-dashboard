/**
 * check-freshness Edge Function
 *
 * Lightweight endpoint: returns sync status for a given entity+filter combo.
 * No SOAP calls — just reads sync_metadata.
 *
 * Request body: { entity: string, filters?: { start_date?, end_date?, cikkszam? } }
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseAdmin } from "../_shared/supabase-admin.ts";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

async function computeFilterHash(entity: string, filters: Record<string, unknown>): Promise<string> {
  const input = JSON.stringify({ entity, ...filters });
  const data = new TextEncoder().encode(input);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: CORS_HEADERS });
  }

  try {
    const { entity, filters = {} } = await req.json();

    if (!entity) {
      return new Response(
        JSON.stringify({ error: "Missing entity parameter" }),
        { status: 400, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    const supabase = getSupabaseAdmin();
    const filterHash = await computeFilterHash(entity, filters);

    // Get sync metadata
    const { data: meta } = await supabase
      .from("sync_metadata")
      .select("*")
      .eq("entity", entity)
      .eq("filter_hash", filterHash)
      .single();

    // Get entity config for TTL
    const { data: config } = await supabase
      .from("entity_config")
      .select("ttl_seconds")
      .eq("entity", entity)
      .single();

    const ttlSeconds = config?.ttl_seconds || 1800;

    if (!meta) {
      return new Response(
        JSON.stringify({
          is_fresh: false,
          has_data: false,
          sync_status: "never_synced",
          last_synced_at: null,
          ttl_seconds: ttlSeconds,
        }),
        { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    const lastSynced = meta.last_synced_at ? new Date(meta.last_synced_at) : null;
    const ageSeconds = lastSynced
      ? (Date.now() - lastSynced.getTime()) / 1000
      : Infinity;
    const isFresh = ageSeconds < ttlSeconds;

    return new Response(
      JSON.stringify({
        is_fresh: isFresh,
        has_data: meta.records_synced > 0,
        sync_status: meta.sync_status,
        last_synced_at: meta.last_synced_at,
        age_seconds: Math.round(ageSeconds),
        ttl_seconds: ttlSeconds,
        records_synced: meta.records_synced,
        error_message: meta.error_message,
      }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ error: (error as Error).message }),
      { status: 500, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  }
});
