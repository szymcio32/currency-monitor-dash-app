import pandas as pd
import plotly.graph_objs as go
import requests

from datetime import datetime
from datetime import timedelta
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate

from app import app
from common import COLORS


@app.callback(
    Output('memory-store', 'data'),
    [Input('base-currency', 'value'),
     Input('start-date-picker', 'date'),
     Input('end-date-picker', 'date')]
)
def get_data(base_currency, start_date, end_date):
    url = f'https://api.exchangeratesapi.io/history?start_at={start_date}&end_at={end_date}&base={base_currency}'
    currency_data = requests.get(url)
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
    [Output('start-date-picker', 'max_date_allowed'),
     Output('start-date-picker', 'initial_visible_month')],
    [Input('end-date-picker', 'date')]
)
def max_date_start_date_picker(max_end_date):
    dt_obj = datetime.strptime(max_end_date, '%Y-%m-%d')
    new_dt_obj = dt_obj - timedelta(days=5)

    return new_dt_obj, new_dt_obj


@app.callback(
    Output('end-date-picker', 'min_date_allowed'),
    [Input('start-date-picker', 'date')]
)
def min_date_end_date_picker(min_end_date):
    dt_obj = datetime.strptime(min_end_date, '%Y-%m-%d')
    new_dt_obj = dt_obj + timedelta(days=4)

    return new_dt_obj


@app.callback(
    Output('table-header', 'children'),
    [Input('base-currency', 'value')]
)
def create_table_header(base_currency):
    return f'Last five rates of {base_currency}'


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

    columns = [{'name': 'Currency', 'id': 'currency'}]
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
            plot_bgcolor=COLORS['background'],
            paper_bgcolor=COLORS['background'],
            font={
                'color': COLORS['text']
            },
            title=go.layout.Title(
                text=f'Average rate of {base_currency}'
            )
        )
    }
