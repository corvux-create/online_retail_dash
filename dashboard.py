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

server = app.server

# Controls
controls = dbc.Col(
    dbc.Card([
        dbc.CardHeader(html.H5("Filters"), className="bg-primary text-white text-center"),
        dbc.CardBody(
            [
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            id='country-dropdown',
                            options=[{'label': c, 'value': c} for c in sorted(df['Country'].unique())],
                            value='United Kingdom',
                            clearable=False,
                            style={
                                'width': '100%',
                                'fontSize': '16px',
                                'height': '48px',
                                'lineHeight': '48px',
                                'alignItems': 'center'
                            }
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
                        width=12,
                        className="mb-3"
                    )
                ),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.Small("Total Revenue", className="text-muted"),
                            html.H5(id="metric-revenue", className="metric-value")
                        ])
                    ], className="mb-2"), width=6),

                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.Small("Total Quantity", className="text-muted"),
                            html.H5(id="metric-quantity", className="metric-value")
                        ])
                    ], className="mb-2"), width=6),
                ]),
                dbc.Row([
                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.Small("Unique Products", className="text-muted"),
                            html.H5(id="metric-products", className="metric-value")
                        ])
                    ], className="mb-2"), width=6),

                    dbc.Col(dbc.Card([
                        dbc.CardBody([
                            html.Small("Transactions", className="text-muted"),
                            html.H5(id="metric-invoices", className="metric-value")
                        ])
                    ], className="mb-2"), width=6),
                ]),
            ],
            className="mb-4 shadow rounded"
        )
    ]),
    md=3, sm=12
)


# App layout
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2("Online Retail Dashboard"), className="mb-4 text-center")),

        dbc.Row(
            [
                controls,
                dbc.Col(
                    dcc.Graph(id='revenue-graph', className="mb-4"),
                    md=9, sm=12
                )
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                        dcc.Graph(id='top-products-graph', className="mb-4"),
                    md=6, sm=12
                ),
                dbc.Col(
                        dcc.Graph(id='scatter-graph', className="mb-4"),
                    md=6, sm=12
                )
            ]
        ),
    ],
    fluid=True
)

# Callback
@app.callback(
    [Output('revenue-graph', 'figure'),
     Output('top-products-graph', 'figure'),
     Output('scatter-graph', 'figure'),
     Output('metric-revenue', 'children'),
     Output('metric-quantity', 'children'),
     Output('metric-products', 'children'),
     Output('metric-invoices', 'children')],
    Input('country-dropdown', 'value'),
    Input('date-picker', 'start_date'),
    Input('date-picker', 'end_date')
)
def update_graph(selected_country, start_date, end_date):
    filtered_df = df[
        (df['Country'] == selected_country) &
        (df['InvoiceDate'] >= pd.to_datetime(start_date)) &
        (df['InvoiceDate'] <= pd.to_datetime(end_date))
    ]

    # Metrics
    total_revenue = f"${filtered_df['TotalPrice'].sum():,.2f}"
    total_quantity = f"{filtered_df['Quantity'].sum():,}"
    unique_products = f"{filtered_df['Description'].nunique():,}"
    num_invoices = f"{filtered_df['Invoice'].nunique():,}"

    # Line chart: Revenue over time
    revenue_grouped = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date)['TotalPrice'].sum().reset_index()
    revenue_fig = px.line(revenue_grouped, x='InvoiceDate', y='TotalPrice',
                          title=f"Total Revenue Over Time - {selected_country}", height=550)
    
    revenue_fig.update_layout(
        title={'x': 0.5, 
               'xanchor': 'center',
                'font': {
                    'size': 24
                }
        }
    )

    # Bar chart: Top 10 products
    product_grouped = filtered_df.groupby('Description')['TotalPrice'].sum().reset_index()
    top_products = product_grouped.sort_values('TotalPrice', ascending=False).head(10)
    product_fig = px.bar(top_products, x='TotalPrice', y='Description', orientation='h', color='Description',
                         title="Top 10 Products by Revenue")
    product_fig.update_layout(
        yaxis={
            'categoryorder': 'total ascending'
        },
        showlegend=False,
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 24
            }
        }
    )

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

    scatter_fig.update_layout(
        title={
            'x': 0.5,
            'xanchor': 'center',
            'font': {
                'size': 24
            }
        }
    )

    return revenue_fig, product_fig, scatter_fig, total_revenue, total_quantity, unique_products, num_invoices

if __name__ == '__main__':
    app.run_server(debug=False)
