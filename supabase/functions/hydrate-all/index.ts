/**
 * hydrate-all Edge Function
 *
 * Admin-triggered initial data load. Iterates through all entities and
 * date ranges, calling sync-entity for each chunk.
 *
 * For sales and movements: loads in monthly chunks from 2010 to present.
 * For inventory and products: single sync (no date dimension).
 *
 * Request body: {
 *   start_year?: number (default 2010),
 *   entities?: string[] (default all),
 *   delay_ms?: number (default 1000)
 * }
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { getSupabaseAdmin } from "../_shared/supabase-admin.ts";
import { ENTITIES } from "../_shared/constants.ts";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function lastDayOfMonth(year: number, month: number): number {
  return new Date(year, month, 0).getDate();
}

/** Invoke the sync-entity function for a specific entity+filters combo. */
async function invokeSyncEntity(
  supabaseUrl: string,
  serviceRoleKey: string,
  entity: string,
  filters: Record<string, string>
): Promise<{ status: string; records?: number; error?: string }> {
  const response = await fetch(`${supabaseUrl}/functions/v1/sync-entity`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${serviceRoleKey}`,
    },
    body: JSON.stringify({ entity, filters }),
  });

  return await response.json();
}

serve(async (req: Request) => {
  if (req.method === "OPTIONS") {
    return new Response("ok", { headers: CORS_HEADERS });
  }

  try {
    const body = await req.json().catch(() => ({}));
    const startYear = body.start_year || 2010;
    const delayMs = body.delay_ms || 1000;
    const requestedEntities: string[] = body.entities || [
      ENTITIES.PRODUCTS,
      ENTITIES.INVENTORY,
      ENTITIES.SALES,
      ENTITIES.MOVEMENTS,
    ];

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1;

    const results: Array<{
      entity: string;
      chunk: string;
      status: string;
      records?: number;
      error?: string;
    }> = [];

    for (const entity of requestedEntities) {
      if (entity === ENTITIES.PRODUCTS || entity === ENTITIES.INVENTORY) {
        // No date dimension — single sync
        const result = await invokeSyncEntity(supabaseUrl, serviceRoleKey, entity, {});
        results.push({ entity, chunk: "full", ...result });
        await sleep(delayMs);
      } else {
        // Date-based entities: iterate monthly chunks
        for (let year = startYear; year <= currentYear; year++) {
          const maxMonth = year === currentYear ? currentMonth : 12;
          for (let month = 1; month <= maxMonth; month++) {
            const startDate = `${year}.${String(month).padStart(2, "0")}.01`;
            const lastDay = lastDayOfMonth(year, month);
            const endDate = `${year}.${String(month).padStart(2, "0")}.${String(lastDay).padStart(2, "0")}`;

            const chunkLabel = `${year}-${String(month).padStart(2, "0")}`;

            const result = await invokeSyncEntity(supabaseUrl, serviceRoleKey, entity, {
              start_date: startDate,
              end_date: endDate,
            });

            results.push({ entity, chunk: chunkLabel, ...result });

            // Delay between chunks to avoid overwhelming the SOAP endpoint
            await sleep(delayMs);
          }
        }
      }
    }

    const totalRecords = results.reduce((sum, r) => sum + (r.records || 0), 0);
    const errors = results.filter((r) => r.status === "error");

    return new Response(
      JSON.stringify({
        status: "completed",
        total_chunks: results.length,
        total_records: totalRecords,
        errors: errors.length,
        details: results,
      }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ status: "error", error: (error as Error).message }),
      { status: 500, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  }
});
