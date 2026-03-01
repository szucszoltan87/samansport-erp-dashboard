/**
 * XML parser for Tharanis SOAP V3 responses.
 * Ported from mvp/tharanis_client.py (lines 126-254).
 *
 * Uses regex-based parsing (matching the working Python implementation)
 * rather than a DOM parser to handle streaming and keep dependencies minimal.
 */

import type { SalesRecord, InventoryRecord, MovementRecord, ProductRecord } from "./types.ts";

// ── Low-level helpers ────────────────────────────────────────────────────────

/** Extract text content from the first matching XML tag, CDATA-aware. */
function tag(xml: string, tagName: string): string {
  const re = new RegExp(`<${tagName}[^>]*>(.*?)</${tagName}>`, "s");
  const m = xml.match(re);
  if (!m) return "";
  let val = m[1].trim();
  const cdata = val.match(/^<!\[CDATA\[(.*?)\]\]>$/s);
  return (cdata ? cdata[1] : val).trim();
}

/** Compute SHA-256 hash of a string for deduplication. */
async function hashString(input: string): Promise<string> {
  const data = new TextEncoder().encode(input);
  const hashBuffer = await crypto.subtle.digest("SHA-256", data);
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  return hashArray.map((b) => b.toString(16).padStart(2, "0")).join("");
}

/** HTML-unescape common entities. */
function htmlUnescape(s: string): string {
  return s
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&quot;/g, '"')
    .replace(/&apos;/g, "'");
}

// ── SOAP envelope extraction ─────────────────────────────────────────────────

/**
 * Extract the inner XML from the SOAP response envelope.
 * Mirrors tharanis_client.py _extract_valasz() (lines 126-141).
 */
export function extractValasz(soapText: string): string {
  const returnMatch = soapText.match(/<return[^>]*>(.*?)<\/return>/s);
  if (!returnMatch) {
    throw new Error("No <return> element found in SOAP response.");
  }

  let inner = htmlUnescape(returnMatch[1]).trim();
  inner = inner.replace(/^<\?xml[^?]*\?>\s*/i, "");

  const hibaMatch = inner.match(/<hiba>(\d+)<\/hiba>/);
  if (hibaMatch && parseInt(hibaMatch[1]) !== 0) {
    const msg = tag(inner, "valasz") || "(no message)";
    throw new Error(`Tharanis API hiba ${hibaMatch[1]}: ${msg}`);
  }

  const valaszMatch = inner.match(/<valasz>(.*?)<\/valasz>/s);
  return valaszMatch ? valaszMatch[1].trim() : "";
}

/**
 * Count raw <elem> occurrences in a valasz block.
 * Used for pagination: if count < limit, we've reached the last page.
 */
export function countElems(valaszXml: string): number {
  return (valaszXml.match(/<elem>/g) || []).length;
}

// ── Sales (kimeno_szamla) parser ─────────────────────────────────────────────

/**
 * Parse <elem>/<tetel> records from a kimeno_szamla valasz.
 * Mirrors tharanis_client.py _parse_tetelek() (lines 144-187).
 */
export async function parseSalesRecords(
  valaszXml: string,
  cikkszamFilter?: string
): Promise<SalesRecord[]> {
  const records: SalesRecord[] = [];

  for (const elemMatch of valaszXml.matchAll(/<elem>(.*?)<\/elem>/gs)) {
    const elem = elemMatch[1];
    let kelt = tag(elem, "telj_dat");

    const fejMatch = elem.match(/<fej>(.*?)<\/fej>/s);
    if (fejMatch) {
      kelt = tag(fejMatch[1], "telj_dat") || kelt;
    }

    for (const tetMatch of elem.matchAll(/<tetel>(.*?)<\/tetel>/gs)) {
      const t = tetMatch[1];
      const cikksz = tag(t, "cikksz");

      if (cikkszamFilter && cikksz !== cikkszamFilter) continue;

      const mennyS = tag(t, "menny");
      const nettoArS = tag(t, "netto_ar");
      const afaS = tag(t, "afa_szaz");

      const menny = parseFloat(mennyS);
      const nettoAr = parseFloat(nettoArS);
      const afaRaw = afaS ? parseFloat(afaS) : 27.0;
      const afa = isNaN(afaRaw) ? 27.0 : afaRaw;

      if (isNaN(menny) || isNaN(nettoAr)) continue;
      if (!cikksz || menny <= 0) continue;

      const bruttoAr = Math.round(nettoAr * (1 + afa / 100) * 10000) / 10000;
      const bruttoErtek = Math.round(bruttoAr * menny * 100) / 100;
      const nettoErtek = Math.round(nettoAr * menny * 100) / 100;

      // Skip if any computed value is NaN
      if (isNaN(bruttoAr) || isNaN(bruttoErtek) || isNaN(nettoErtek)) continue;

      // Convert date from YYYY.MM.DD to YYYY-MM-DD for PostgreSQL
      const fulfillmentDate = kelt.replace(/\./g, "-");

      const rawHash = await hashString(`${fulfillmentDate}|${cikksz}|${menny}|${nettoAr}`);

      records.push({
        fulfillment_date: fulfillmentDate,
        sku: cikksz,
        quantity: menny,
        net_price: nettoAr,
        vat_pct: afa,
        gross_price: bruttoAr,
        net_value: nettoErtek,
        gross_value: bruttoErtek,
        is_storno: false,
        raw_xml_hash: rawHash,
      });
    }
  }

  return records;
}

// ── Inventory (keszlet) parser ───────────────────────────────────────────────

/**
 * Parse <elem> records from a keszlet valasz.
 * Mirrors tharanis_client.py _parse_keszlet() (lines 190-214).
 */
export function parseInventoryRecords(valaszXml: string): InventoryRecord[] {
  const records: InventoryRecord[] = [];

  for (const elemMatch of valaszXml.matchAll(/<elem>(.*?)<\/elem>/gs)) {
    const elem = elemMatch[1];
    const cikksz = tag(elem, "cikksz");
    if (!cikksz) continue;

    const warehouses: number[] = [];
    let total = 0;

    for (let i = 1; i <= 6; i++) {
      const v = tag(elem, `kiadhato${i}`);
      const qty = v ? parseFloat(v) : 0;
      warehouses.push(isNaN(qty) ? 0 : qty);
      total += isNaN(qty) ? 0 : qty;
    }

    records.push({
      sku: cikksz,
      total_available: Math.round(total * 100) / 100,
      warehouse_1: warehouses[0],
      warehouse_2: warehouses[1],
      warehouse_3: warehouses[2],
      warehouse_4: warehouses[3],
      warehouse_5: warehouses[4],
      warehouse_6: warehouses[5],
    });
  }

  return records;
}

// ── Movements (raktari_mozgas) parser ────────────────────────────────────────

/**
 * Parse <elem> records from a raktari_mozgas valasz.
 * Mirrors tharanis_client.py _parse_mozgas() (lines 217-254).
 */
export async function parseMovementRecords(
  valaszXml: string,
  cikkszamFilter?: string
): Promise<MovementRecord[]> {
  const records: MovementRecord[] = [];

  for (const elemMatch of valaszXml.matchAll(/<elem>(.*?)<\/elem>/gs)) {
    const elem = elemMatch[1];

    const fejMatch = elem.match(/<fej>(.*?)<\/fej>/s);
    if (!fejMatch) continue;

    const fej = fejMatch[1];
    const kelt = tag(fej, "kelt");
    const irany = tag(fej, "irany") as "B" | "K";
    const mozgas = tag(fej, "mozgas");

    for (const tetMatch of elem.matchAll(/<tetel>(.*?)<\/tetel>/gs)) {
      const t = tetMatch[1];
      const cikksz = tag(t, "cikksz");

      if (cikkszamFilter && cikksz !== cikkszamFilter) continue;

      const mennyS = tag(t, "menny");
      const menny = parseFloat(mennyS);

      if (isNaN(menny) || !cikksz || menny === 0) continue;

      const movementDate = kelt.replace(/\./g, "-");
      const rawHash = await hashString(`${movementDate}|${cikksz}|${irany}|${Math.abs(menny)}`);

      records.push({
        movement_date: movementDate,
        sku: cikksz,
        direction: irany,
        movement_type: mozgas,
        quantity: Math.abs(menny),
        raw_xml_hash: rawHash,
      });
    }
  }

  return records;
}

// ── Products (cikk) parser ───────────────────────────────────────────────────

/**
 * Parse <elem> records from a cikk valasz.
 */
export function parseProductRecords(valaszXml: string): ProductRecord[] {
  const records: ProductRecord[] = [];

  for (const elemMatch of valaszXml.matchAll(/<elem>(.*?)<\/elem>/gs)) {
    const elem = elemMatch[1];
    const cikksz = tag(elem, "cikksz");
    if (!cikksz) continue;

    records.push({
      sku: cikksz,
      name: tag(elem, "megnevezes") || tag(elem, "nev") || "",
      category: tag(elem, "kategoria") || "",
      manufacturer: tag(elem, "gyarto") || "",
      unit: tag(elem, "me") || "",
      active: tag(elem, "aktiv") !== "0",
    });
  }

  return records;
}

// ── Dispatcher ───────────────────────────────────────────────────────────────

/**
 * Parse a valasz XML block into typed records based on entity name.
 */
export async function parseRecords(
  entity: string,
  valaszXml: string,
  cikkszamFilter?: string
): Promise<Array<SalesRecord | InventoryRecord | MovementRecord | ProductRecord>> {
  switch (entity) {
    case "kimeno_szamla":
      return await parseSalesRecords(valaszXml, cikkszamFilter);
    case "keszlet":
      return parseInventoryRecords(valaszXml);
    case "raktari_mozgas":
      return await parseMovementRecords(valaszXml, cikkszamFilter);
    case "cikk":
      return parseProductRecords(valaszXml);
    default:
      throw new Error(`Unknown entity: ${entity}`);
  }
}
