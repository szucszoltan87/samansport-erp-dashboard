# Tharanis ERP Dashboard – MVP

> Product-level sales analytics UI for the Tharanis.hu ERP system.
> Stack: Python · Streamlit · Plotly · raw SOAP (no WSDL)

---

## 🎯 What This MVP Does

1. **Select a product** from a searchable dropdown (6,500+ products with names)
2. **Set a date range** in the sidebar
3. **Choose a metric**: Bruttó érték / Mennyiség / Bruttó ár
4. **Load data** → the app fetches live invoices from Tharanis via SOAP V3
5. **Explore the chart** — toggle between bar and line view instantly

---

## 📊 Metrics Explained

| Mutató | Source | Aggregation |
|---|---|---|
| **Bruttó érték** | `netto_ar × (1 + afa_szaz/100) × menny` | Sum per month |
| **Mennyiség** | `menny` field in invoice tetel | Sum per month |
| **Bruttó ár** | `netto_ar × (1 + afa_szaz/100)` | Average per month |

---

## 🚀 Quick Start

```powershell
# Activate virtual environment
venv\Scripts\activate

# Launch dashboard
streamlit run app.py
```

Dashboard opens at `http://localhost:8501`

---

## 🔌 API Details

| Parameter | Value |
|---|---|
| Endpoint | `https://login.tharanis.hu/apiv3.php` |
| Namespace | `urn://apiv3` |
| SOAP function | `leker` |
| Entity (param3) | `kimeno_szamla` |
| Auth | `UGYFELKOD=7354`, `CEGKOD=ab`, API key |

All credentials are in `.env`. The client sends raw SOAP envelopes (no WSDL/zeep).

---

## 📁 File Structure

```
mvp/
├── .env                  # API credentials
├── .env.example          # Credential template
├── requirements.txt      # Python dependencies
├── tharanis_client.py    # V3 SOAP client (raw HTTP POST, paginated)
├── app.py                # Streamlit dashboard
└── README.md             # This file

Product master CSV (outside mvp dir):
../../inventory_analysis_2020_2026/rakbiz_analitika_012020_012026.csv
```

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| No products in dropdown | Check that the `rakbiz_analitika_012020_012026.csv` exists two levels up |
| API error / no data | Verify `.env` credentials; try a shorter date range |
| Import errors | Run `pip install -r requirements.txt` |

### Test the API client directly

```powershell
venv\Scripts\activate
python tharanis_client.py
```

Expected output:
```
Tharanis V3 API — connection test
Fetching kimeno_szamla: 2026.01.21 to 2026.02.20
Records fetched : 2506
Unique products : 598
Total Bruttó ért: 22,246,044 HUF
```

---

## 🗺️ Next Steps

- Add multi-product comparison on a single chart
- Export filtered data to CSV/Excel
- Add year-over-year comparison view
- Build full Next.js frontend backed by a FastAPI service
