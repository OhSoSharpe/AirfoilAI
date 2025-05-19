# Airfoil Generator and Interactive Dashboard

An interactive dashboard built with Python and Dash for visualizing and understanding "NACA 4-digit airfoils". The app allows you to explore how changes in airfoil parameters — maximum camber (m), camber position (p), and thickness (t) — affect the shape and characteristics of an airfoil. The dashboard relies on NACA4_Airfoil.py, which contains the airfoil point-generation logic using standard NACA 4-digit formulas.

## Purpose

This project is a personal initiative to combine my background in aerospace engineering with my ongoing journey in programming, machine learning, and AI.  It serves as a hands-on platform to deepen my understanding of how computational tools can be used to explore aerodynamic concepts — specifically, how airfoil geometry influences flight performance. The aim is to bridge theory with application by developing tools that support airfoil analysis and design.

## Goals

The goal of this project is to develop an AI-powered system that can generate optimized airfoil shapes based on specified flight performance constraints. These generated airfoils will be converted into 3D-printable STL files and used to construct and test an RC aircraft. This process will demonstrate how machine learning can be applied to real-world aerodynamic design and testing.

## Features

- Real-time interactive visualization of airfoil geometry
- Sliders to control:
    - Max camber (m)
    - Camber position (p)
    - Thickness (t)
- Optional overlays to show:
    - Max camber point
    - Max thickness line
    - Leading and trailing edges
- Responsive Plotly chart with zoom and pan

## File Structure

- 📄 [`NACA4_Airfoil.py`](NACA4_Airfoil.py)                      # Core airfoil generation logic using NACA 4-digit equation and parameters
- 📄 [`airfoil_dashboard.py`](airfoil_dashboard.py)              # Dash app for visualizing and interacting with airfoils
- 📁 [`generated_airfoil_images/`](generated_airfoil_images/)    # Folder containing images of generated airfoils from the various possible combinations of m, p, and t parameters
    - 📄 `NACA_XXXX.png`                                         # Image of airfoil shape based on m, p, t parameters
- 📁 [`generated_airfoil_json/`](generated_airfoil_json/)        # Folder containing airfoil data files in JSON format
    - 📄 `NACA_XXXX.json`                                        # JSON file containing 'x' and 'y' coordinates of the airfoil points, camber line points, and critical points of max camber, max thickness, and leading/trailing edges
- 📄 [`requirements.txt`](requirements.txt)                      # Python dependencies
- 📄 [`README.md`](README.md)                                    # Project overview

## Running the Dashboard

1. Make sure you have Python 3.10+ installed.
2. Install required packages with pip install -r requirements.txt
3. Run the dashboard: python airfoil_dashboard.py
4. Open a browser and go to http://127.0.0.1:8050 to interact with the airfoil visualizer

## Roadmap

✅ = Complete  
🚧 = In Progress  
🟡 = Planned

- ✅ Create a script using the NACA 4-digit equations to generate airfoils and save images and JSON files of them
- ✅ Create an interactive dashboard with sliders and a graph
- 🚧 Compute flight performance values (Cl, Cd, AoA, etc.)
- 🟡 Build a machine learning module to optimize airfoil design
- 🟡 Add STL export functionality for 3D printing