import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from point_set import *

app = dash.Dash(
    __name__,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)

server = app.server

axis_template = {
    "showbackground": True,
    "backgroundcolor": "#141414",
    "gridcolor": "rgb(255, 255, 255)",
    "zerolinecolor": "rgb(255, 255, 255)",
}

plot_layout = {
    "title": "",
    "margin": {"t": 0, "b": 0, "l": 0, "r": 0},
    "font": {"size": 12, "color": "white"},
    "showlegend": False,
    "plot_bgcolor": "#141414",
    "paper_bgcolor": "#141414",
    "scene": {
        "xaxis": axis_template,
        "yaxis": axis_template,
        "zaxis": axis_template,
        "aspectratio": {"x": 1, "y": 1.2, "z": 1},
        "camera": {"eye": {"x": 1.25, "y": 1.25, "z": 1.25}},
        "annotations": [],
    },
}

data=[dict(
        x=[0],
        y=[0],
        z=[0],
        mode='markers',
        type='scatter3d',
        text=None,
        marker=dict(
            size=12,
            opacity=0.8
            )
        )
    ]
# GITHUB_LINK = os.environ.get(
#     "GITHUB_LINK",
#     "https://github.com/plotly/dash-sample-apps/tree/master/apps/dash-brain-viewer",
# )

app.layout = html.Div(
    [
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Div(
                                    [
                                        html.H4("Range Tree and Variations"),
                                    ],
                                    className="header__title",
                                ),
                                html.Div(
                                    [
                                        html.P(
                                            "Description here."
                                        )
                                    ],
                                ),
                                # html.Div(
                                #     [
                                #         html.A(
                                #             "View on GitHub",
                                #             href=GITHUB_LINK,
                                #             target="_blank",
                                #         )
                                #     ],
                                #     className="header__button",
                                # ),
                            ],
                            className="header pb-20",
                        ),
                        html.Div(
                            [
                                dcc.Graph(
                                    id='points',
                                    figure = {
                                        "data": data,
                                        "layout": plot_layout,
                                    },
                                ),
                                dcc.Interval(
                                    id ='interval-component',
                                    interval=1*1000,
                                    n_intervals=0,
                                )
                            ],

                            className="graph__container",
                        )
                    ],
                    className="container",
                )
            ],
            className="two-thirds column app__left__section",
        ),
        html.Div(
            [
                # html.Div(
                #     [
                #
                #     ],
                #     className="colorscale pb-20",
                # ),
                html.Div(
                    [
                        html.P("Select option", className="subheader"),
                        dcc.RadioItems(
                            options=[
                                {"label": "Regular Range Tree", "value": "vanilla"},
                            ],
                            id="radio-options",
                            labelClassName="label__option",
                            inputClassName="input__option",
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Generate Random Data", className="subheader"),
                        html.Br(),
                        dcc.Input(id="num_elements", type="number", placeholder="Number of Points"),
                        html.Span(" | "),
                        html.Button("Generate", id='generate', n_clicks=0),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Query", className="subheader"),
                        html.Br(),
                        html.Div(id='range'),
                        # configure these to set the correct ranges
                        dcc.RangeSlider(id="x",
                                        min=-np.sqrt(len(data[0]['x'])),
                                        max=np.sqrt(len(data[0]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[0]['x'])), np.sqrt(len(data[0]['x']))]
                                        ),
                        dcc.RangeSlider(id="y",
                                        min=-np.sqrt(len(data[0]['x'])),
                                        max=np.sqrt(len(data[0]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[0]['x'])), np.sqrt(len(data[0]['x']))]
                                        ),
                        dcc.RangeSlider(id="z",
                                        min=-np.sqrt(len(data[0]['x'])),
                                        max=np.sqrt(len(data[0]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[0]['x'])), np.sqrt(len(data[0]['x']))]
                                        ),
                    ],
                    className="pb-20",
                ),
                # html.Div(
                #     [
                #         html.Span("Remove point", className="subheader"),
                #
                #     ],
                #     className="pb-20",
                # ),
            ],
            className="one-third column app__right__section",
        ),
        dcc.Store(id="annotation_storage"),
    ]
)

@app.callback(
    dash.dependencies.Output('points', 'figure'),
    [dash.dependencies.Input('generate', 'n_clicks')],
    [dash.dependencies.State('num_elements', 'value')])
def gen_points(clicks, num_points):
    if (num_points == None): num_points = 10
    xs, ys, zs = generate_random_points(num_points, np.sqrt(num_points))
    print(clicks, num_points)
    data[0]['x'] = xs
    data[0]['y'] = ys
    data[0]['z'] = zs

    return { "data": data, "layout": plot_layout}

@app.callback(
    dash.dependencies.Output('range', 'children'),
    [dash.dependencies.Input('x', 'value'),
     dash.dependencies.Input('y', 'value'),
     dash.dependencies.Input('z', 'value')],)
def update_range(x,y,z):
    return 'Range: ' + str(x) + ', ' + str(y) + ', ' + str(z)




if __name__ == "__main__":
    app.run_server(debug=True)
