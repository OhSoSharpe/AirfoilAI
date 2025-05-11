import numpy as np
import matplotlib.pyplot as plt
import os
import json



class NACA4Airfoil:
    def __init__(self, m, p, t, num_points=100):
        self.m = m
        self.p = p
        self.t = t
        self.num_points = num_points
        self.x, self.y_upper, self.y_lower, self.chord = self.generate_airfoil()
        self.yc, _ = self.compute_camber_line(self.x)
        self.xc = self.x
    
    def thickness_distribution(self, x):
        t = self.t
        return 5 * t * (0.2969*np.sqrt(x) - 0.1260*x - 0.3516*x**2 + 0.2843*x**3 - 0.1015*x**4)
    
    def compute_camber_line(self, x):
        m = self.m
        p = self.p
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)

        for i, xi in enumerate(x):
            if xi < p:
                yc[i] = (m / (p**2)) * (2*p*xi - xi**2)
                dyc_dx[i] = (2*m / (p**2)) * (p -xi)
            else:
                yc[i] = (m / ((1 - p)**2)) * ((1 - 2*p) + 2*p*xi - xi**2)
                dyc_dx[i] = (2*m / ((1 - p)**2)) * (p - xi)

        theta = np.arctan(dyc_dx)
        return yc, theta

    def generate_airfoil(self):
        beta = np.linspace(0, np.pi, self.num_points)
        x = (1 - np.cos(beta)) / 2  # Cosine spacing
        yt = self.thickness_distribution(x)
        yc, theta = self.compute_camber_line(x)

        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)

        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        # Chord line
        chord_y = (yu + yl) / 2
        # Return x and both upper/lower surfaces
        return x, (xu, yu), (xl, yl), chord_y

    def save_plot(self, generated_airfoil_images):
        coords = self.export_coordinates()
        x = coords[:, 0]
        y = coords[:, 1]

        xc = self.x
        yc, _ = self.compute_camber_line(xc)

        plt.figure(figsize=(10, 5))
        plt.plot(x, y, 'b-')
        plt.plot(xc, yc, color='black', linestyle='--', linewidth=1, label='Chord Line')
        plt.fill(x, y, color='skyblue', alpha=0.4)
        plt.xlabel("x")
        plt.ylabel("y")
        plt.axis('equal')
        plt.grid(True)
        plt.legend()
        plt.title(f'NACA Airfoil m={self.m}, p={self.p}, t={self.t}')
        plt.savefig(generated_airfoil_images)
        plt.close()

    def export_coordinates(self):
        xu, yu = self.y_upper
        xl, yl = self.y_lower
        # Combine upper and lower surfaces
        x_combined = np.concatenate([xu, xl[::-1]])
        y_combined = np.concatenate([yu, yl[::-1]])
        return np.vstack((x_combined, y_combined)).T  # Return as (N, 2) array

    def save_to_json(self, generated_airfoils_json):
        data = {
            "Parameters": {
                "m": self.m,
                "p": self.p,
                "t": self.t,
                "num_points": self.num_points
            },
            "Airfoil_Coordinates": [
                {"x": float(xi), "y": float(yi)} for xi, yi in self.export_coordinates()
            ],
            "Camber_Line": [
                {"x": float(xi), "y": float(yi)} for xi, yi in zip (self.xc, self.yc)
            ]
            }

        with open(generated_airfoils_json, 'w') as f:
            json.dump(data, f, indent=4)

# Create output folder
json_folder = "generated_airfoils_json"
os.makedirs(json_folder, exist_ok=True)
img_folder = "generated_airfoil_images"
os.makedirs(img_folder, exist_ok=True)

# Defining parameter ranges
m_values = [0.0, 0.02, 0.04, 0.06, 0.08, 0.1]
p_values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6]
t_values = [0.08, 0.10, 0.12, 0.14, 0.16, 0.18]

# Loop through all possible combinations and save each airfoil
for m in m_values:
    for p in p_values:
        for t in t_values:
            airfoil = NACA4Airfoil(m=m, p=p, t=t)
            
            # Save JSON
            json_filename = f"NACA_m{m:.2f}_p{p:.2f}_t{t:.2f}.json"
            airfoil.save_to_json(os.path.join(json_folder, json_filename))

            # Save Images
            img_filename = f"NACA_m{m:.2f}_p{p:.2f}_t{t:.2f}.png"
            airfoil.save_plot(os.path.join(img_folder, img_filename))

            print(f"Saved JSON and image for m={m:.2f}, p={p:.2f}, t={t:.2f}")