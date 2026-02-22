"""
Seasonality Analyzer for SamanSport Inventory
Analyzes sales patterns and provides ordering recommendations
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


class SeasonalityAnalyzer:
    """Analyze seasonality and provide ordering recommendations"""

    def __init__(self, movements_df):
        """
        Initialize analyzer with warehouse movements data

        Args:
            movements_df: DataFrame with columns: Cikkszám, Cikknév, Kelt, Csökkenés, Nettó érték
        """
        self.movements = movements_df.copy()
        self.prepare_data()

    def prepare_data(self):
        """Prepare data for analysis"""
        # Filter only sales (Csökkenés > 0)
        self.sales = self.movements[self.movements['Csökkenés'] > 0].copy()

        if len(self.sales) > 0:
            # Extract date components
            self.sales['Év'] = self.sales['Kelt'].dt.year
            self.sales['Hónap'] = self.sales['Kelt'].dt.month
            self.sales['Hónap név'] = self.sales['Kelt'].dt.strftime('%B')
            self.sales['Év-Hónap'] = self.sales['Kelt'].dt.to_period('M')

            # Calculate revenue
            self.sales['Árbevétel'] = abs(self.sales['Nettó érték'])

    def get_top_products(self, n=100):
        """
        Get top N products by total revenue

        Args:
            n (int): Number of top products to return

        Returns:
            DataFrame with top products and their metrics
        """
        product_revenue = self.sales.groupby(['Cikkszám', 'Cikknév']).agg({
            'Árbevétel': 'sum',
            'Csökkenés': 'sum'
        }).reset_index()

        product_revenue.columns = ['Cikkszám', 'Cikknév', 'Összes árbevétel', 'Összes mennyiség']
        product_revenue = product_revenue.sort_values('Összes árbevétel', ascending=False)

        top_products = product_revenue.head(n).reset_index(drop=True)
        top_products['Rangsor'] = range(1, len(top_products) + 1)

        return top_products

    def calculate_monthly_seasonality(self, product_code=None):
        """
        Calculate monthly seasonality patterns

        Args:
            product_code (str): If provided, calculate for specific product. Otherwise, aggregate all.

        Returns:
            DataFrame with monthly averages and seasonality index
        """
        # Filter by product if specified
        if product_code:
            data = self.sales[self.sales['Cikkszám'] == product_code].copy()
        else:
            data = self.sales.copy()

        if len(data) == 0:
            return pd.DataFrame()

        # Group by month and calculate averages
        monthly_sales = data.groupby('Hónap').agg({
            'Csökkenés': 'mean',
            'Árbevétel': 'mean'
        }).reset_index()

        monthly_sales.columns = ['Hónap', 'Átlag mennyiség', 'Átlag árbevétel']

        # Calculate seasonality index (average / overall average)
        overall_avg_qty = monthly_sales['Átlag mennyiség'].mean()
        overall_avg_rev = monthly_sales['Átlag árbevétel'].mean()

        monthly_sales['Mennyiség index'] = (monthly_sales['Átlag mennyiség'] / overall_avg_qty * 100).round(1)
        monthly_sales['Árbevétel index'] = (monthly_sales['Átlag árbevétel'] / overall_avg_rev * 100).round(1)

        # Add month names
        month_names = {
            1: 'Január', 2: 'Február', 3: 'Március', 4: 'Április',
            5: 'Május', 6: 'Június', 7: 'Július', 8: 'Augusztus',
            9: 'Szeptember', 10: 'Október', 11: 'November', 12: 'December'
        }
        monthly_sales['Hónap név'] = monthly_sales['Hónap'].map(month_names)

        return monthly_sales

    def identify_peak_months(self, product_code=None, threshold=120):
        """
        Identify peak sales months (seasonality index > threshold)

        Args:
            product_code (str): Product code to analyze
            threshold (int): Seasonality index threshold (default 120 = 20% above average)

        Returns:
            List of peak month numbers
        """
        seasonality = self.calculate_monthly_seasonality(product_code)

        if len(seasonality) == 0:
            return []

        peak_months = seasonality[seasonality['Mennyiség index'] >= threshold]['Hónap'].tolist()

        return sorted(peak_months)

    def calculate_ordering_recommendations(self, top_n=100, lead_time_months=2.5):
        """
        Calculate when to order products based on seasonality and lead time

        Args:
            top_n (int): Number of top products to analyze
            lead_time_months (float): Shipping lead time in months (default 2.5 for 2-3 months)

        Returns:
            DataFrame with ordering recommendations
        """
        top_products = self.get_top_products(top_n)

        recommendations = []

        for _, product in top_products.iterrows():
            product_code = product['Cikkszám']
            product_name = product['Cikknév']

            # Get peak months for this product
            peak_months = self.identify_peak_months(product_code, threshold=115)

            if len(peak_months) == 0:
                # No clear seasonality, use overall average
                peak_months = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]

            # Calculate order months (peak month - lead time)
            order_months = []
            for peak_month in peak_months:
                # Subtract lead time
                order_date = datetime(2024, peak_month, 1) - relativedelta(months=lead_time_months)
                order_month = order_date.month
                order_months.append(order_month)

            # Remove duplicates and sort
            order_months = sorted(list(set(order_months)))

            # Convert month numbers to names
            month_names = {
                1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr',
                5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug',
                9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'
            }

            peak_month_names = ', '.join([month_names[m] for m in peak_months[:3]])  # Top 3 peaks
            order_month_names = ', '.join([month_names[m] for m in order_months[:3]])  # Top 3 order times

            # Get seasonality data
            seasonality = self.calculate_monthly_seasonality(product_code)

            if len(seasonality) > 0:
                max_season_index = seasonality['Mennyiség index'].max()
                min_season_index = seasonality['Mennyiség index'].min()
                seasonality_variance = max_season_index - min_season_index
            else:
                max_season_index = 100
                min_season_index = 100
                seasonality_variance = 0

            recommendations.append({
                'Rangsor': product['Rangsor'],
                'Cikkszám': product_code,
                'Cikknév': product_name,
                'Összes árbevétel': product['Összes árbevétel'],
                'Csúcs hónapok': peak_month_names,
                'Rendelés hónapok': order_month_names,
                'Szezonalitás variancia': round(seasonality_variance, 1),
                'Max index': round(max_season_index, 1),
                'Min index': round(min_season_index, 1),
            })

        return pd.DataFrame(recommendations)

    def get_monthly_trend(self, product_code=None):
        """
        Get month-by-month sales trend data for charts

        Args:
            product_code (str): Product code to analyze (None for aggregate)

        Returns:
            DataFrame with monthly sales data
        """
        if product_code:
            data = self.sales[self.sales['Cikkszám'] == product_code].copy()
        else:
            data = self.sales.copy()

        if len(data) == 0:
            return pd.DataFrame()

        monthly_trend = data.groupby('Év-Hónap').agg({
            'Csökkenés': 'sum',
            'Árbevétel': 'sum'
        }).reset_index()

        monthly_trend.columns = ['Év-Hónap', 'Mennyiség', 'Árbevétel']
        monthly_trend['Év-Hónap'] = monthly_trend['Év-Hónap'].astype(str)

        return monthly_trend

    def get_summary_stats(self):
        """Get summary statistics for the dataset"""
        if len(self.sales) == 0:
            return {}

        return {
            'Összes tranzakció': len(self.sales),
            'Egyedi termékek': self.sales['Cikkszám'].nunique(),
            'Összes árbevétel': self.sales['Árbevétel'].sum(),
            'Átlag havi árbevétel': self.sales.groupby('Év-Hónap')['Árbevétel'].sum().mean(),
            'Időszak kezdete': self.sales['Kelt'].min().strftime('%Y-%m-%d'),
            'Időszak vége': self.sales['Kelt'].max().strftime('%Y-%m-%d'),
        }


# Test function
if __name__ == "__main__":
    print("🧪 Testing Seasonality Analyzer with sample data...")

    # Create sample data
    dates = pd.date_range(start='2023-01-01', end='2024-12-31', freq='D')
    np.random.seed(42)

    sample_data = []
    for date in dates:
        month = date.month
        # Create seasonality pattern (higher sales in certain months)
        base_qty = 10
        if month in [11, 12]:  # Peak in Nov-Dec
            qty = base_qty * 2
        elif month in [6, 7, 8]:  # Peak in summer
            qty = base_qty * 1.5
        else:
            qty = base_qty

        sample_data.append({
            'Cikkszám': 'TEST001',
            'Cikknév': 'Test Product',
            'Kelt': date,
            'Csökkenés': qty + np.random.randint(-3, 3),
            'Nettó érték': -(qty * 1000),
        })

    df = pd.DataFrame(sample_data)

    # Analyze
    analyzer = SeasonalityAnalyzer(df)

    print("\n📊 Summary Stats:")
    stats = analyzer.get_summary_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

    print("\n📈 Monthly Seasonality:")
    seasonality = analyzer.calculate_monthly_seasonality()
    print(seasonality.to_string(index=False))

    print("\n🎯 Peak Months:")
    peaks = analyzer.identify_peak_months()
    print(f"  {peaks}")

    print("\n📦 Ordering Recommendations:")
    recommendations = analyzer.calculate_ordering_recommendations(top_n=1)
    print(recommendations.to_string(index=False))

    print("\n✅ Test completed!")
