/**
 * sync-entity Edge Function
 *
 * Core sync orchestrator: checks freshness, claims debounce lock,
 * paginates through the Tharanis SOAP API, and upserts records into Supabase.
 *
 * Request body: { entity: string, filters?: { start_date?, end_date?, cikkszam? } }
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseAdmin } from "../_shared/supabase-admin.ts";
import { buildLekerXml, postSoap } from "../_shared/soap-client.ts";
import { extractValasz, countElems, parseRecords } from "../_shared/xml-parser.ts";
import { TABLES } from "../_shared/constants.ts";
import type { SyncRequest } from "../_shared/types.ts";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

/** Compute a stable hash for filter deduplication. */
async function computeFilterHash(entity: string, filters: Record<string, unknown>): Promise<string> {
  const input = JSON.stringify({ entity, ...filters });
  const data = new TextEncoder().encode(input);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** Upsert records into the appropriate Supabase table. */
async function upsertRecords(
  supabase: ReturnType<typeof getSupabaseAdmin>,
  entity: string,
  records: Array<Record<string, unknown>>
): Promise<void> {
  const tableName = TABLES[entity as keyof typeof TABLES];
  if (!tableName) throw new Error(`No table mapping for entity: ${entity}`);

  if (records.length === 0) return;

  if (entity === "keszlet") {
    // Inventory is a snapshot: upsert on SKU
    const { error } = await supabase
      .from(tableName)
      .upsert(records.map((r) => ({ ...r, synced_at: new Date().toISOString() })), {
        onConflict: "sku",
      });
    if (error) throw new Error(`Upsert error (${tableName}): ${error.message}`);
  } else if (entity === "cikk") {
    // Products: upsert on SKU
    const { error } = await supabase
      .from(tableName)
      .upsert(records.map((r) => ({ ...r, synced_at: new Date().toISOString() })), {
        onConflict: "sku",
      });
    if (error) throw new Error(`Upsert error (${tableName}): ${error.message}`);
  } else {
    // Sales and movements: insert with conflict ignore (dedup via unique constraint)
    // Process in batches of 500 to avoid payload limits
    const batchSize = 500;
    for (let i = 0; i < records.length; i += batchSize) {
      const batch = records.slice(i, i + batchSize).map((r) => ({
        ...r,
        synced_at: new Date().toISOString(),
      }));
      const { error } = await supabase
        .from(tableName)
        .upsert(batch, {
          onConflict:
            entity === "kimeno_szamla"
              ? "fulfillment_date,sku,quantity,net_price,raw_xml_hash"
              : "movement_date,sku,direction,quantity,raw_xml_hash",
          ignoreDuplicates: true,
        });
      if (error) throw new Error(`Upsert error (${tableName}): ${error.message}`);
    }
  }
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: CORS_HEADERS });
  }

  try {
    const { entity, filters = {} } = (await req.json()) as SyncRequest;

    if (!entity) {
      return new Response(
        JSON.stringify({ status: "error", error: "Missing entity parameter" }),
        { status: 400, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    const supabase = getSupabaseAdmin();

    // 1. Get entity config for TTL and page size
    const { data: config } = await supabase
      .from("entity_config")
      .select("ttl_seconds, page_size, enabled")
      .eq("entity", entity)
      .single();

    if (!config?.enabled) {
      return new Response(
        JSON.stringify({ status: "disabled", entity }),
        { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    const ttl = config.ttl_seconds;
    const pageSize = config.page_size;

    // 2. Compute filter hash for debouncing
    const filterHash = await computeFilterHash(entity, filters || {});

    // 3. Try to claim sync lock (debouncing)
    const { data: lockAcquired } = await supabase.rpc("claim_sync_lock", {
      p_entity: entity,
      p_filter_hash: filterHash,
      p_filter_params: { entity, ...(filters || {}) },
      p_ttl_seconds: ttl,
    });

    if (!lockAcquired) {
      return new Response(
        JSON.stringify({
          status: "skipped",
          reason: "Data is fresh or another sync is in progress",
        }),
        { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
      );
    }

    // 4. Paginate through SOAP API
    let page = 0;
    let totalRecords = 0;
    let hasMore = true;

    while (hasMore) {
      const lekerXml = buildLekerXml(entity, filters, page, pageSize);
      const soapResponse = await postSoap(entity, lekerXml);
      const valaszXml = extractValasz(soapResponse);

      if (!valaszXml) {
        hasMore = false;
        break;
      }

      const elemCount = countElems(valaszXml);
      const records = await parseRecords(entity, valaszXml, filters?.cikkszam);

      // 5. Upsert into Supabase
      await upsertRecords(supabase, entity, records as Array<Record<string, unknown>>);

      totalRecords += records.length;
      hasMore = elemCount >= pageSize;
      page++;
    }

    // 6. Release lock with success
    await supabase.rpc("release_sync_lock", {
      p_entity: entity,
      p_filter_hash: filterHash,
      p_records_synced: totalRecords,
      p_pages_fetched: page,
    });

    return new Response(
      JSON.stringify({ status: "synced", records: totalRecords, pages: page }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  } catch (error) {
    // Try to release lock on error
    try {
      const body = await req.clone().json();
      const supabase = getSupabaseAdmin();
      const filterHash = await computeFilterHash(body.entity, body.filters || {});
      await supabase.rpc("release_sync_lock", {
        p_entity: body.entity,
        p_filter_hash: filterHash,
        p_records_synced: 0,
        p_pages_fetched: 0,
        p_error: (error as Error).message,
      });
    } catch {
      // Lock release failed too — it will expire via the 5-min timeout
    }

    return new Response(
      JSON.stringify({ status: "error", error: (error as Error).message }),
      { status: 500, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  }
});
