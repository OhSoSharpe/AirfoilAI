import subprocess
import os
import json
import pandas as pd
from tqdm import tqdm

# Folder containing the airfoil JSON files
DATA_DIR = "./generated_airfoils_json"

# XFOIL program
XFOIL_EXECUTABLE = r"C:\Tools\XFOIL\xfoil.exe"

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

# Function to find the airfoil in dataset
def find_airfoil(m, p, t):
    distances = ((df["m"] - m) ** 2 + (df["p"] - p) ** 2 + (df["t"] - t) ** 2)
    idx = distances.idxmin()
    return df.loc[idx]   

def get_naca_name(m, p, t):
    m_digit = int(m * 100)
    p_digit = int(p * 10)
    t_digit = int(t * 100)
    return f"Naca_{m_digit:d}{p_digit:d}{t_digit:d}"

# Converting .json files to .dat files for XFOIL
def json_to_dat(filename, coordinates):
    with open(filename, "w") as f:
        for x, y in coordinates:
            try:
                # Skip if x or y is a header string like "x" or "y"
                x_val = float(x)
                y_val = float(y)
                f.write(f"{x_val:.6f} {y_val:.6f}\n")
            except ValueError:
                continue

# Parameters for XFOIL
reynolds = 500000
alpha_start = -5
alpha_end = 15
alpha_step = 1

# Make output directory if nonexistant
os.makedirs("airfoils_dat", exist_ok=True)
os.makedirs("xfoil_outputs", exist_ok=True)

# Loop through all airfoils
for _, row in tqdm(df.iterrows(), total=len(df), desc="Processing airfoils"):
    m, p, t = row["m"], row["p"], row["t"]
    airfoil_name = get_naca_name(m, p, t)
    airfoil_file = f"airfoils_dat/{row['filename']}.dat"
    output_file = f"xfoil_outputs/{airfoil_name}.out"

    # Load original JSON to get coordinates
    json_path = os.path.join(DATA_DIR, row["filename"] + ".json")
    
    
    try:
        with open(json_path) as f:
            json_data = json.load(f)
            coords = json_data["Airfoil_Coordinates"]
    except (FileNotFoundError, KeyError) as e:
        print(f"Skipping {row['filename']}: {e}")
        continue # Skip to next if file missing or key not found
        
    json_to_dat(airfoil_file, coords)

    xfoil_commands = f"""
LOAD {airfoil_file.replace(os.sep, '/')}
OPER
VISC {reynolds}
ITER 100
ASeq {alpha_start} {alpha_end} {alpha_step}
PWRT
{output_file}

QUIT
"""
    
    # Write command script to a temporary file
    temp_cmd_file = "xfoil_input.txt"
    with open (temp_cmd_file, "w") as f:
        f.write(xfoil_commands)

    # Run XFOIL
    try:
        with open(temp_cmd_file, "r") as input_file:
            result = subprocess.run(
                [XFOIL_EXECUTABLE],
                stdin = input_file,
                stdout = subprocess.PIPE,
                stderr = subprocess.PIPE,
                text=True,
                timeout = 30, # prevent hanging forever
                )
    except subprocess.TimeoutExpired:
        print(f"XFOIL timed out on {airfoil_name}")
        continue
    except Exception as e:
        print(f"Error running XFOIL on {airfoil_name}")
        continue

    # Checking if XFOIL ran correctly
    if result.returncode != 0:
        print(f"XFOIL error on {airfoil_name}: {result.stderror.strip()}")
    else:
        print(f"XFOIL completed for {airfoil_name}")

    # Remove temporary input file after running
    try:
        os.remove(temp_cmd_file)
    except OSError:
        pass