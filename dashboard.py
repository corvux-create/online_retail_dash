import dash
from dash import dcc, html
import plotly.express as px
import pandas as pd

# Load and clean data
df = pd.read_excel("data/online_retail_II.xlsx")
df = df.dropna(subset=['Customer ID']).copy()
df['TotalPrice'] = df['Quantity'] * df['Price']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])

# Grouped data
revenue_by_country = df.groupby('Country')['TotalPrice'].sum().sort_values(ascending=False)
top_products = df.groupby('Description')['TotalPrice'].sum().sort_values(ascending=False).head(10)
sales_over_time = df.resample('W-Mon', on='InvoiceDate')['TotalPrice'].sum().reset_index()

# Dash app
app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Online Retail Dashboard", style={'textAlign': 'center'}),

    html.Div([
        html.H3(f"Total Revenue: £{df['TotalPrice'].sum():,.2f}")
    ], style={'textAlign': 'center', 'marginBottom': '40px'}),

    dcc.Graph(
        figure=px.bar(
            revenue_by_country.head(10),
            title="Top Countries by Revenue",
            labels={'value': 'Revenue', 'index': 'Country'}
        )
    ),

    dcc.Graph(
        figure=px.bar(
            top_products,
            title="Top 10 Products by Revenue",
            labels={'value': 'Revenue', 'index': 'Product'}
        )
    ),

    dcc.Graph(
        figure=px.line(
            sales_over_time,
            x='InvoiceDate',
            y='TotalPrice',
            title='Weekly Revenue Over Time'
        )
    )
])

if __name__ == '__main__':
    app.run(debug=True)
