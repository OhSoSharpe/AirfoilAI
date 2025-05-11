import os
import json
import dash
from dash import html, dcc, Input, Output
import pandas as pd

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
])

if __name__ == "__main__":
    app.run(debug = True)