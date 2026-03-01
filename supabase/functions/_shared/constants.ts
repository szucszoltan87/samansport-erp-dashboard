export const THARANIS_API_URL = "https://login.tharanis.hu/apiv3.php";
export const SOAP_TIMEOUT_MS = 120_000;
export const DEFAULT_PAGE_SIZE = 200;

// Entity names matching the Tharanis API
export const ENTITIES = {
  SALES: "kimeno_szamla",
  INVENTORY: "keszlet",
  MOVEMENTS: "raktari_mozgas",
  PRODUCTS: "cikk",
} as const;

// Supabase table names
export const TABLES = {
  kimeno_szamla: "sales_invoice_lines",
  keszlet: "inventory_snapshot",
  raktari_mozgas: "warehouse_movements",
  cikk: "products",
} as const;
