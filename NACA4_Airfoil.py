import numpy as np
import matplotlib.pyplot as plt

# NACA 4-Digit Airfoil Generator
def generate_naca4_airfoil(m, p, t, num_points=100):
    # Chord length (normalized between 0 and 1)
    x = np.linspace(0, 1, num_points)
    
    # Thickness distribution equation (t = max thickness as a percentage of chord)
    y_t = (5 * t) * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
    
    # Camber line equations (m = maximum camber, p = position of max camber)
    y_c = np.where(x < p,
                   (m / p**2) * (2 * p * x - x**2),  # for x < p
                   (m / ((1 - p)**2)) * ((1 - 2 * p) + 2 * p * x - x**2))  # for x >= p
    
    # Slope of the camber line (dy/dx)
    dy_c_dx = np.where(x < p,
                       (2 * m / p**2) * (p - x),  # for x < p
                       (2 * m / ((1 - p)**2)) * (p - x))  # for x >= p
    
    # Determining the angle theta (use np.arctan for element-wise computation)
    theta = np.arctan(dy_c_dx)

    # Upper and lower surface equations
    y_upper = y_c + y_t * np.cos(theta)  # Use np.cos for element-wise computation
    y_lower = y_c - y_t * np.cos(theta)  # Use np.cos for element-wise computation
    
    return x, y_c, dy_c_dx, y_t, y_upper, y_lower, theta

# Test the NACA 2412 (m=0.02, p=0.4, t=0.12) airfoil
x, y_c, dy_c_dx, y_t, y_upper, y_lower, theta = generate_naca4_airfoil(0.02, 0.4, 0.12, num_points=100)

# Defining the max and min of the airfoil to scale the graph
y_min = min(y_lower)
y_max = max(y_upper)
y_range = y_max - y_min
padding = 0.1 * y_range

# Plot the airfoil
plt.figure(figsize=(10, 5))
plt.plot(x, y_upper, label='Upper Surface', color='blue')
plt.plot(x, y_lower, label='Lower Surface', color='red')

# Chord line
chord_y = (y_upper + y_lower) / 2
plt.plot(x, chord_y, color='black', linestyle='--', linewidth=1, label='Chord Line')

# AFT data for comparison
aft_x_upper = [1.000084, 0.999106, 0.996177, 0.991307, 0.984515, 0.975825, 0.965269, 0.952888, 0.938727, 0.922841, 0.905287, 0.886134, 0.865454, 0.843325, 0.819834, 0.795069, 0.769127, 0.742109, 0.714119, 0.685266, 0.655665, 0.625431, 0.594684, 0.563545, 0.532138, 0.500588, 0.469023, 0.437567, 0.40635, 0.375297, 0.34468, 0.314678, 0.285418, 0.257025, 0.229618, 0.203313, 0.178222, 0.154449, 0.132094, 0.111248, 0.091996, 0.074415, 0.058573, 0.044532, 0.032343, 0.022051, 0.013692, 0.007292, 0.00287, 0.000439, 0]
aft_y_upper = [0.001257, 0.001461, 0.00207, 0.003077, 0.004469, 0.006231, 0.00834, 0.010778, 0.013512, 0.016514, 0.019752, 0.023192, 0.026799, 0.030537, 0.034369, 0.03826, 0.042172, 0.046069, 0.049913, 0.05367, 0.057302, 0.060775, 0.064054, 0.067103, 0.06989, 0.072381, 0.074547, 0.076358, 0.077787, 0.078768, 0.079198, 0.079063, 0.078363, 0.077102, 0.07529, 0.072947, 0.070097, 0.066771, 0.063006, 0.058842, 0.054325, 0.049504, 0.044427, 0.039144, 0.033704, 0.028152, 0.022531, 0.016878, 0.011224, 0.005592, 0]
aft_x_lower = [0.001535, 0.005015, 0.010421, 0.017725, 0.026892, 0.03788, 0.050641, 0.06512, 0.081257, 0.098987, 0.118239, 0.138937, 0.161004, 0.184354, 0.208902, 0.234556, 0.261222, 0.288802, 0.317198, 0.346303, 0.376013, 0.406269, 0.437099, 0.468187, 0.499412, 0.530653, 0.561789, 0.592698, 0.623259, 0.653352, 0.682858, 0.711661, 0.739645, 0.7667, 0.792716, 0.81759, 0.841222, 0.863515, 0.884379, 0.90373, 0.921487, 0.937579, 0.951939, 0.964507, 0.975232, 0.984069, 0.99098, 0.995938, 0.99892, 0.999916]
aft_y_lower = [-0.005395, -0.010439, -0.015126, -0.019451, -0.023408, -0.02699, -0.030193, -0.033014, -0.035451, -0.037507, -0.039185, -0.040494, -0.041445, -0.042056, -0.042346, -0.042339, -0.042063, -0.041549, -0.04083, -0.039941, -0.038917, -0.037791, -0.036513, -0.03507, -0.033493, -0.031808, -0.030043, -0.028222, -0.026368, -0.0245, -0.022636, -0.020791, -0.018979, -0.017212, -0.015499, -0.013849, -0.012271, -0.01077, -0.009356, -0.008033, -0.006809, -0.005691, -0.004685, -0.003798, -0.003035, -0.002402, -0.001904, -0.001546, -0.00133, -0.001257]

# Plot the AFT data
plt.plot(aft_x_upper, aft_y_upper, label='Upper Surface (AFT)', color='green')
plt.plot(aft_x_lower, aft_y_lower, label='Lower Surface (AFT)', color='purple')

# Set plot labels and legend

plt.title("Comparison of NACA 2412 and AFT Airfoil")
plt.xlabel("Chord (x)")
plt.ylabel("Thickness (y)")
plt.grid(True)

# Adjust aspect ratio
aspect_ratio = (y_range + 2*padding) / 1.1
plt.gca().set_aspect(aspect_ratio)
plt.legend()

# Setting the axes equal
plt.axis('equal')
# Show the plot
plt.show()