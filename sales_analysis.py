"""
Sales Insights for Consumer Goods Company
Data Analysis and Business Intelligence Script

This script analyzes sales data to provide business insights including:
- Top products and customers by revenue
- Regional performance analysis
- Monthly sales trends
- Pareto principle analysis (80/20 rule)
- Profitability analysis
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class SalesAnalyzer:
    def __init__(self, file_path):
        """Initialize the SalesAnalyzer with data file path"""
        self.file_path = file_path
        self.df = None
        self.clean_df = None
        
    def load_data(self):
        """Load and inspect the sales data"""
        print("Loading sales data...")
        try:
            self.df = pd.read_csv(self.file_path)
        except FileNotFoundError:
            print(f"Data file not found: {self.file_path}. Creating a sample dataset at 'data/sales_data.csv'.")
            # Create sample dataset
            sample_data = {
                'OrderID': [1, 2, 3, 4, 5, 6, 7, 8],
                'CustomerName': ['Alice', 'Bob', 'Charlie', 'Diana', 'Edward', 'Frank', 'Grace', 'Helen'],
                'ProductName': ['Smartphone', 'Laptop', 'Desk', 'Chair', 'Blender', 'Headphones', 'TV', 'Coffee Table'],
                'Category': ['Electronics', 'Electronics', 'Furniture', 'Furniture', 'Home & Garden', 'Electronics', 'Electronics', 'Furniture'],
                'Region': ['North', 'South', 'East', 'West', 'North', 'South', 'East', 'West'],
                'OrderDate': ['2023-01-05', '2023-01-12', '2023-01-20', '2023-02-02', '2023-02-10', '2023-02-18', '2023-03-01', '2023-03-09'],
                'Sales': [20000, 55000, 15000, 7000, 4000, 3000, 45000, 9000],
                'Profit': [3000, 8000, 2500, 1200, 600, 500, 6000, 1500],
                'Quantity': [1, 1, 1, 2, 1, 1, 1, 1]
            }
            self.df = pd.DataFrame(sample_data)
            # Ensure directory exists and save
            import os
            os.makedirs('data', exist_ok=True)
            self.df.to_csv('data/sales_data.csv', index=False)
            print("Sample dataset created.")
        print(f"Data loaded successfully! Shape: {self.df.shape}")
        return self.df
    
    def inspect_data(self):
        """Inspect the data for quality issues"""
        print("\nData Inspection:")
        print("=" * 50)
        
        print(f"Dataset shape: {self.df.shape}")
        print(f"Columns: {list(self.df.columns)}")
        
        print("\nData Types:")
        print(self.df.dtypes)
        
        print("\nMissing Values:")
        missing_data = self.df.isnull().sum()
        print(missing_data[missing_data > 0] if missing_data.sum() > 0 else "No missing values found!")
        
        print("\nData Sample:")
        print(self.df.head())
        
        print("\nBasic Statistics:")
        print(self.df.describe())
        
    def clean_data(self):
        """Clean and prepare the data for analysis"""
        print("\nData Cleaning Process:")
        print("=" * 50)
        
        # Create a copy for cleaning
        self.clean_df = self.df.copy()
        
        # Convert OrderDate to datetime
        self.clean_df['OrderDate'] = pd.to_datetime(self.clean_df['OrderDate'])
        
        # Add useful derived columns
        self.clean_df['Month'] = self.clean_df['OrderDate'].dt.month
        self.clean_df['MonthName'] = self.clean_df['OrderDate'].dt.strftime('%B')
        self.clean_df['Year'] = self.clean_df['OrderDate'].dt.year
        self.clean_df['Profit_Margin'] = (self.clean_df['Profit'] / self.clean_df['Sales']) * 100
        
        # Remove any duplicates
        initial_rows = len(self.clean_df)
        self.clean_df = self.clean_df.drop_duplicates()
        final_rows = len(self.clean_df)
        
        if initial_rows != final_rows:
            print(f"Removed {initial_rows - final_rows} duplicate rows")
        
        print("Data cleaning completed!")
        return self.clean_df
    
    def calculate_kpis(self):
        """Calculate key performance indicators"""
        print("\nKey Performance Indicators:")
        print("=" * 50)
        
        kpis = {}
        
        # Total metrics
        kpis['Total_Sales'] = self.clean_df['Sales'].sum()
        kpis['Total_Profit'] = self.clean_df['Profit'].sum()
        kpis['Total_Orders'] = len(self.clean_df)
        kpis['Total_Quantity'] = self.clean_df['Quantity'].sum()
        kpis['Average_Order_Value'] = kpis['Total_Sales'] / kpis['Total_Orders']
        kpis['Overall_Profit_Margin'] = (kpis['Total_Profit'] / kpis['Total_Sales']) * 100
        
        # Print KPIs
        print(f"Total Sales: Rs {kpis['Total_Sales']:,.2f}")
        print(f"Total Profit: Rs {kpis['Total_Profit']:,.2f}")
        print(f"Total Orders: {kpis['Total_Orders']:,}")
        print(f"Total Quantity Sold: {kpis['Total_Quantity']:,}")
        print(f"Average Order Value: Rs {kpis['Average_Order_Value']:.2f}")
        print(f"Overall Profit Margin: {kpis['Overall_Profit_Margin']:.2f}%")
        
        return kpis
    
    def top_products_analysis(self, top_n=10):
        """Analyze top products by revenue"""
        print(f"\nTop {top_n} Products by Revenue:")
        print("=" * 50)
        
        product_analysis = self.clean_df.groupby('ProductName').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'Quantity': 'sum',
            'OrderID': 'count'
        }).rename(columns={'OrderID': 'Order_Count'})
        
        product_analysis['Profit_Margin'] = (product_analysis['Profit'] / product_analysis['Sales']) * 100
        product_analysis = product_analysis.sort_values('Sales', ascending=False)
        
        top_products = product_analysis.head(top_n)
        
        print(top_products.round(2))
        
        return top_products
    
    def top_customers_analysis(self, top_n=10):
        """Analyze top customers by revenue"""
        print(f"\nTop {top_n} Customers by Revenue:")
        print("=" * 50)
        
        customer_analysis = self.clean_df.groupby('CustomerName').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'OrderID': 'count',
            'Quantity': 'sum'
        }).rename(columns={'OrderID': 'Order_Count'})
        
        customer_analysis['Profit_Margin'] = (customer_analysis['Profit'] / customer_analysis['Sales']) * 100
        customer_analysis = customer_analysis.sort_values('Sales', ascending=False)
        
        top_customers = customer_analysis.head(top_n)
        
        print(top_customers.round(2))
        
        return top_customers
    
    def regional_analysis(self):
        """Analyze sales performance by region"""
        print("\nRegional Performance Analysis:")
        print("=" * 50)
        
        regional_analysis = self.clean_df.groupby('Region').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'OrderID': 'count',
            'Quantity': 'sum'
        }).rename(columns={'OrderID': 'Order_Count'})
        
        regional_analysis['Profit_Margin'] = (regional_analysis['Profit'] / regional_analysis['Sales']) * 100
        regional_analysis['Sales_Percentage'] = (regional_analysis['Sales'] / regional_analysis['Sales'].sum()) * 100
        regional_analysis = regional_analysis.sort_values('Sales', ascending=False)
        
        print(regional_analysis.round(2))
        
        return regional_analysis
    
    def category_analysis(self):
        """Analyze sales performance by product category"""
        print("\nCategory Performance Analysis:")
        print("=" * 50)
        
        category_analysis = self.clean_df.groupby('Category').agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'OrderID': 'count',
            'Quantity': 'sum'
        }).rename(columns={'OrderID': 'Order_Count'})
        
        category_analysis['Profit_Margin'] = (category_analysis['Profit'] / category_analysis['Sales']) * 100
        category_analysis['Sales_Percentage'] = (category_analysis['Sales'] / category_analysis['Sales'].sum()) * 100
        category_analysis = category_analysis.sort_values('Sales', ascending=False)
        
        print(category_analysis.round(2))
        
        return category_analysis
    
    def monthly_trend_analysis(self):
        """Analyze monthly sales trends"""
        print("\nMonthly Sales Trend Analysis:")
        print("=" * 50)
        
        monthly_analysis = self.clean_df.groupby(['Year', 'Month', 'MonthName']).agg({
            'Sales': 'sum',
            'Profit': 'sum',
            'OrderID': 'count',
            'Quantity': 'sum'
        }).rename(columns={'OrderID': 'Order_Count'})
        
        monthly_analysis['Profit_Margin'] = (monthly_analysis['Profit'] / monthly_analysis['Sales']) * 100
        monthly_analysis = monthly_analysis.reset_index()
        
        print(monthly_analysis.round(2))
        
        return monthly_analysis
    
    def pareto_analysis(self, column='ProductName', metric='Sales'):
        """Perform Pareto analysis (80/20 rule)"""
        print(f"\nPareto Analysis ({metric} by {column}):")
        print("=" * 50)
        
        # Group by the specified column and sum the metric
        pareto_data = self.clean_df.groupby(column)[metric].sum().sort_values(ascending=False)
        
        # Calculate cumulative percentages
        total = pareto_data.sum()
        pareto_data_pct = (pareto_data / total) * 100
        cumulative_pct = pareto_data_pct.cumsum()
        
        # Find the 80% threshold
        threshold_80 = pareto_data_pct[cumulative_pct <= 80]
        threshold_20 = pareto_data_pct[cumulative_pct > 80]
        
        print(f"Top performers (80% of {metric}):")
        print(f"Number of items: {len(threshold_80)} out of {len(pareto_data)} total")
        print(f"Percentage of items: {(len(threshold_80)/len(pareto_data)*100):.1f}%")
        print(f"Actual contribution: {threshold_80.sum():.1f}%")
        
        print(f"\nRemaining items (20% of {metric}):")
        print(f"Number of items: {len(threshold_20)}")
        print(f"Percentage of items: {(len(threshold_20)/len(pareto_data)*100):.1f}%")
        print(f"Actual contribution: {threshold_20.sum():.1f}%")
        
        return pareto_data, pareto_data_pct, cumulative_pct
    
    def generate_insights_report(self):
        """Generate a comprehensive insights report"""
        print("\n" + "="*60)
        print("SALES INSIGHTS REPORT")
        print("="*60)
        
        # Calculate all analyses
        kpis = self.calculate_kpis()
        top_products = self.top_products_analysis()
        top_customers = self.top_customers_analysis()
        regional_performance = self.regional_analysis()
        category_performance = self.category_analysis()
        monthly_trends = self.monthly_trend_analysis()
        
        print("\nKEY INSIGHTS:")
        print("-" * 40)
        
        # Top product insight
        top_product = top_products.index[0]
        top_product_sales = top_products.iloc[0]['Sales']
        print(f"1. Best-selling product: '{top_product}' with Rs {top_product_sales:,.2f} in sales")
        
        # Top customer insight
        top_customer = top_customers.index[0]
        top_customer_sales = top_customers.iloc[0]['Sales']
        print(f"2. Top customer: '{top_customer}' with Rs {top_customer_sales:,.2f} in purchases")
        
        # Regional insight
        top_region = regional_performance.index[0]
        top_region_sales = regional_performance.iloc[0]['Sales']
        top_region_pct = regional_performance.iloc[0]['Sales_Percentage']
        print(f"3. Best performing region: {top_region} with Rs {top_region_sales:,.2f} ({top_region_pct:.1f}% of total sales)")
        
        # Category insight
        top_category = category_performance.index[0]
        top_category_sales = category_performance.iloc[0]['Sales']
        top_category_pct = category_performance.iloc[0]['Sales_Percentage']
        print(f"4. Top category: {top_category} with Rs {top_category_sales:,.2f} ({top_category_pct:.1f}% of total sales)")
        
        # Profit margin insight
        best_margin_category = category_performance.loc[category_performance['Profit_Margin'].idxmax()]
        print(f"5. Most profitable category: {best_margin_category.name} with {best_margin_category['Profit_Margin']:.1f}% margin")
        
        # Monthly trend insight
        if len(monthly_trends) > 1:
            best_month = monthly_trends.loc[monthly_trends['Sales'].idxmax()]
            print(f"6. Best sales month: {best_month['MonthName']} {best_month['Year']} with Rs {best_month['Sales']:,.2f}")
        
        print("\nRECOMMENDATIONS:")
        print("-" * 40)
        print("- Focus marketing efforts on the top-performing region and category")
        print("- Develop loyalty programs for top customers")
        print("- Consider expanding the best-selling product line")
        print("- Analyze seasonal patterns for inventory planning")
        print("- Monitor profit margins across all categories")
        
        return {
            'kpis': kpis,
            'top_products': top_products,
            'top_customers': top_customers,
            'regional_performance': regional_performance,
            'category_performance': category_performance,
            'monthly_trends': monthly_trends
        }

def main():
    """Main function to run the complete sales analysis"""
    print("Starting Sales Insights Analysis...")
    print("=" * 60)
    
    # Initialize analyzer
    analyzer = SalesAnalyzer('data/sales_data.csv')
    
    # Load and analyze data
    analyzer.load_data()
    analyzer.inspect_data()
    analyzer.clean_data()
    
    # Generate comprehensive report
    results = analyzer.generate_insights_report()
    
    print("\nAnalysis completed successfully!")
    print("Check the generated visualizations and reports for detailed insights.")

if __name__ == "__main__":
    main() 