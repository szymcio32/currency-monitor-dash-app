import dash_table
import dash_core_components as dcc
import dash_html_components as html

from datetime import datetime
from datetime import timedelta

from common import COLORS
from common import BASE_CURRENCIES
from common import TODAY_DATE


layout = html.Div(className="main", children=[
    html.Div([dcc.Store(id='memory-store')]),
    html.Div([dcc.Store(id='memory-store-currencies')]),
    html.H1(
        children="Dash application for currency monitoring"
    ),

    html.Section(children=[
        html.Div(children=[
            html.Label(
                'Select base currency: ',
            ),
            dcc.Dropdown(
                id='base-currency',
                value='PLN',
                options=[{'label': currency, 'value': currency} for currency in BASE_CURRENCIES]
            ),
        ],
            className='select-data small-width'
        ),

        html.Div(children=[
            html.Label(
                'Select currencies: ',
            ),
            dcc.Dropdown(
                id='currencies-dropdown',
                value=['EUR'],
                multi=True
            ),
        ],
            className='select-data higher-width'
        ),
        html.Div(children=[
            html.Label(
                'Select start date: ',
            ),
            html.Div(
                dcc.DatePickerSingle(
                    id='start-date-picker',
                    min_date_allowed=datetime(2019, 1, 1),
                    max_date_allowed=(datetime.today() - timedelta(days=7)),
                    date=datetime(2019, 1, 1),
                    initial_visible_month=datetime(2019, 1, 1)
                ),
            ),
        ],
            className='select-data small-width'
        ),

        html.Div(children=[
            html.Label(
                'Select end date: ',
            ),
            html.Div(
                dcc.DatePickerSingle(
                    id='end-date-picker',
                    min_date_allowed=datetime(2019, 1, 5),
                    max_date_allowed=TODAY_DATE,
                    date=TODAY_DATE,
                    initial_visible_month=TODAY_DATE,
                    style={'background-color': COLORS['background'], 'color': COLORS['text']}
                ),
            ),
        ],
            className='select-data small-width'
        )
    ],
        className='main-options'
    ),

    html.Section(
        dcc.Graph(
            id='currency-graph',
        ),
        className='container'
    ),

    html.Section(children=[
        html.H2(
            id="table-header",
        ),
        dash_table.DataTable(
            id='currency-table',
            merge_duplicate_headers=True,
            style_header={
                'textAlign': 'center',
                'fontWeight': 'bold',
                'fontSize': '15px'
            },
            style_cell={
                'padding': '10px',
                'backgroundColor': COLORS['background'],
                'color': COLORS['text'],
                'border': 'none',
            },
            style_data_conditional=[
                {
                    'if': {
                        'column_id': 'currency'
                    },
                    'fontSize': '15px',
                    'color': '#CCF1FF',
                    'textAlign': 'center',
                    'padding-right': '50px'
                }
            ],
            style_header_conditional=[
                {
                    'if': {
                        'column_id': 'currency'
                    },
                    'padding-right': '50px'
                }
            ],
        ),
    ],
        className="container"
    )
])
