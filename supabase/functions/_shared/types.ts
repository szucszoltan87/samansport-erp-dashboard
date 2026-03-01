export interface SalesRecord {
  fulfillment_date: string; // YYYY-MM-DD
  sku: string;
  quantity: number;
  net_price: number;
  vat_pct: number;
  gross_price: number;
  net_value: number;
  gross_value: number;
  is_storno: boolean;
  raw_xml_hash: string;
}

export interface InventoryRecord {
  sku: string;
  total_available: number;
  warehouse_1: number;
  warehouse_2: number;
  warehouse_3: number;
  warehouse_4: number;
  warehouse_5: number;
  warehouse_6: number;
}

export interface MovementRecord {
  movement_date: string; // YYYY-MM-DD
  sku: string;
  direction: "B" | "K";
  movement_type: string;
  quantity: number;
  raw_xml_hash: string;
}

export interface ProductRecord {
  sku: string;
  name: string;
  category: string;
  manufacturer: string;
  unit: string;
  active: boolean;
}

export interface SyncRequest {
  entity: string;
  filters?: {
    start_date?: string; // YYYY.MM.DD
    end_date?: string;
    cikkszam?: string;
  };
}

export interface SyncMetadata {
  id: number;
  entity: string;
  filter_hash: string;
  filter_params: Record<string, unknown>;
  last_synced_at: string | null;
  sync_started_at: string | null;
  sync_status: "idle" | "running" | "error";
  error_message: string | null;
  ttl_seconds: number;
  pages_fetched: number;
  records_synced: number;
}

export interface EntityConfig {
  entity: string;
  ttl_seconds: number;
  page_size: number;
  enabled: boolean;
  description: string;
}
