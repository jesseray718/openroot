import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Physical constants
DYNAMIC_VISCOSITY_MU = 1.81e-5  # Pa·s
AIR_DENSITY_RHO = 1.204        # kg/m³
CORE_DEPTH_L = 0.05            # Core depth in meters

# Experimental Data (Velocity m/s vs Measured Pressure Drop Pa)
v_exp = np.array([0.10, 0.20, 0.30, 0.40, 0.50, 0.60])
dP_exp = np.array([0.38, 0.89, 1.55, 2.38, 3.39, 4.58])

# Model function
def darcy_forchheimer_model(v, K, beta):
    viscous = (DYNAMIC_VISCOSITY_MU / K) * v
    inertial = beta * AIR_DENSITY_RHO * (v ** 2)
    return CORE_DEPTH_L * (viscous + inertial)

# Curve fitting
fitted_params, covariance = curve_fit(
    darcy_forchheimer_model, 
    v_exp, 
    dP_exp, 
    p0=[1e-7, 1000.0], 
    bounds=(0, [np.inf, np.inf])
)
K_fitted, beta_fitted = fitted_params

# High-resolution grid for smooth curve rendering
v_fit = np.linspace(0, 0.65, 200)
dP_fit = darcy_forchheimer_model(v_fit, K_fitted, beta_fitted)

# Calculate residuals at experimental data points
dP_pred = darcy_forchheimer_model(v_exp, K_fitted, beta_fitted)
residuals = dP_exp - dP_pred

# Plotting Setup (2 Subplots: Fit Curve + Residual Error)
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8, 7), gridspec_kw={'height_ratios': [3, 1]}, sharex=True)

# Top Plot: Experimental Points vs Fitted Curve
ax1.scatter(v_exp, dP_exp, color='red', zorder=5, label='Experimental Data (Measured)')
ax1.plot(v_fit, dP_fit, color='navy', linewidth=2, label=f'Darcy-Forchheimer Fit\n(K={K_fitted:.2e} m², β={beta_fitted:.1f} m⁻¹)')
ax1.set_ylabel('Pressure Drop ΔP (Pa)')
ax1.set_title('Aero-Disc Core Resistance Characteristic Curve')
ax1.grid(True, linestyle='--', alpha=0.6)
ax1.legend()

# Bottom Plot: Residuals (Experimental - Predicted)
ax2.axhline(0, color='black', linestyle='--', linewidth=1)
ax2.stem(v_exp, residuals, linefmt='b-', markerfmt='bo', basefmt=' ')
ax2.set_xlabel('Superficial Velocity v (m/s)')
ax2.set_ylabel('Residual (Pa)')
ax2.set_title('Model Residuals (Experimental - Predicted)')
ax2.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()

# Save the plot figure
plt.savefig('darcy_forchheimer_fit.png', dpi=300)
print("Plot successfully saved as 'darcy_forchheimer_fit.png'")
plt.show()
