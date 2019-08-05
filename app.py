import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
import pandas as pd
import plotly.graph_objs as go
from datetime import datetime
from datetime import timedelta
import requests
import dash_table


today_data = datetime.today().strftime('%Y-%m-%d')
base_currencies = ['CAD', 'HKD', 'ISK', 'PHP', 'DKK', 'HUF', 'CZK', 'GBP', 'RON', 'SEK', 'IDR', 'INR', 'BRL', 'RUB',
                   'HRK', 'JPY', 'THB', 'CHF', 'EUR', 'MYR', 'BGN', 'TRY', 'CNY', 'NOK', 'NZD', 'ZAR', 'USD', 'MXN',
                   'SGD', 'AUD', 'ILS', 'KRW', 'PLN']

app = dash.Dash(__name__)

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'background': colors['background']}, children=[
    html.Div([dcc.Store(id='memory-store')]),
    html.Div([dcc.Store(id='memory-store-currencies')]),
    html.H1(
        children="Hello app",
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(
        children="A web application with Dash",
        style={
            'textAlign': 'center',
            'color': colors['text']
        }
    ),

    html.Div(
        dcc.Dropdown(
            id='currencies-dropdown',
            value=['EUR'],
            multi=True,
            style={
                'background': colors['background'],
                'color': colors['text']
            }
        ),
        style={'width': '48%', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.Dropdown(
            id='base-currency',
            value='PLN',
            options=[{'label': currency, 'value': currency} for currency in base_currencies],
            style={
                'background': colors['background'],
                'color': colors['text']
            }
        ),
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.DatePickerSingle(
            id='start-date-picker',
            min_date_allowed=datetime(2019, 1, 1),
            max_date_allowed=(datetime.today()-timedelta(days=7)),
            date=datetime(2019, 1, 1),
            initial_visible_month=datetime(2019, 1, 1)
        ),
        style={'width': '48%', 'display': 'inline-block'}
    ),

    html.Div(
        dcc.DatePickerSingle(
            id='end-date-picker',
            min_date_allowed=datetime(2019, 1, 5),
            max_date_allowed=today_data,
            date=today_data,
            initial_visible_month=today_data
        ),
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
    ),

    dcc.Graph(
        id='currency-graph',
    ),

    html.Div(
        dash_table.DataTable(
            id='currency-table',
        )
    )
])


@app.callback(
    Output('memory-store', 'data'),
    [Input('base-currency', 'value')]
)
def get_data(base_currency):
    currency_data = requests.get(f'https://api.exchangeratesapi.io/history?start_at=2018-12-31&end_at={today_data}&base={base_currency}')
    currency_df = pd.DataFrame(currency_data.json())

    return currency_df.to_json(date_format='iso', orient='split')


@app.callback(
    Output('memory-store-currencies', 'data'),
    [Input('memory-store', 'data')]
)
def get_unique_currencies_list(currency_df):
    currency_df_json = pd.read_json(currency_df, orient='split')
    unique_currencies = currency_df_json.rates.iloc[0]

    return unique_currencies

@app.callback(
    Output('start-date-picker', 'max_date_allowed'),
    [Input('start-date-picker', 'date')]
)
def max_start_date(max_end_date):
    pass


@app.callback(
    [Output('currency-table', 'columns'),
     Output('currency-table', 'data')],
    [Input('memory-store', 'data'),
     Input('currencies-dropdown', 'value')]
)
def create_table(currency_df, currencies):
    if currency_df is None:
        raise PreventUpdate

    currency_df_json = pd.read_json(currency_df, orient='split')
    limit_to_five = currency_df_json[-5:]

    columns = [{'name': 'currency', 'id': 'currency'}]
    date_columns = [
        {'name': data.strftime('%d-%m-%Y'), 'id': data.strftime('%d-%m-%Y')}
        for data in limit_to_five.index]
    columns.extend(date_columns)

    rows = []
    for currency in currencies:
        single_row = {
            'currency': currency
        }
        for rate, date in zip(limit_to_five['rates'], date_columns):
            date_column = date['id']
            try:
                single_row[date_column] = 1 / rate[currency]
            except KeyError:
                single_row[date_column] = 1
        rows.append(single_row)
    # columns = [{'name': 'Date', 'id': 'date'}]
    # dynamic_columns = [{'name': currency, 'id': currency} for currency in ['USD', 'CAD']]
    # columns.extend(dynamic_columns)
    #
    # rows = []
    # for data, rate in zip(limit_to_five.index, limit_to_five['rates']):
    #     single_row = {}
    #     string_date = data.strftime('%d-%m-%Y')
    #     single_row['date'] = string_date
    #     for currency in ['CAD', 'USD']:
    #         single_row[currency] = rate[currency]
    #     rows.append(single_row)

    return columns, rows


@app.callback(
    Output('currencies-dropdown', 'options'),
    [Input('memory-store-currencies', 'data')]
)
def create_dropdown_options(unique_currencies):
    if unique_currencies is None:
        raise PreventUpdate

    currencies_dropdown_options = [
        {'label': currency, 'value': currency} for currency in unique_currencies.keys()
    ]
    return currencies_dropdown_options


@app.callback(
    Output('currency-graph', 'figure'),
    [Input('memory-store', 'data'),
     Input('memory-store-currencies', 'data'),
     Input('currencies-dropdown', 'value'),
     Input('base-currency', 'value')]
)
def update_currency_graph(currency_df, unique_currencies, currencies_from_dropdown, base_currency):
    if currency_df is None or unique_currencies is None:
        raise PreventUpdate

    currency_df_json = pd.read_json(currency_df, orient='split')
    data = []
    for currency in currencies_from_dropdown:
        data.append(go.Scatter(
            x=list(currency_df_json.index),
            y=[1/item[currency]
               if currency in unique_currencies else 1
               for item in currency_df_json['rates']
               ],
            name=currency,
            mode='lines'
        ))

    return {
        'data': data,
        'layout': go.Layout(
            xaxis={'type': 'date', 'title': 'Date'},
            yaxis={'title': base_currency},
            showlegend=True,
            hovermode='closest',
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font={
                'color': colors['text']
            },
            title=go.layout.Title(
                text=f'Average rate of {base_currency}'
            )
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
