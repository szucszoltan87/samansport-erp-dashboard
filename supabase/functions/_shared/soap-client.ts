/**
 * SOAP client for Tharanis ERP V3 API.
 * Ported from mvp/tharanis_client.py (lines 42-123).
 */

import { THARANIS_API_URL, SOAP_TIMEOUT_MS, DEFAULT_PAGE_SIZE } from "./constants.ts";

function getCredentials() {
  return {
    ugyfelkod: Deno.env.get("THARANIS_UGYFELKOD") || "7354",
    cegkod: Deno.env.get("THARANIS_CEGKOD") || "ab",
    apikulcs: Deno.env.get("THARANIS_APIKULCS") || "",
  };
}

function xmlEncode(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

/**
 * Build the inner <leker> XML for kimeno_szamla (sales invoices).
 */
function buildSalesLekerXml(
  startDate: string,
  endDate: string,
  cikkszam: string | undefined,
  page: number,
  limit: number
): string {
  let szurok =
    `<szuro><mezo>teljdat</mezo><relacio>&gt;=</relacio><ertek>${startDate}</ertek></szuro>` +
    `<szuro><mezo>teljdat</mezo><relacio>&lt;=</relacio><ertek>${endDate}</ertek></szuro>` +
    `<szuro><mezo>storno</mezo><relacio>=</relacio><ertek>0</ertek></szuro>`;

  if (cikkszam) {
    szurok += `<szuro><mezo>cikksz</mezo><relacio>=</relacio><ertek>${xmlEncode(cikkszam)}</ertek></szuro>`;
  }

  return `<leker><limit>${limit}</limit><oldal>${page}</oldal><szurok>${szurok}</szurok><adatok><fej>I</fej></adatok></leker>`;
}

/**
 * Build the inner <leker> XML for keszlet (inventory).
 */
function buildInventoryLekerXml(
  cikkszam: string | undefined,
  page: number,
  limit: number
): string {
  let szurok = "";
  if (cikkszam) {
    szurok = `<szurok><szuro><mezo>cikksz</mezo><relacio>=</relacio><ertek>${xmlEncode(cikkszam)}</ertek></szuro></szurok>`;
  }
  return `<leker><limit>${limit}</limit><oldal>${page}</oldal>${szurok}</leker>`;
}

/**
 * Build the inner <leker> XML for raktari_mozgas (warehouse movements).
 */
function buildMovementsLekerXml(
  startDate: string,
  endDate: string,
  cikkszam: string | undefined,
  page: number,
  limit: number
): string {
  let szurok =
    `<szuro><mezo>kelt</mezo><relacio>&gt;=</relacio><ertek>${startDate}</ertek></szuro>` +
    `<szuro><mezo>kelt</mezo><relacio>&lt;=</relacio><ertek>${endDate}</ertek></szuro>` +
    `<szuro><mezo>torolt</mezo><relacio>=</relacio><ertek>0</ertek></szuro>`;

  if (cikkszam) {
    szurok += `<szuro><mezo>cikksz</mezo><relacio>=</relacio><ertek>${xmlEncode(cikkszam)}</ertek></szuro>`;
  }

  return `<leker><limit>${limit}</limit><oldal>${page}</oldal><szurok>${szurok}</szurok><adatok><fej>I</fej></adatok></leker>`;
}

/**
 * Build the inner <leker> XML for cikk (products).
 */
function buildProductsLekerXml(page: number, limit: number): string {
  return `<leker><limit>${limit}</limit><oldal>${page}</oldal></leker>`;
}

/**
 * Build the <leker> XML payload for a given entity and filters.
 */
export function buildLekerXml(
  entity: string,
  filters: { start_date?: string; end_date?: string; cikkszam?: string } | undefined,
  page: number,
  limit: number = DEFAULT_PAGE_SIZE
): string {
  switch (entity) {
    case "kimeno_szamla":
      return buildSalesLekerXml(
        filters?.start_date || "",
        filters?.end_date || "",
        filters?.cikkszam,
        page,
        limit
      );
    case "keszlet":
      return buildInventoryLekerXml(filters?.cikkszam, page, limit);
    case "raktari_mozgas":
      return buildMovementsLekerXml(
        filters?.start_date || "",
        filters?.end_date || "",
        filters?.cikkszam,
        page,
        limit
      );
    case "cikk":
      return buildProductsLekerXml(page, limit);
    default:
      return `<leker><limit>${limit}</limit><oldal>${page}</oldal></leker>`;
  }
}

/**
 * Wrap lekerXml in a full SOAP envelope for the V3 API.
 * Matches the format from tharanis_client.py _build_envelope().
 */
export function buildSoapEnvelope(entity: string, lekerXml: string): string {
  const { ugyfelkod, cegkod, apikulcs } = getCredentials();

  return `<?xml version="1.0" encoding="UTF-8"?>
<SOAP-ENV:Envelope
  xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"
  xmlns:ns1="urn://apiv3"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
  xmlns:xsd="http://www.w3.org/2001/XMLSchema">
  <SOAP-ENV:Body>
    <ns1:leker>
      <param0 xsi:type="xsd:string">${ugyfelkod}</param0>
      <param1 xsi:type="xsd:string">${cegkod}</param1>
      <param2 xsi:type="xsd:string">${apikulcs}</param2>
      <param3 xsi:type="xsd:string">${entity}</param3>
      <param4 xsi:type="xsd:string"><![CDATA[${lekerXml}]]></param4>
    </ns1:leker>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>`;
}

/**
 * POST a SOAP envelope to the Tharanis V3 API and return the raw XML response.
 */
export async function postSoap(entity: string, lekerXml: string): Promise<string> {
  const envelope = buildSoapEnvelope(entity, lekerXml);

  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), SOAP_TIMEOUT_MS);

  try {
    const response = await fetch(THARANIS_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "text/xml; charset=utf-8",
        "Accept-Encoding": "gzip",
      },
      body: envelope,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`SOAP HTTP error: ${response.status} ${response.statusText}`);
    }

    return await response.text();
  } finally {
    clearTimeout(timeoutId);
  }
}
