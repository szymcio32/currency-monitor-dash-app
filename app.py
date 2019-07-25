import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go
import datetime
import requests


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
