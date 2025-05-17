import dash
import dash_bootstrap_components as dbc
from dash import html, dcc, Input, Output, State
import pandas as pd
import plotly.express as px

# df = pd.read_csv("OnlineRetail.csv", encoding='ISO-8859-1')
df = pd.read_excel("data/online_retail_II.xlsx")

# Remove the rows from data frame where country name is Unspecified
df_country_cleaned = df[df['Country']!='Unspecified']

df_country_cleaned['InvoiceDate'] = pd.to_datetime(df_country_cleaned['InvoiceDate'])
df_country_cleaned['TotalPrice'] = df_country_cleaned['Quantity'] * df_country_cleaned['Price']

# Initialize Dash app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
controls_Dropdown = html.Div(
            [
                # html.Label("Select Country:", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id='country-dropdown',
                    options=[{'label': c, 'value': c} for c in sorted(df_country_cleaned['Country'].unique())],
                    value='United Kingdom',
                    clearable=False,
                    # style={'width': '100%'}
                ),
            ]
        )

controls_DatePickerRange = html.Div(
            [
                # html.Label("Select Date Rangeyyy:", style={"fontWeight": "bold"}),
                dcc.DatePickerRange(
                    id='date-picker',
                    min_date_allowed=df_country_cleaned['InvoiceDate'].min().date(),
                    max_date_allowed=df_country_cleaned['InvoiceDate'].max().date(),
                    start_date=df_country_cleaned['InvoiceDate'].min().date(),
                    end_date=df_country_cleaned['InvoiceDate'].max().date(),
                    # style={'width': '100%'}
                ),
            ]
        )


app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H2("Online Retail Dashboard"))),

        dbc.Row(
            [
                dbc.Col(
                    controls_Dropdown,
                    md=3, sm=12
                ),
                dbc.Col(
                    controls_DatePickerRange,
                    md=5, sm=12
                ),
                dbc.Col(
                    [
                        html.Br(),  # Adds vertical space to align button
                        html.Button("Update", id='update-button', n_clicks=0, className="btn btn-primary")
                    ],
                    md=2, sm=12, className="d-flex align-items-end justify-content-center"
                ),
            ],
            className="mb-4"
        ),

        dbc.Row(
            dbc.Col(dcc.Graph(id='revenue-graph'))
        ),
    ],
    fluid=True
)


# Callback
@app.callback(
    Output('revenue-graph', 'figure'),
    Input('update-button', 'n_clicks'),
    State('country-dropdown', 'value'),
    State('date-picker', 'start_date'),
    State('date-picker', 'end_date')
)
def update_graph(n_clicks, selected_country, start_date, end_date):
    filtered_df = df_country_cleaned[
        (df_country_cleaned['Country'] == selected_country) &
        (df_country_cleaned['InvoiceDate'] >= pd.to_datetime(start_date)) &
        (df_country_cleaned['InvoiceDate'] <= pd.to_datetime(end_date))
    ]

    grouped = filtered_df.groupby(filtered_df['InvoiceDate'].dt.date)['TotalPrice'].sum().reset_index()
    fig = px.line(grouped, x='InvoiceDate', y='TotalPrice',
                  title=f"Total Revenue Over Time - {selected_country}")
    return fig

if __name__ == '__main__':
    app.run(debug=True)
