import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px

# Load and clean the data
df = pd.read_excel("data/online_retail_II.xlsx")
df = df[df['Country'] != 'Unspecified']
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['TotalPrice'] = df['Quantity'] * df['Price']

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

# Controls
controls = dbc.Col(
    dbc.Card([
        dbc.CardHeader(html.H5("Filters")),
        dbc.CardBody([
            dbc.Row(
                dbc.Col(
                    dcc.Dropdown(
                        id='country-dropdown',
                        options=[{'label': c, 'value': c} for c in sorted(df['Country'].unique())],
                        value='United Kingdom',
                        clearable=False,
                        style={'width': '100%'}
                    ),
                    width=12,
                    className="mb-3"
                )
            ),
            dbc.Row(
                dbc.Col(
                    dcc.DatePickerRange(
                        id='date-picker',
                        min_date_allowed=df['InvoiceDate'].min().date(),
                        max_date_allowed=df['InvoiceDate'].max().date(),
                        start_date=df['InvoiceDate'].min().date(),
                        end_date=df['InvoiceDate'].max().date(),
                        style={'width': '100%'}
                    ),
                    width=12,
                    className="mb-3"
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Button("Update", id='update-button', n_clicks=0, className="btn btn-primary w-100"),
                    width=12
                )
            ),
        ])
    ]),
    md=3, sm=12
)


# App layout
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2("Online Retail Dashboard"), className="mb-4")),

        dbc.Row(
            [
                controls,
                dbc.Col(
                    [
                        dbc.Row(dcc.Graph(id='revenue-graph'), className="mb-4"),
                        dbc.Row(dcc.Graph(id='top-products-graph'), className="mb-4"),
                        dbc.Row(dcc.Graph(id='scatter-graph'))
                    ],
                    md=9, sm=12
                ),
            ]
        ),
    ],
    fluid=True
)

# Callback
@app.callback(
    [Output('revenue-graph', 'figure'),
     Output('top-products-graph', 'figure'),
     Output('scatter-graph', 'figure')],
    Input('update-button', 'n_clicks'),
    State('country-dropdown', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date')
)
def update_graph(n_clicks, selected_country, start_date, end_date):
    filtered_df = df[
        (df['Country'] == selected_country) &
        (df['InvoiceDate'] >= pd.to_datetime(start_date)) &
        (df['InvoiceDate'] <= pd.to_datetime(end_date))
    ]

    # Line chart: Revenue over time
    revenue_grouped = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date)['TotalPrice'].sum().reset_index()
    revenue_fig = px.line(revenue_grouped, x='InvoiceDate', y='TotalPrice',
                          title=f"Total Revenue Over Time - {selected_country}")

    # Bar chart: Top 10 products
    product_grouped = filtered_df.groupby('Description')['TotalPrice'].sum().reset_index()
    top_products = product_grouped.sort_values('TotalPrice', ascending=False).head(10)
    product_fig = px.bar(top_products, x='TotalPrice', y='Description', orientation='h',
                         title="Top 10 Products by Revenue")
    product_fig.update_layout(yaxis={'categoryorder': 'total ascending'})

    # Scatter plot: Quantity vs Price
    scatter_data = filtered_df[(filtered_df['Quantity'] > 0) & (filtered_df['Price'] > 0)]
    scatter_fig = px.scatter(
        scatter_data,
        x='Quantity',
        y='Price',
        size='TotalPrice',
        hover_data=['Description'],
        title="Quantity vs. Price Scatter Plot",
        opacity=0.6
    )

    return revenue_fig, product_fig, scatter_fig

if __name__ == '__main__':
    app.run(debug=True)
