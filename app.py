import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as go


df = pd.read_json('PLN_data.json')

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

    dcc.Graph(
        id='graph',
        figure={
            'data': [
                go.Scatter(
                    x=list(df.index),
                    y=[1/item['USD'] for item in df['rates']],
                    name="USD",
                    mode='lines'
                ),
                go.Scatter(
                    x=list(df.index),
                    y=[1/item['EUR'] for item in df['rates']],
                    name="EUR",
                    mode='lines'
                )
            ],
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
    )
])


if __name__ == '__main__':
    app.run_server(debug=True)
