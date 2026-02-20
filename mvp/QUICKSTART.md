# 🚀 Quick Start Guide - 5 Minutes to Running Dashboard

## Option 1: Automated Setup (Recommended)

### Windows Users:
```bash
1. Double-click: setup.bat
2. Edit .env file with your Tharanis credentials (opens automatically)
3. Double-click: run.bat
```

✅ **Done!** Dashboard opens at http://localhost:8501

---

## Option 2: Manual Setup

### Step 1: Install (One-time)
```bash
cd e:\users\SzZ\side_hustle\PPCAgentLab\clients\SamanSport\app\mvp

python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Configure (One-time)
```bash
copy .env.example .env
notepad .env
```

Add your credentials:
```env
THARANIS_API_KEY=your_key_here
THARANIS_USERNAME=your_username
THARANIS_PASSWORD=your_password
```

### Step 3: Run
```bash
venv\Scripts\activate
streamlit run app.py
```

---

## 🧪 Test API Connection First

Before launching the dashboard, verify API works:

```bash
venv\Scripts\activate
python tharanis_client.py
```

Expected output:
```
✅ SOAP client initialized successfully
✅ Authentication successful
✅ Fetched 1,234 transactions
📊 Sample transactions (first 5):
   Cikkszám    Cikknév          Kelt        Csökkenés    Nettó érték
   ---------------------------------------------------------------
   ABC123     Boxing Gloves    2024-01-15    10.0        -15000
   ...
```

---

## 📊 Using the Dashboard

1. **Select Date Range**
   - Sidebar → Choose start/end dates
   - Recommend: Last 2 years for good seasonality detection

2. **Load Data**
   - Click "Load Data from Tharanis" button
   - Wait 10-30 seconds (depends on data volume)

3. **Explore Results**
   - **Tab 1**: See overall seasonality patterns
   - **Tab 2**: View top 100 revenue products
   - **Tab 3**: Get ordering recommendations (accounts for 2.5 month lead time)
   - **Tab 4**: Drill down into individual products

4. **Download Recommendations**
   - Tab 3 → Click "Download Recommendations as CSV"
   - Open in Excel for planning

---

## 💡 What to Look For

### High Priority Products
Products with **Seasonality Variance > 50%** need careful order planning:
- **Example**: 150% in December, 60% in March = 90% variance
- **Action**: Order well in advance of peak season

### Peak Season Ordering
If product peaks in **November-December**:
- With 2.5 month lead time → Order in **August-September**
- Dashboard shows this automatically in "Ordering Recommendations"

### Multiple Peaks
Some products have 2-3 peak seasons:
- Plan multiple order cycles throughout the year
- Dashboard shows all peak months

---

## 🎯 Expected Results

After running with 2 years of data, you'll see:

✅ **Aggregate Seasonality**: Overall business peaks (e.g., Q4 holiday season)
✅ **Top 100 Products**: Your most profitable items ranked
✅ **Ordering Calendar**: When to order each product
✅ **Variance Analysis**: Which products need careful planning

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Authentication failed | Check credentials in `.env` file |
| No data returned | Try shorter date range, verify API access |
| Import errors | Run `pip install -r requirements.txt` |
| Dashboard won't start | Check virtual environment is activated |

---

## 📞 Next Steps

1. ✅ Validate data looks correct
2. ✅ Export ordering recommendations
3. ✅ Share with procurement team
4. 📈 Scale to full Next.js dashboard (see IMPLEMENTATION_GUIDE.md)

---

**Estimated Time to First Results**: 5-10 minutes
**Data Processing**: ~30 seconds per year of data
**Works Offline**: No, requires Tharanis API connection
