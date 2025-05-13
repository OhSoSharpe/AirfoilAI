import os
import json
import dash
from dash import html, dcc, Input, Output
import pandas as pd
import plotly.graph_objs as go

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
    style = {'textAlign': 'center'})
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
         Input("t-slider", "value")]
)
def update_airfoil_display(m, p, t):
    match = find_airfoil(m, p, t)
    params_str = f"Selected Airfoil: m = {match['m']}, p = {match['p']}, t = {match['t']}"
    filepath = os.path.join(DATA_DIR, f"{match['filename']}.json")

    with open(filepath) as f:
        data = json.load(f)
    
    x_coords = [pt["x"] for pt in data["Airfoil_Coordinates"]]
    y_coords = [pt["y"] for pt in data["Airfoil_Coordinates"]]
    camber_x = [pt["x"] for pt in data["Camber_Line"]]
    camber_y = [pt["y"] for pt in data["Camber_Line"]]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x = x_coords, y = y_coords, mode = "lines", name = "Airfoil", fill = "toself"))
    fig.add_trace(go.Scatter(x = camber_x, y = camber_y, mode = "lines",  name = "Camber Line", line = dict(dash = "dash", color = "black")))
    fig.update_layout(title = "Airfoil Shape", xaxis_title = "x", yaxis_title = "y", yaxis_scaleanchor = "x", margin = dict(l = 20, r = 20, t = 40, b = 20))

    return params_str, fig

if __name__ == "__main__":
    app.run(debug = True)