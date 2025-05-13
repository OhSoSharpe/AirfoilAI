import os
import json
import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objs as go
import numpy as np

# Folder containing the airfoil JSON files
DATA_DIR = "./generated_airfoils_json"

# Load metadata from all JSON files into a DataFrame
def load_airfoil_data():
    records = []
    for filename in os.listdir(DATA_DIR):
        if filename.endswith(".json"):
            filepath = os.path.join(DATA_DIR, filename)
            with open(filepath) as f:
                data = json.load(f)
                data["filename"] = filename.replace(".json", "")
                records.append(data)
    return pd.DataFrame(records)

df = load_airfoil_data()

# Flatten the nested Parameters dictionary into top-level columns
df = pd.concat([df.drop(columns=["Parameters"]), df["Parameters"].apply(pd.Series)], axis=1)

# Initialize Dash App
app = dash.Dash(__name__)
app.title = "Airfoil Dashboard"

# App Layout
app.layout = html.Div([
    html.H1("NACA 4-Digit Airfoil Viewer"),

    html.Div([
        html.Label("Max Camber (m)"),
        dcc.Slider(
            id = "m-slider",
            min = df["m"].min(),
            max = df["m"].max(),
            step = 0.02,
            value = df["m"].min(),
            marks = {round(val, 2): str(round(val, 2)) for val in df["m"].unique()}
        ),

        html.Label("Camber Position (p)"),
        dcc.Slider(
            id = "p-slider",
            min = df["p"].min(),
            max = df["p"].max(),
            step = 0.1,
            value = df["p"].min(),
            marks = {round(val, 2): str(round(val, 2)) for val in df["p"].unique()}
        ),

        html.Label("Thickness (t)"),
        dcc.Slider(
            id = "t-slider",
            min = df["t"].min(),
            max = df["t"].max(),
            step = 0.02,
            value = df["t"].min(),
            marks = {round(val, 2): str(round(val, 2)) for val in df["t"].unique()}
        ),    
    ],
    style = {'width': '60%', 'margin': 'auto'}),

    html.Hr(),

    html.Div(id = "airfoil-display", style = {'textAlign': 'center', 'fontSize': 24}),

    html.Div([
        dcc.Graph(
            id = 'airfoil-plot',
            style = {'height': '600px', 'marginTop': '20px'},
            config = {'scrollZoom': True},)],
    style = {'textAlign': 'center'}),

    html.Div([dcc.Checklist(
        id = 'feature-toggles',
        options = [
            {'label': 'Show Max Camber Point', 'value': 'camber'},
            {'label': 'Show Max Thickness Point', 'value': 'thickness'},
            {'label': 'Show Leading/Trailing Edge', 'value': 'edges'}
        ],
        value = ['camber', 'edges'],
        labelStyle = {'display': 'inline-block', 'marginRight': '20px'}
    )],
    style = {'textAlign': 'center', 'marginTop': '20px'})
])

# Function to find the airfoil in dataset
def find_airfoil(m, p, t):
    distances = ((df["m"] - m) ** 2 + (df["p"] - p) ** 2 + (df["t"] - t) ** 2)
    idx = distances.idxmin()
    return df.loc[idx]

@app.callback(
        [Output("airfoil-display", "children"),
         Output("airfoil-plot", "figure")],
        [Input("m-slider", "value"),
         Input("p-slider", "value"),
         Input("t-slider", "value"),
         Input("feature-toggles", "value")]
)
def update_airfoil_display(m, p, t, toggles):
    match = find_airfoil(m, p, t)
    params_str = f"Selected Airfoil: m = {match['m']}, p = {match['p']}, t = {match['t']}"
    filepath = os.path.join(DATA_DIR, f"{match['filename']}.json")

    with open(filepath) as f:
        data = json.load(f)
    
    # Get airfoil shape
    x_coords = [pt["x"] for pt in data["Airfoil_Coordinates"]]
    y_coords = [pt["y"] for pt in data["Airfoil_Coordinates"]]

    # Get camber line
    camber_x = [pt["x"] for pt in data["Camber_Line"]]
    camber_y = [pt["y"] for pt in data["Camber_Line"]]

    fig = go.Figure()

    # Airfoil surface
    fig.add_trace(go.Scatter(x = x_coords, y = y_coords, mode = "lines", name = "Airfoil", fill = "toself"))
    
    # Camber line
    fig.add_trace(go.Scatter(x = camber_x, y = camber_y, mode = "lines",  name = "Camber Line", line = dict(dash = "dash", color = "black")))
    
    # Toggle Features ( Max Camber, Max Thickness, Leading/Trailing Edges)
    if "camber" in toggles:
        max_idx = np.argmax(camber_y)
        fig.add_trace(go.Scatter(x = [camber_x[max_idx]], y = [camber_y[max_idx]], mode = "markers", name = "Max Camber", marker = dict(size = 10, color = "blue", symbol = "cross")))

    if "thickness" in toggles:
        # Convert to numpy arrays
        x_coords_np = np.array(x_coords)
        y_coords_np = np.array(y_coords)

        # Find the index where changes from upper to lower surface
        split_idx = np.argmax(x_coords_np)

        # Split y values into upper and lower surfaces
        upper_x = x_coords_np[:split_idx + 1]
        lower_x = x_coords_np[split_idx + 1:][::-1]
        upper_y = y_coords_np[:split_idx + 1]
        lower_y = y_coords_np[split_idx + 1:][::-1]

        # Interpolate lower y to match upper x
        shared_x = np.linspace(0, 1, 200)
        upper_interp = np.interp(shared_x, upper_x, upper_y)
        lower_interp = np.interp(shared_x, lower_x, lower_y)

        # Calculate thickness at each x
        thickness_vals = upper_interp - lower_interp
        max_thickness_idx = np.argmax(thickness_vals)

        # Coordinates of max thickness
        x_thick = shared_x[max_thickness_idx]
        y_upper = upper_interp[max_thickness_idx]
        y_lower = lower_interp[max_thickness_idx]

        # Vertical line from upper to lower showing max thickness
        fig.add_trace(go.Scatter(x = [x_thick, x_thick], y = [y_lower, y_upper], mode = "lines + markers", name = "Max Thickness", marker = dict(size = 8, color = "red", symbol = "diamond"), line = dict(color = "red", width = 2, dash = "dot")))

    if "edges" in toggles:
        fig.add_trace(go.Scatter(x = [x_coords[0], x_coords[-1]], y = [y_coords[0], y_coords[-1]], mode = "markers", name = "Leading/Trailing Edges", marker = dict(size = 8, color = "green", symbol = "circle")))
    
    fig.update_layout(title = "Airfoil Shape", xaxis_title = "x", yaxis_title = "y", yaxis_scaleanchor = "x", margin = dict(l = 20, r = 20, t = 40, b = 20))

    return params_str, fig

if __name__ == "__main__":
    app.run(debug = True)