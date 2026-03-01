/**
 * cron-refresh Edge Function
 *
 * Scheduled background refresh of high-priority entities.
 * Designed to be triggered by pg_cron or an external scheduler.
 *
 * Refreshes:
 * - Inventory (keszlet) — always (5 min TTL)
 * - Sales (kimeno_szamla) — current month only (30 min TTL)
 * - Movements (raktari_mozgas) — current month only (30 min TTL)
 */

import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { ENTITIES } from "../_shared/constants.ts";

const CORS_HEADERS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type",
};

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
    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;

    const now = new Date();
    const year = now.getFullYear();
    const month = now.getMonth() + 1;
    const lastDay = new Date(year, month, 0).getDate();

    const startDate = `${year}.${String(month).padStart(2, "0")}.01`;
    const endDate = `${year}.${String(month).padStart(2, "0")}.${String(lastDay).padStart(2, "0")}`;

    const results: Array<{ entity: string; status: string; records?: number; error?: string }> = [];

    // 1. Refresh inventory (no date filter)
    const invResult = await invokeSyncEntity(supabaseUrl, serviceRoleKey, ENTITIES.INVENTORY, {});
    results.push({ entity: ENTITIES.INVENTORY, ...invResult });

    // 2. Refresh current month sales
    const salesResult = await invokeSyncEntity(supabaseUrl, serviceRoleKey, ENTITIES.SALES, {
      start_date: startDate,
      end_date: endDate,
    });
    results.push({ entity: ENTITIES.SALES, ...salesResult });

    // 3. Refresh current month movements
    const movResult = await invokeSyncEntity(supabaseUrl, serviceRoleKey, ENTITIES.MOVEMENTS, {
      start_date: startDate,
      end_date: endDate,
    });
    results.push({ entity: ENTITIES.MOVEMENTS, ...movResult });

    return new Response(
      JSON.stringify({ status: "completed", results }),
      { headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  } catch (error) {
    return new Response(
      JSON.stringify({ status: "error", error: (error as Error).message }),
      { status: 500, headers: { ...CORS_HEADERS, "Content-Type": "application/json" } }
    );
  }
});
