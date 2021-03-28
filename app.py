import os
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from point_set import *
from range_trees.rangetree import *
import time


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

data=[
        dict(
            x=[-1, -1, 1, 1, -1, -1, 1, 1],
            y=[-1, 1, 1, -1, -1, 1, 1, -1],
            z=[-1, -1, -1, -1, 1, 1, 1, 1],
            i = [7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
            j = [3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
            k = [0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
            type='mesh3d',
            opacity=0.2,
            showscale=True,
        ),
        dict(
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
        ),
]

GITHUB_LINK = "https://github.com/6851-2021/range-trees-visualization"

tree = TreeNode.create_from_points([(0,0,0)])

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
                                            "Use the radio buttons to select which range tree variant you want to use. \n"
                                            "Hit the generate button to create randomly located points in the range: [-sqrt(num_points), sqrt(num_points)] in all axes."
                                        )
                                    ],
                                ),

                            ],
                            className="header pb-20",
                        ),
                        html.Div(id="tree-type"),
                        html.Div(
                            [

                                dcc.Graph(
                                    id='points',
                                    figure = {
                                        "data": data,
                                        "layout": plot_layout,
                                    },
                                ),
                            ],

                            className="graph__container",
                        ),
                        html.Div(
                            [
                                html.A(
                                    "View on GitHub",
                                    href=GITHUB_LINK,
                                    target="_blank",
                                )
                            ],
                            className="header__button",
                        ),
                        html.Div(id="placeholder"),
                    ],
                    className="container",
                )
            ],
            className="two-thirds column app__left__section",
        ),
        html.Div(
            [
                html.Div(
                    [
                        html.P("Select option", className="subheader"),
                        dcc.RadioItems(
                            options=[
                                {"label": "Regular Range Tree", "value": "Regular"},
                            ],
                            id="radio-options",
                            labelClassName="label__option",
                            inputClassName="input__option",
                            value='Regular',
                        ),
                    ],
                    className="pb-20",
                ),
                html.Div(
                    [
                        html.Span("Generate Random Data", className="subheader"),
                        html.Br(),
                        dcc.Input(id="num_elements", type="number", placeholder="Number of Points"),
                        html.Br(),
                        html.Br(),
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
                                        min=-np.sqrt(len(data[1]['x'])),
                                        max=np.sqrt(len(data[1]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[1]['x'])), np.sqrt(len(data[1]['x']))],
                                        allowCross=False,),
                        dcc.RangeSlider(id="y",
                                        min=-np.sqrt(len(data[1]['x'])),
                                        max=np.sqrt(len(data[1]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[1]['x'])), np.sqrt(len(data[1]['x']))],
                                        allowCross=False,),
                        dcc.RangeSlider(id="z",
                                        min=-np.sqrt(len(data[1]['x'])),
                                        max=np.sqrt(len(data[1]['x'])),
                                        step=1,
                                        value=[-np.sqrt(len(data[1]['x'])), np.sqrt(len(data[1]['x']))],
                                        allowCross=False,),
                        html.Button("Query", id='query', n_clicks=0),
                        html.Br(),
                        html.Br(),
                        html.Span("Answer", className="subheader"),
                        html.Div(id="answer", className="subheader pb-20")
                    ],
                    className="pb-20",
                ),
            ],
            className="one-third column app__right__section",
        ),
        dcc.Store(id="annotation_storage"),
    ]
)

@app.callback(
    dash.dependencies.Output('answer', 'children'),
    dash.dependencies.Input('query', 'n_clicks'),
    [dash.dependencies.State('x', 'value'),
     dash.dependencies.State('y', 'value'),
     dash.dependencies.State('z', 'value'),]
)
def query(n, x,y,z):
    start = PointIndex((x[0], y[0], z[0]))
    end = PointIndex((x[1], y[1], z[1]))
    total = 0
    start_time = time.time()
    for elem in tree.range_query(start, end):
        total += 1
    end_time = time.time()
    return str(total) +  " elements in range " + \
           str(x) + ', ' + str(y) + ', ' + str(z) + ' in time: ' + str(end_time - start_time)

@app.callback(
    dash.dependencies.Output('tree-type', 'children'),
    [dash.dependencies.Input('radio-options', 'value')]
)
def update_tree(tree_type):
    return "Currently selected: " + tree_type + " Range Tree"

@app.callback(
    dash.dependencies.Output('points', 'figure'),
    dash.dependencies.Output('x', 'min'),
    dash.dependencies.Output('y', 'min'),
    dash.dependencies.Output('z', 'min'),
    dash.dependencies.Output('x', 'max'),
    dash.dependencies.Output('y', 'max'),
    dash.dependencies.Output('z', 'max'),
    dash.dependencies.Output('range', 'children'),
    [dash.dependencies.Input('generate', 'n_clicks'),
     dash.dependencies.Input('x', 'value'),
     dash.dependencies.Input('y', 'value'),
     dash.dependencies.Input('z', 'value')],
    [dash.dependencies.State('num_elements', 'value'),
     dash.dependencies.State('x', 'min'),
     dash.dependencies.State('y', 'min'),
     dash.dependencies.State('z', 'min'),
     dash.dependencies.State('x', 'max'),
     dash.dependencies.State('y', 'max'),
     dash.dependencies.State('z', 'max')]
)
def update_points(n, x, y, z, num_points, xmin, ymin, zmin, xmax, ymax, zmax):
    global tree
    global data
    ctx = dash.callback_context
    range_string = 'Range: ' + str(x) + ', ' + str(y) + ', ' + str(z)

    if ctx.triggered:
        input_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if input_id == 'generate':
            if (num_points == None): num_points = 10
            xs, ys, zs = generate_random_points(num_points, np.sqrt(num_points))
            data[1]['x'] = xs
            data[1]['y'] = ys
            data[1]['z'] = zs

            tree = TreeNode.create_from_points(list(zip(xs, ys, zs)))

            minR = -np.floor(np.sqrt(num_points))
            maxR = np.floor(np.sqrt(num_points))

            return { "data": data, "layout": plot_layout}, minR, minR, minR, maxR, maxR, maxR, range_string
        else:
            xs = [x[0] if np.floor(i / 2) % 2 == 0 else x[1] for i in range(8)]
            ys = [y[0] if np.floor((i - 1) / 2) % 2 == 0 else y[1] for i in range(8)]
            zs = [z[0] if np.floor(i / 4) % 2 == 0 else z[1] for i in range(8)]

            data[0]['x'] = xs
            data[0]['y'] = ys
            data[0]['z'] = zs

            return {"data": data, "layout": plot_layout}, xmin, ymin, zmin, xmax, ymax, zmax, range_string



    return { "data": data, "layout": plot_layout}, xmin, ymin, zmin, xmax, ymax, zmax, range_string




if __name__ == "__main__":
    app.run_server(debug=True)
