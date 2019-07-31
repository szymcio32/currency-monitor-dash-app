import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import datetime
import requests
import dash_table


today_data = datetime.datetime.today().strftime('%Y-%m-%d')

app = dash.Dash()

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'background': colors['background']}, children=[
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
        style={'width': '48%', 'display': 'inline-block'},
    ),

    html.Div(
        dcc.Dropdown(
            id='base-currency',
            value='PLN',
            style={
                'background': colors['background'],
                'color': colors['text']
            }
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
    ),

    html.Div(id='hidden-data', style={'display': 'none'})
])


@app.callback(
    Output('hidden-data', 'children'),
    [Input('base-currency', 'value')]
)
def get_data(base_currency):
    currency_data = requests.get(f'https://api.exchangeratesapi.io/history?start_at=2019-01-01&end_at={today_data}&base={base_currency}')
    currency_df = pd.DataFrame(currency_data.json())

    return currency_df.to_json(date_format='iso', orient='split')

@app.callback(
    [Output('currency-table', 'columns'),
     Output('currency-table', 'data')],
    [Input('hidden-data', 'children'),
     Input('currencies-dropdown', 'value')]
)
def create_table(currency_df, currencies):
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
            single_row[date_column] = rate[currency]
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
    [Output('base-currency', 'options'),
     Output('currencies-dropdown', 'options')],
    [Input('hidden-data', 'children')]
)
def create_dropdown_options(currency_df):
    currency_df_json = pd.read_json(currency_df, orient='split')
    rates = currency_df_json.rates.iloc[0]
    base_currencies_options = [
        {'label': currency, 'value': currency} for currency in rates.keys()
    ]
    currencies_dropdown_options = list(base_currencies_options)

    return base_currencies_options, currencies_dropdown_options


@app.callback(
    Output('currency-graph', 'figure'),
    [Input('hidden-data', 'children'),
     Input('currencies-dropdown', 'value'),
     Input('base-currency', 'value')]
)
def update_currency_graph(currency_df, currencies, base_currency):
    currency_df_json = pd.read_json(currency_df, orient='split')
    data = []
    for currency in currencies:
        data.append(go.Scatter(
            x=list(currency_df_json.index),
            y=[1/item[currency] for item in currency_df_json['rates']],
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
