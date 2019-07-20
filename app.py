import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.graph_objs as go


df = pd.read_json('PLN_data.json')
first_currency_row = df.rates.iloc[0]

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
            options=[
                {'label': currency, 'value': currency} for currency, _ in first_currency_row.items()
            ],
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
            options=[
                {'label': currency, 'value': currency} for currency, _ in first_currency_row.items()
            ],
            value=['PLN'],
            style={
                'background': colors['background'],
                'color': colors['text']
            }
        ),
        style={'width': '48%', 'float': 'right', 'display': 'inline-block'}
    ),

    dcc.Graph(
        id='currency-graph',
    )
])


@app.callback(
    Output('currency-graph', 'figure'),
    [Input('currencies-dropdown', 'value')]
)
def update_currency_graph(currencies):
    data = []
    for currency in currencies:
        data.append(go.Scatter(
            x=list(df.index),
            y=[1/item[currency] for item in df['rates']],
            name=currency,
            mode='lines'
        ))

    return {
        'data': data,
        'layout': go.Layout(
            xaxis={'type': 'date', 'title': 'Date'},
            yaxis={'title': 'PLN'},
            showlegend=True,
            hovermode='closest',
            plot_bgcolor=colors['background'],
            paper_bgcolor=colors['background'],
            font={
                'color': colors['text']
            }
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True)
